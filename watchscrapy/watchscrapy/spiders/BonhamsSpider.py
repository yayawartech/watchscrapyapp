import math
import time
import json
import scrapy
import logging
import requests
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from WatchInfo.settings import DEBUG
from scrapy.http import HtmlResponse
from watchscrapy.items import WatchItem
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException


class BonhamsSpider(scrapy.Spider):
    name = "bonhamsSpider"
    allowed_domains = ["www.bonhams.com"]

    def __init__(self, url='', job='', *args, **kwargs):
        super(BonhamsSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        if not DEBUG:
            options.add_argument('headless')
            options.add_argument('headless')
            service = Service('/usr/local/bin/chromedriver')
            browser = webdriver.Chrome(service=service, options=options)
        else:
            browser = webdriver.Chrome(options=options)
        browser.set_window_size(1440, 900)
        return browser

    def start_requests(self):
        self.browser = self.sel_configuration()
        # start_urls = [
        #     'https://www.bonhams.com/auction/28690/hong-kong-watches/']
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        item = WatchItem()
        logging.warn("BonhamsSpider; msg=Spider started;url= %s", response.url)
        try:
            # 1 HouseName
            house_name = 3
            item["house_name"] = house_name
            # 2 Name
            name = response.xpath(
                '//*[@id="skip-to-content"]/section[1]/div/div/div[1]/h1/div/text()').extract()
            item["name"] = " ".join(name)

            # 3 Date
            date_info = response.xpath(
                '//*[@id="skip-to-content"]/section[1]/div/div/div[1]/div[2]/div[1]/text()').extract()[0]

            item["date"] = datetime.strptime(
                date_info.strip(), '%d %B %Y').strftime('%b %d,%Y')

            # 4 Location
            location = response.xpath(
                '//*[@id="skip-to-content"]/section[1]/div/div/div[1]/div[3]/div[2]/span/a/text()').extract()

            item["location"] = " ".join(location)

            # Split the URL by '/'
            parts = response.url.split('/')

            # The auction ID is the third element after splitting by '/'
            auc_id = parts[4]

            item["auction_url"] = response.url

            base_url = "https://www.bonhams.com/api/v1/lots/"+auc_id
            resp = requests.get(base_url).text
            jresp = json.loads(resp)
            total_lot = jresp["total_lots"]

            page_numbers = int(math.ceil(total_lot/10))
            for i in range(page_numbers):
                final_url = base_url + "?page=" + str(i+1)
                resp = requests.get(final_url).text
                time.sleep(4)
                jresp = json.loads(resp)

                lots = jresp["lots"]
                for lot in lots:
                    # 5 Lot
                    lot_number = lot['iSaleLotNo']
                    item["lot"] = lot_number

                    # 6 Images

                    url_for_image = "https://" + \
                        self.allowed_domains[0]+lot['url']

                    # 7 title
                    title = lot['image']['alt']
                    item["title"] = title

                    # 9 Lot Currency
                    lot_currency = lot['main_currency']
                    item["lot_currency"] = lot_currency.strip()

                    # 10 Est min Price
                    # 11 Est max Price

                    try:
                        est_min_price = lot['high_low_estimates']['prices'][0]['low'].replace(
                            ",", "")
                        est_max_price = lot['high_low_estimates']['prices'][0]['high'].replace(
                            ",", "")
                    except Exception as e:
                        est_min_price = 0
                        est_max_price = 0
                    item["est_min_price"] = est_min_price
                    item["est_max_price"] = est_max_price

                    # 12 sold
                    # 13 sold_price
                    # 14 sold_price_dollar

                    try:
                        if lot['sLotStatus'] == "SOLD":
                            sold_price = lot['hammer_prices']['prices'][0]['value'].replace(
                                ",", "")
                            item["sold"] = 1
                            item["sold_price"] = sold_price
                    except Exception as e:
                        item["sold"] = 0
                        item["sold_price"] = 0

                    item["sold_price_dollar"] = None
                    # 15 url
                    url = "https://"+self.allowed_domains[0] + lot['url']
                    logging.debug(
                        "BonhamsSpider; msg=New URL is ;url= %s;", url)
                    item["url"] = url

                    resp = requests.get(url)
                    htmlr = HtmlResponse(
                        url="test", body=resp.text, encoding='utf-8')
                    # 8 Description

                    desc_name = ""
                    # desc_content_info = htmlr.xpath(
                    #     '//div[@class="lot-details__description__content"]/text()').extract()
                    desc_content_info = htmlr.xpath(
                        '//*[@id="skip-to-content"]/section/div/div/div[5]/div[1]/div/div/div[1]/div[1]/div').extract()

                    # Iterate over each HTML snippet
                    clean_data_string = ''

                    # Iterate over each HTML snippet
                    for html_snippet in desc_content_info:
                        # Parse HTML using BeautifulSoup
                        soup = BeautifulSoup(html_snippet, 'html.parser')

                        # Extract clean text
                        clean_data = soup.div.get_text(
                            separator='\n', strip=True)

                        # Concatenate clean data to the string
                        clean_data_string += clean_data + '\n'

                    desc_content = ""
                    for desc in desc_content_info:
                        desc_content = desc_content + desc

                    footnote_info = htmlr.xpath(
                        '//h3[@class="lot-details__description__footnotes"]/text()').extract()
                    footnote = ""
                    if footnote_info:
                        footnote_title = "<strong>" + \
                            footnote_info[0] + "</strong>"

                        notes_info = htmlr.xpath(
                            '//div[@class="lot-details__description__content"]/text()').extract()
                        footnote_desc = ""
                        for note in notes_info:
                            footnote_desc = footnote_desc + note
                        footnote = footnote_title + "<br/>" + footnote_desc

                    item["description"] = desc_name + \
                        desc_content + "<br/>" + footnote
                    item["status"] = "Success"
                    item["auction_url"] = response.url
                    item['total_lots'] = total_lot
                    item["job"] = self.job                    

                    yield scrapy.Request(url_for_image, callback=self.parse_image, meta={'item': item})

        except Exception as e:
            item['url'] = response.url
            item['status'] = "Failed"
            logging.error(
                "BonhamsSpider; msg=Crawling Failed > %s ;url= %s", str(e), response.url)
            logging.error("BonhamsSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
            yield item

    def parse_image(self, response):
        self.browser.get(response.url)
        print(f'\n-- url_for_image:: {response.url} --\n')
        parent_element = self.browser.find_element(
            By.XPATH, '/html/body/div[1]/main/section/div/div/div[3]/div/div[2]/div[1]/div')

        button_elements = parent_element.find_elements(By.XPATH, './/button')
        images = []
        for image in button_elements:
            try:
                img = image.find_element(By.XPATH, './/img')
                img_value = img.get_attribute("src")
                images.append(img_value)
            except NoSuchElementException:
                continue

        item = response.meta['item']
        print(f'\n--- images:: {images} --\n')
        item['images'] = images
        print(f'\n--- item:: {item} --\n')

        # Yield the item with the extracted image URLs
        yield item
