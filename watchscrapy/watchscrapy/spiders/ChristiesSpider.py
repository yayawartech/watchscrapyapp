import re
import json
import time
import scrapy
import logging
import requests
import traceback
from datetime import datetime
from selenium import webdriver
from watchscrapy.items import WatchItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


class ChristiesSpider(scrapy.Spider):
    name = "christiesSpider"
    allowed_domains = ["onlineonly.christies.com"]

    def __init__(self, url='', job='', *args, **kwargs):
        super(ChristiesSpider, self).__init__(*args, **kwargs)
        # self.start_urls = [
        # 'https://onlineonly.christies.com/s/watches-online-top-time/lots/3229']
        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('headless')
        browser = webdriver.Chrome(options=options)
        return browser

    def start_requests(self):
        self.browser = self.sel_configuration()
        time.sleep(5)

        for url in self.start_urls:
            url += "&loadall=true&page=2&sortby=LotNumber" if '?' in url else "?loadall=true&page=2&sortby=LotNumber"
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        url = response.url
        time.sleep(5)
        self.browser.get(response.url)
        time.sleep(5)
        # Accept Cookie popup
        try:
            accept_cookie = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[3]/div[2]/div/div/div[2]/div/div/button[2]'))
            )
            accept_cookie.click()
            time.sleep(5)
        except NoSuchElementException:
            logging.warn("\n---- No cookie ----\n")
        item = WatchItem()
        lots_urls = set()
        try:
            # 1 House Name

            # 2 Auction Name
            name = self.browser.find_element(
                By.XPATH, '/html/body/div[1]/chr-auction-header-next/header/div/div[2]/div[1]/h1').text

            # 3 Date
            date = self.browser.find_element(By.XPATH,
                                             '/html/body/div[1]/chr-auction-header-next/header/div/div[2]/div[1]/div/p/strong').text
            date_string = re.search(r'\d{2} [A-Z]{3} \d{4}', date).group()

            # Convert the date string to a datetime object
            date_obj = datetime.strptime(date_string, '%d %b %Y')

            # Format the datetime object
            formatted_date = date_obj.strftime('%b %d,%Y')

            # 4 Location
            location = self.browser.find_element(
                By.XPATH, '/html/body/div[1]/chr-auction-header-next/header/div/div[2]/div[2]/div/div/div/span').text

            # 5 Lot
            # Find the parent element by XPath
            parent_element = self.browser.find_element(
                By.XPATH, '/html/body/div[1]/chr-auction-results-view/main/section/div/ul')

            # Find all div elements inside the parent
            li_elements = parent_element.find_elements(
                By.XPATH, './/li')

            # Iterate over each div element to find the 'a' tag and extract href attribute
            for li in li_elements:
                try:
                    # Find 'a' tag inside the div
                    a_tag = li.find_element(
                        By.XPATH, './/chr-lot-tile/div[2]/div[2]/h2/a')

                    # Get the href attribute value
                    href_value = a_tag.get_attribute('href')
                    lots_urls.add(href_value)

                except NoSuchElementException:
                    # If 'a' tag is not found in the div, skip it
                    continue

            lot_string = self.browser.find_element(
                By.XPATH, '/html/body/div[1]/chr-page-nav/nav/div/ul/li[2]/a').text
            # Using regular expression to extract the number
            lot_number = re.search(r'\((\d+)\)', lot_string).group(1)

            lot = int(lot_number)
            time.sleep(5)

            for url in lots_urls:
                yield scrapy.Request("https://www.google.com", dont_filter=True, callback=self.parseBS, meta={'url': url, 'browser': self.browser, 'date': formatted_date, 'name': name, 'location': location, 'lots': lot})
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())

    def parseBS(self, response):
        url = response.meta.get('url')

        logging.warn(
            "SothebysSpider; msg=Crawling going to start;url= %s", url)
        item = WatchItem()
        item['name'] = response.meta.get('name')
        item['house_name'] = 5
        item['date'] = response.meta.get('date')
        item['location'] = response.meta.get('location')
        item['lot'] = response.meta.get('lots')
        try:
            self.browser.get(url)
            time.sleep(5)

            # 6 Images
            images = []

            active_image = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[2]/div/chr-lot-header-gallery-button/div/div/chr-image/div/img')
            img1 = active_image.get_attribute("src")
            index = img1.find('?')
            modified_url = img1[:index] if index != -1 else img1
            images.append(modified_url)

            parent_element = self.browser.find_elements(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[1]/div')

            for div in parent_element:
                chr_lot = div.find_element(
                    By.XPATH, './/chr-lot-header-gallery-button')
                div_1 = chr_lot.find_element(By.XPATH, './/div')
                div_2 = div_1.find_element(By.XPATH, './/div')
                chr_image = div_2.find_element(By.XPATH, './/chr-image')
                div_3 = chr_image.find_element(By.XPATH, './/div')
                img = div_3.find_element(By.XPATH, './/img')
                image_url = img.get_attribute("src")
                index = image_url.find('?')
                # Remove everything after the '?' character
                modified_url = image_url[:index] if index != -1 else image_url
                images.append(modified_url)

            item['images'] = images

            # 7 Title
            title = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[1]/div/span').text or None
            if title is None:
                title = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[1]/span').text

            item['title'] = title

            # 8 Description
            description = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[2]/div[2]/div[1]/div[1]/div[1]/div/chr-lot-details/section/div/chr-accordion/div/chr-accordion-item/div/fieldset/div').text
            item['description'] = description

            estimation = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[2]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[2]/div[2]/span').text
            if estimation:

                # Split the estimation string by spaces
                parts = estimation.split()

                # Extract the lot currency
                lot_currency = parts[0]

                # Extract the minimum and maximum prices
                est_min_price = parts[1]
                est_max_price = parts[4]

            else:
                lot_currency = None
                est_min_price = None
                est_max_price = None

            # 9 Lot Currency
            item['lot_currency'] = lot_currency
            # 10 Est Min Price
            item['est_min_price'] = est_min_price
            # 11 Est Max Price
            item['est_max_price'] = est_max_price

            # 12 Sold Price
            sold_price = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[2]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[1]/span[2]').text

            # Split the sold_price string by spaces
            parts = sold_price.split()

            # Extract the sold price
            sold_price_value = parts[1]
            sold_price_without_comma = sold_price_value.replace(',', '')
            item['sold_price'] = sold_price_without_comma

            # 13 Sold Price Dollar
            item['sold_price_dollar'] = None
            if sold_price_value:
                item["sold"] = 1
            else:
                item['sold'] = 0

            # 14  URL
            item['url'] = url
            item["status"] = "Success"

        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())

        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = url
        item["job"] = self.job
        yield item
