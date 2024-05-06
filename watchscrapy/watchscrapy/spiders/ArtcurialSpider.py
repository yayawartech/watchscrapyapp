# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import traceback
import requests
import json
import time
from watchscrapy.items import WatchItem
from scrapy.http import HtmlResponse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class ArtcurialSpider(scrapy.Spider):
    name = "artcurialSpider"
    allowed_domains = ["www.artcurial.com"]
    start_urls = [
        'https://www.artcurial.com/en/sales/vente-fr-3484-modern-vintage-watches-online']

    def __init__(self, url='', job='', *args, **kwargs):
        super(ArtcurialSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        # setup = Setup.objects.first()
        # SELENIUM_CHROMEDRIVER_PATH = setup.chromedriver
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('headless')
        browser = webdriver.Chrome(options=options)
        browser.set_window_size(1440, 900)
        return browser

    def start_requests(self):
        # Provide a complete URL with the scheme (e.g., "http://" or "https://")
        start_urls = [
            'https://www.artcurial.com/en/sales/vente-fr-3484-modern-vintage-watches-online']
        browser = self.sel_configuration()
        logged_in = self.login(browser)
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'browser': browser})


    def parse(self, response):
        logging.warn(
            "ArtcurialSpider; msg=Spider started;url= %s", response.url)
        try:
            name = response.xpath(
                '//*[@id="app"]/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/h3/text()').extract()
            # 3
            date = response.xpath(
                '//*[@id="app"]/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/div[2]/div/a/span/text()').extract()
            # 4
            location = "Online"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/json',
                "X-Algolia-Api-Key": "3349c930e83dcf3e4de1de65bc7af214",
                "X-Algolia-Application-Id": "R0QMYZZKST"

            }
            body = {
                "query": "", "filters": "saleObjectId:vente-fr-3484-modern-vintage-watches-online", "hitsPerPage": 200, "numericFilters": ""
            }
            url = "https://r0qmyzzkst-dsn.algolia.net/1/indexes/items/query?x-algolia-agent=Algolia%20for%20JavaScript%20(4.15.0)%3B%20Browser"
            resp = requests.post(url, headers=headers, json=body)
            
            # resp = requests.get(new_url)
            respj = json.loads(resp.text)            

            auction_url = response.url
            print(f"\nrespnose_url:: {response.url}\n\n")

            # Scrape another page using Selenium
            browser = response.meta.get('browser')
            z = browser.get(response.url)
            print(f'\n\n ----------- z:: {z} \n\n\n\n\n--------')
            time.sleep(10)
            all_lots = browser.find_elements(By.XPATH, '//*[@id="app"]/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[2]/td[1]/h5/text()')
            print(f"\n\n-- all_lots:: {all_lots}\n\n")

            total_lots = len(all_lots)
            logging.warn("ArtcurialSpider; msg=Total Lots: %s;url= %s", len(
                all_lots), response.url)
            for lots in all_lots:
                url_segment = lots.xpath(
                    'div[@class="mosaic__item-img"]/a/@href').extract()[0]
                url = "https://" + self.allowed_domains[0] + url_segment
                lot_number = lots.xpath(
                    'div[@class="mosaic__item-infos"]/div[1]/p/a/span/text()').extract()[0]
                items = {'name': name, 'date': date, 'location': location,
                         'lot_number': lot_number, 'auction_url': auction_url, 'lots': total_lots}
                yield scrapy.Request(url, callback=self.parse_url, meta=items)
        except Exception as e:
            item = WatchItem()
            item['url'] = response.url
            item['status'] = "Failed"
            logging.error(
                "ArtcurialSpider; msg=Crawling Failed > %s;url= %s", str(e), auction_url)
            logging.error("ArtcurialSpider; msg=Crawling Failed;url= %s;Error=%s",
                          auction_url, traceback.format_exc())
            yield item

    def parse_url(self, response):
        item = WatchItem()
        try:
            # 1 HouseName
            house_name = 2
            item["house_name"] = house_name

            # 2 Name
            name = response.meta.get("name")
            item["name"] = name

            # 3 Date
            date = response.meta.get("date")
            item["date"] = datetime.strptime(
                date.strip(), '%d %B %Y').strftime('%b %d,%Y')

            # 4 Location
            location = response.meta.get("location")
            item["location"] = location

            # 5 Lot Number
            lot_number = response.meta.get("lot_number")
            item["lot"] = re.findall(r'\d+', lot_number)[0]

            product_visuals = response.xpath('//div[@class="product-visuals"]')

            # 6 Images
            images_info = product_visuals.xpath(
                'div[1]/ul/li/img/@src').extract()

            images = "https://" + \
                self.allowed_domains[0] + "/" + images_info[0]

            item["images"] = images

            strong_info = product_visuals.xpath(
                'div[@class="product-visuals__description description-tablet-landscape-up"]/strong/text()').extract()
            if not strong_info:
                strong_info = product_visuals.xpath(
                    'div[@class="product-visuals__description description-tablet-landscape-up"]/p/strong/text()').extract()

            # 7 title
            if len(strong_info) > 1 and "Estimation" not in strong_info[1]:
                title = strong_info[0] + " " + strong_info[1]
            else:
                title = strong_info[0]
            item["title"] = title

            # 8 Description
            description = product_visuals.xpath(
                'div[@class="product-visuals__description description-tablet-landscape-up"]').extract()[0]
            item["description"] = description

            estimation_info = strong_info[-1].strip().replace(
                "Estimation", "").strip().split("-")
            sold_pre_info = product_visuals.xpath(
                'div[@class="product-visuals__description description-tablet-landscape-up"]/span/text()').extract()

            if len(strong_info) > 1 and "Estimation" not in strong_info[-1]:
                est_min_price = est_max_price = 0
                lot_currency = sold_pre_info[0].split()[-1]
            else:
                est_min_price = estimation_info[0].strip().split(
                    " ")[-1].replace(",", "")
                est_max_price = estimation_info[1].strip().split(" ")[
                    0].replace(",", "")
                lot_currency = estimation_info[1].strip().split(" ")[-1]

            # 9 Lot Currency
            item["lot_currency"] = lot_currency
            # 10 Est min Price
            item["est_min_price"] = est_min_price

            # 11 Est max Price
            item["est_max_price"] = est_max_price

            # 12 sold
            sold = sold_price = 0
            if sold_pre_info:
                sold_info = sold_pre_info[0].split(" ")
                if sold_info[0] == "Sold":
                    sold = 1
                    sold_price = sold_info[1].replace(",", "")

            item["sold"] = sold
            # 13 sold_price
            item["sold_price"] = sold_price

            # 14 sold_price_dollar
            item["sold_price_dollar"] = 0

            # 15 url
            item["url"] = response.url
            item["status"] = "Success"
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ArtcurialSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.error("ArtcurialSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = response.meta.get("auction_url")
        item["job"] = self.job
        yield item

    def login(self, browser):
        login_url = 'https://www.artcurial.com/en/log-in'
        time.sleep(2)
        try:
            browser.get(login_url)
            time.sleep(3)

            username = browser.find_element(By.XPATH, '//*[@id="input-139"]')
            username.send_keys('manjul@gmail.com')
            password = browser.find_element(By.XPATH, '//*[@id="input-143"]')
            password.send_keys('Artcurial@123')

            time.sleep(5)
            # login button
            browser.find_element(
                By.XPATH, '//*[@id="app"]/div/main/div/div[1]/div/div/div[2]/span/form/div[3]/div/button').click()
            time.sleep(5)
            print(f"\n\n----- login successful -----\n\n\n")
        except Exception as e:
            logging.error(
                "HeritageSpider; msg=Login Failed > %s;url= %s", str(e), login_url)
            logging.error(
                "HeritageSpider; msg=Login Failed;url= %s;Error=%s", login_url, traceback.format_exc())

        return True
