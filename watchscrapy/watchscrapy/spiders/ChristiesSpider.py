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
from selenium.common.exceptions import NoSuchElementException


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
        self.browser.find_element(
            By.XPATH, '/html/body/div[3]/div[2]/div/div/div[2]/div/div/button[2]').click()
        time.sleep(10)

        item = WatchItem()
        lots_urls = set()
        try:
            # 1 House Name
            # item['house_name'] = 5

            # 3 Date
            date_str = self.browser.find_element(By.XPATH,
                                                 '/html/body/div[1]/chr-auction-header-next/header/div/div[2]/div[1]/div/p/strong').text
            date = re.search(r'\d{2} [A-Z]{3} \d{4}', date_str).group()

            # Parse the date
            date = datetime.strptime(
                date.strip(), '%d %b %Y').strftime('%b %d,%Y')

            # 4 Location
            location = self.browser.find_element(
                By.XPATH, '/html/body/div[1]/chr-auction-header-next/header/div/div[2]/div[2]/div/div/div/span').text
            # item['location'] = location

            # Find the parent element by XPath
            parent_element = self.browser.find_element(
                By.XPATH, '/html/body/div[1]/chr-auction-results-view/main/section/div/ul')

            # Find all div elements inside the parent
            li_elements = parent_element.find_elements(
                By.XPATH, './/li')

            # Iterate over each li element to find the 'a' tag and extract href attribute
            for li in li_elements:
                try:
                    # Find 'a' tag inside the div
                    a_tag = li.find_element(
                        By.XPATH, './/chr-lot-tile/div[2]/div[2]/h2/a')

                    # Get the href attribute value
                    href_value = a_tag.get_attribute('href')
                    lots_urls.add(href_value)

                except NoSuchElementException:
                    # If 'a' tag is not found in the li, skip it
                    continue

            lot_string = self.browser.find_element(
                By.XPATH, '/html/body/div[1]/chr-page-nav/nav/div/ul/li[2]/a').text
            # Using regular expression to extract the number
            lot_number = re.search(r'\((\d+)\)', lot_string).group(1)
            print(f'\n\n--total_lots:: {lot_number} ---\n\n')
            # 5 Lot
            time.sleep(5)
            print(f'\n\n--source_url:: {url}')
            for url in lots_urls:
                yield scrapy.Request("https://www.google.com", dont_filter=True, callback=self.parseBS, meta={'url': url, 'browser': self.browser, 'date': date, 'location': location, 'lots': lot_number, 'source_url': response.url, })
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())

    def parseBS(self, response):
        url = response.meta.get('url')
        browser = response.meta.get('browser')
        source_url = response.meta.get('url')
        print(f'\n\n--source_url in parseBS:: {source_url}')
        logging.warn(
            "ChristiesSpider; msg=Crawling going to start;url= %s", url)
        item = WatchItem()

        try:
            browser.get(url)
            time.sleep(10)

            item['house_name'] = 5
            lot_text = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[1]/div[1]/div/chr-item-pagination/span').text
            lot_number = re.search(r'\d+', lot_text).group()
            item['lot'] = lot_number
            print(f'\n\n--lot_number:: {lot_number} ---\n\n')

            # 2 Auction Name
            name = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[1]/div[1]/chr-breadcrumb/nav/ol/li/a/div/span[2]').text
            item['name'] = name

            # 3 Date
            item['date'] = response.meta.get('date')
            item['location'] = response.meta.get('location')

            # 6 Images
            images_links = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[2]/div/chr-lot-header-gallery-button/div/div/chr-image/div/img')

            image = images_links.get_attribute('src')

            # Split the string by "?"
            image_parts = image.split("?")

            # Take the first part which contains the URL without parameters
            clean_image_url = image_parts[0]
            print(f'\n-- clean_image:: {clean_image_url} --\n')
            item['images'] = clean_image_url

            # 7 Title
            title = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[1]/span').text
            item['title'] = title.strip()

            # 8 Description
            description = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div[3]/div[2]/div[2]/div[1]/div[1]/div[1]/div/chr-lot-details/section/div/chr-accordion/div/chr-accordion-item/div/fieldset/div').text
            item['description'] = description

            time.sleep(5)
            try:
                estimation = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[2]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[2]/div[2]/span').text
            except:
                estimation = None
            if estimation is not None:
                # Split the estimation string by spaces
                parts = estimation.split()

                # Extract the lot currency
                lot_currency = parts[0]

                # Extract the minimum and maximum prices
                est_min_price = parts[1]
                est_max_price = parts[3]

            else:
                lot_currency = None
                est_min_price = None
                est_max_price = None

            # 9 Lot Currency
            item['lot_currency'] = lot_currency.strip()
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

            item['sold_price'] = sold_price_value

            # 13 Sold Price Dollar
            item['sold_price_dollar'] = 0
            item["sold"] = 1

            # 14  URL
            item['url'] = source_url
            item["status"] = "Success"

        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())

        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = source_url
        item["job"] = self.job
        yield item
