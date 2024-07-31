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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class ArtcurialSpider(scrapy.Spider):
    name = "artcurialSpider"
    allowed_domains = ["www.artcurial.com"]
    # start_urls = [
    #     'https://www.artcurial.com/en/sales/vente-fr-3484-modern-vintage-watches-online']

    def __init__(self, url='', job='', *args, **kwargs):
        super(ArtcurialSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('headless')
        service = Service('/usr/local/bin/chromedriver')
        browser = webdriver.Chrome(service=service, options=options)
        browser.set_window_size(1440, 900)
        return browser

    def start_requests(self):
        self.browser = self.sel_configuration()
        self.login(self.browser)
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"browser": self.browser})

    def parse(self, response):
        logging.warn(
            "ArtcurialSpider; msg=Spider started;url= %s", response.url)
        try:
            self.browser.get(response.url)
            time.sleep(15)
            name = self.browser.find_element(By.XPATH,
                                             '//*[@id="app"]/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[1]/div/div/div/h3').text
            # 3
            date_string = self.browser.find_element(By.XPATH,
                                                    '//*[@id="app"]/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/div[2]/div/a/span').text
            full_date_and_time = date_string.split(" at ")
            full_date = full_date_and_time[0]

            partial_date = datetime.strptime(full_date, '%B %d, %Y')
            date = partial_date.strftime('%b %d,%Y')

            # 4
            location = "Online"
            auction_url = response.url
            # Scrape another page using Selenium
            browser = response.meta.get('browser')
            try:
                browser.get(response.url)
                
            except Exception as e:
                logging.warn(f'Failed to load page: {e}')

            time.sleep(20)

            all_lots_elements = browser.find_elements(
                By.XPATH, '//*[@id="app"]/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[2]/td[1]/h5')

            # Extracting text content from each element in the list
            all_lots = [element.text for element in all_lots_elements]
            all_lots = int(all_lots[0].split()[0])            

            total_lots = all_lots
            # =====================================
            logging.warn("ArtcurialSpider; msg=Total Lots: %s;url= %s",
                         all_lots, response.url)
            for index in range(all_lots):
                url = response.url + "/lots/"+str(index+1)
                lot_number = index+1
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
            item['date'] = date
            # item["date"] = datetime.strptime(
            # date.strip(), '%d %B %Y').strftime('%b %d,%Y')

            # 4 Location
            location = response.meta.get("location")
            item["location"] = location

            # 5 Lot Number
            lot_number = response.meta.get("lot_number")

            item["lot"] = re.findall(r'\d+', str(lot_number))[0]

            self.browser.get(response.url)
            time.sleep(10)
            try:
                parent_element = self.browser.find_element(
                By.XPATH, '/html/body/div/div/div/div/main/div/section/div[1]/div[2]/div[1]/section/section/div/ul')
                child_elements = parent_element.find_elements(By.XPATH, './/li')
                images = []

                url_pattern = r'url\("([^"]+)"\)'

                for li in child_elements:
                    try:
                        div_1 = li.find_element(By.XPATH, './/div')
                        div_list = div_1.find_elements(By.XPATH, './/div')

                        for i in div_list:                        
                            try:
                                image_url_style = i.get_attribute('style')

                                match = re.search(url_pattern, image_url_style)
                                if match:
                                    url = match.group(1)
                                    img_url = url.split("?")
                                    
                                    images.append(img_url[0])

                            except NoSuchElementException:
                                continue
                    except NoSuchElementException:
                        continue

                item["images"] = images
            except NoSuchElementException:
                logging.error("Parent element not found")

            title = self.browser.find_elements(
                By.XPATH, '/html/body/div/div/div/div/main/div/section/div[1]/div[2]/div[3]/div/div[1]/div/div[2]/div[1]/div/h4')

            title = [element.text for element in title]
            item["title"] = "".join(title)

            # 8 Description
            description = self.browser.find_elements(
                By.XPATH, '//*[@id="app"]/div/main/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div')
            description = [element.text for element in description]
            description = " ".join(description)

            # Remove all single quotes
            text_without_single_quotes = description.replace("'", "")

            # Remove all double quotes
            text_without_quotes = text_without_single_quotes.replace('"', '')
            item["description"] = text_without_quotes

            estimation_info = self.browser.find_elements(
                By.XPATH, '//*[@id="app"]/div/main/div/section/div[1]/div[2]/div[3]/div/div[1]/div/div[2]/div[2]/span')
            estimation_info = [element.text for element in estimation_info]
            # 9 Lot Currency
            # item["lot_currency"] = "€"
            # 10 Est min Price
            # Assuming the currency symbols are €, $, or £
            pattern = r'Estimation : (\d{1,3}(?:\s\d{3})*)\s*€\s*-\s*(\d{1,3}(?:\s\d{3})*)\s*€'

            # Initialize variables to store extracted information
            est_min_price = None
            est_max_price = None
            lot_currency = None

            # Extracting information from each estimation info
            for info in estimation_info:
                match = re.search(pattern, info)
                if match:
                    # Extract estimated min and max prices and the currency
                    est_min_price = match.group(1).replace(' ', '')
                    est_max_price = match.group(2).replace(' ', '')
                    # lot_currency = match.group(3)
            # Printing the extracted information
            print("Estimated Min Price:", est_min_price)
            print("Estimated Max Price:", est_max_price)

            item["est_min_price"] = est_min_price

            # 11 Est max Price
            item["est_max_price"] = est_max_price

            item["lot_currency"] = '€'
            # 12 sold
            sold_price = 0
            try:
                sold_price = self.browser.find_element(
                    By.XPATH, '/html/body/div/div/div/div/main/div/section/div[1]/div[2]/div[3]/div/div[1]/div/div[3]/div[1]/div/div/div').text
                price = int(re.sub(r'\D', '', sold_price[0]))
                item['sold_price'] = price
                item['sold'] = 1
            except:
                item["sold"] = 0
                item["sold_price"] = 0

            # 14 sold_price_dollar
            item["sold_price_dollar"] = None

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
            logging.info("\n----- login successful -----\n")
        except Exception as e:
            logging.error(
                "HeritageSpider; msg=Login Failed > %s;url= %s", str(e), login_url)
            logging.error(
                "HeritageSpider; msg=Login Failed;url= %s;Error=%s", login_url, traceback.format_exc())

        return True
