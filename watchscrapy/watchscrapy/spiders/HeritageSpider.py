# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import FormRequest
import re
import json
import pprint
import logging
import traceback
from datetime import datetime


# additions
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
from watchscrapy.items import WatchItem
from watchapp.models import Setup

from scrapy import signals


class HeritageSpider(scrapy.Spider):
    name = "heritageSpider"
    allowed_domains = ["jewelry.ha.com"]

    def __init__(self, url='', job='', *args, **kwargs):
        super(HeritageSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        setup = Setup.objects.first()
        SELENIUM_CHROMEDRIVER_PATH = setup.chromedriver
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('headless')
        browser = webdriver.Chrome(
            executable_path=SELENIUM_CHROMEDRIVER_PATH, chrome_options=options)
        browser.set_window_size(1440, 900)
        return browser

    def start_requests(self):

        # browser = self.sel_configuration()
        logged_in = self.login(self.browser)
        for source_url in self.start_urls:
            try:
                logging.warn(
                    "HeritageSpider; msg=Spider started;url= %s", source_url)
                lots_urls = []
                self.browser.get(source_url)
                while True:
                    links = self.browser.find_elements_by_class_name(
                        'item-title')
                    for link in links:
                        link_url = link.get_attribute('href')
                        if link_url is not None:
                            lots_urls.append(link_url)
                    try:
                        elem_check = self.browser.find_element_by_class_name(
                            'icon-right-triangle')
                        elem_check.click()
                        time.sleep(2)
                    except NoSuchElementException:
                        break
                total_lots = len(lots_urls)
                date = self.browser.find_element_by_class_name(
                    'lotno').text.split("|")[-1].strip()
                logging.warn(
                    "HeritageSpider; msg=Total Lots: %s;url= %s", total_lots, source_url)
                for i in range(total_lots):
                    url = lots_urls[i]

                    yield scrapy.Request("https://www.test.com/"+str(i), callback=self.parseBS, meta={'date': date, 'url': url, 'browser': self.browser, 'source_url': source_url, 'lots': total_lots})
            except Exception as e:
                item = WatchItem()
                item['status'] = "Failed"
                item['job'] = self.job
                logging.error(
                    "HeritageSpider; msg=Crawling Failed > %s;url=%s", str(e), source_url)
                logging.error("HeritageSpider; msg=Crawling Failed;url=%sError=%s",
                              traceback.format_exc(), source_url)
                yield item

    def parseBS(self, response):
        url = response.meta.get('url')
        browser = response.meta.get('browser')
        source_url = response.meta.get('source_url')

        item = WatchItem()
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = source_url
        item["job"] = self.job
        item['url'] = url
        try:
            browser.get(url)
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            lot = soup.find('div', {'class': 'item-carousel'}
                            ).find_all('div')[0].find_all('small')[0].find_all('span')
            if not lot:
                item['status'] = "Failed"
                return item
            # 1 House Name
            item['house_name'] = 7

            # 2 Auction Name
            # item['name'] = self.clean_text(soup.find('div', {'class': 'breadcrumbs'}).find('li', {'class': 'active'}).text) or None
            try:
                item['name'] = soup.find(
                    'div',  {'class': 'item-carousel'}).find_all('h1', {'itemprop': 'name'})[0].text
            except:
                item['name'] = None

            # 3 Date
            date = response.meta.get('date')
            item['date'] = datetime.strptime(
                date.strip(), '%b %d, %Y').strftime('%b %d,%Y')

            # 4 Location
            item['location'] = 'Online'  # Not Available in Product Page #

            # 5 Lot
            item['lot'] = re.findall(r'\d+', lot[0].text)[0]

            # 6 Images
            images_links = []
            images_info = soup.find('div', {'class': 'gallery-view-nav'})
            if images_info:
                images = images_info.find_all('img')
                for image in images:
                    images_links.append(image['data-src'])
            else:
                images_links.append(
                    soup.find('img', {'class': 'ls-is-cached lazyloaded'})["src"])

            item['images'] = images_links

            # 7 Title
            item['title'] = self.clean_text(
                soup.find('h1', {'itemprop': 'name'}).text)

            # 8 Description
            item['description'] = self.clean_text(
                soup.find('span', {'itemprop': 'description'}).text)

            item_info = soup.find(
                'div', {'class': 'item-info'}).find_all('strong', {'class': 'headline'})[0].text
            price_data = self.clean_text(soup.find('span', {'class': 'price-data'}).text.replace(
                'JavaScript Must Be Enabled To View Pricing Data', '').replace('includes Buyer\'s Premium (BP)\xa0', ''))

            sold_price_info = price_data.split(".")[0].replace(",", "")

            # 9 Lot Currency
            item['lot_currency'] = sold_price_info.replace(
                re.findall(r'\d+', sold_price_info)[0], "")

            # 10 Est Min Price
            item['est_min_price'] = 0

            # 11 Est Max Price
            item['est_max_price'] = 0

            # 12 Sold Price
            item['sold_price'] = re.findall(r'\d+', sold_price_info)[0]
            item['sold'] = 1
            # 13 Sold Price Dollar
            item['sold_price_dollar'] = 0

            item["status"] = "Success"
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "HeritageSpider; msg=Crawling Failed > %s;url= %s", str(e), url)
            logging.error(
                "HeritageSpider; msg=Crawling Failed;url= %s;Error=%s", url, traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = source_url
        item["job"] = self.job
        return item

    def login(self, browser):
        login_url = 'https://www.ha.com/c/login.zx?source=nav'
        time.sleep(2)
        try:
            browser.get(login_url)
            browser.find_element_by_id('username').send_keys('pice_adinet')
            browser.find_element_by_id('password').send_keys('L1nd0d14')
            time.sleep(2)
            browser.find_element_by_id('loginButton').click()
        except Exception as e:
            logging.error(
                "HeritageSpider; msg=Login Failed > %s;url= %s", str(e), login_url)
            logging.error(
                "HeritageSpider; msg=Login Failed;url= %s;Error=%s", login_url, traceback.format_exc())
        return True

    def clean_text(self, text):
        return text.replace('\n', ' ').replace('\t', ' ').strip()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(HeritageSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened,
                                signal=signals.spider_opened)
        return spider

    def spider_opened(self, spider):
        logging.warning("Setting up resources.")
        self.browser = self.sel_configuration()

    def spider_closed(self, spider):
        logging.warning("Cleaning up resources.")
        self.browser.close()
