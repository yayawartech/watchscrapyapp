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
from json import JSONDecodeError


# additions
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from watchscrapy.items import WatchItem
# from watchapp.models import Setup


class ChristiesSpider(scrapy.Spider):
    name = "christiesSpider"
    allowed_domains = ["onlineonly.christies.com"]
    start_urls = [
        'https://onlineonly.christies.com/s/watches-online-top-time/lots/3229']

    def __init__(self, url='', job='', *args, **kwargs):
        super(ChristiesSpider, self).__init__(*args, **kwargs)
        # self.start_urls = [
            # 'https://onlineonly.christies.com/s/watches-online-top-time/lots/3229']
        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        # setup = Setup.objects.first()
        # SELENIUM_CHROMEDRIVER_PATH = setup.chromedriver
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('headless')
        # browser = webdriver.Chrome(executable_path=SELENIUM_CHROMEDRIVER_PATH, options=options)
        # driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=options)
        browser = webdriver.Chrome(options=options)
        return browser
        
    def start_requests(self):

        for source_url in self.start_urls:
            try:
                logging.warn(
                    "ChristiesSpider; msg=Spider started;url= %s", source_url)
                browser = self.sel_configuration()
                browser.set_window_size(1440, 900)

                response = requests.get(source_url)
                url = response.url
                should_continue = True
                if 'onlineonly.christies.com/s/' in url:
                    try:
                        christies_version = 2
                        # url += '?' if '?' not in url else ''
                        url += "&showAll=True&SortBy=LotNumber" if '?' in url else "?showAll=True&SortBy=LotNumber"

                        print(f'\n\n-----url:: {url}----\n\n')
                        response = requests.get(url)

                        time.sleep(5)
                        resp = response.text
                        print(f'\n\n------------resp::: {resp} ------\n\n')

                        a = "new LotListModule.LotList(lotListDataUrl, saleId, showPopup, "
                        b = "});"
                        # c = self.between(resp,a,b)

                        # print(f'\n******* C:{c}******\n\n')

                        # value = self.before(c,"ko.applyBindings(lotListViewModel);")
                        # jsonv = value.rstrip()[:-2]
                        # self.final_json = json.loads(jsonv)

                        # print(f'\n\n++++++++++++final_json:: {self.final_json}+++++++\n\n')
                    except JSONDecodeError as e:
                        logging.warn(
                            "ChristiesSpider; msg=Spider Halted!!  No data found in URL;url= %s", source_url)
                        should_continue = False
                else:
                    logging.debug(
                        "ChristiesSpider; msg=Version 1 detected;url= %s", source_url)
                    christies_version = 1
                    url = url + "&pg=all"

                if should_continue:
                    browser.get(url)
                    delay = 20  # seconds
                    time.sleep(5)
                    # myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'load-all')))
                    # total_lots = myElem.text
                    # logging.warn("ChristiesSpider; msg=Total Lots: %s;url= %s",total_lots,source_url)
                    # myElem.click()
                    # time.sleep(5)
                    if christies_version == 1:
                        links = browser.find_elements_by_css_selector(
                            "div.image-preview-container a")
                    else:
                        links = browser.find_elements_by_css_selector(
                            "a.box-link")
                    print(f'\n\n-----link:: {link} ------\n\n')
                    lots_urls = []
                    for link in links:
                        link_url = link.get_attribute('href')
                        if link_url is not None:
                            lots_urls.append(link_url)
                    total_lots = len(lots_urls)
                    logging.warn(
                        "ChristiesSpider; msg=Total Lots: %s;url= %s", total_lots, source_url)
                    browser.close()
                    logging.debug(
                        "ChristiesSpider; msg=Moving ahead;url= %s", source_url)
                    for i in range(total_lots):
                        url = lots_urls[i]
                        if christies_version == 1:
                            yield scrapy.Request(url, callback=self.parse, meta={"auction_url": source_url, 'lots': total_lots})
                        else:
                            sold_price = self.final_json["items"][i]["priceRealised"]
                            yield scrapy.Request(url, callback=self.parsev2, meta={"sold_price": sold_price, "auction_url": source_url, 'lots': total_lots})
            except Exception as e:
                item = WatchItem()
                item['status'] = "Failed"
                logging.error(
                    "ChristiesSpider; msg=Crawling Failed > %s;url=%s", str(e), source_url)
                logging.error("ChristiesSpider; msg=Crawling Failed;url=%sError=%s",
                              traceback.format_exc(), source_url)
                yield item

    def parse(self, response):
        if "searchresults.aspx" not in response.url:
            item = WatchItem()
            try:
                # 1 House Name
                item['house_name'] = 5

                # 2 Auction Name
                name = response.xpath(
                    '//*[@id="main_center_0_lblSaleTitle"]/text()').extract()
                item['name'] = name[0]

                # 3 Date
                date = response.xpath(
                    '//*[@id="main_center_0_lblSaleDate"]/descendant-or-self::*/text()').extract_first() or None
                date = date.split("-")[-1].strip()
                item['date'] = datetime.strptime(
                    date.strip(), '%d %B %Y').strftime('%b %d,%Y')
                # 4 Location
                location = response.xpath(
                    '//*[@id="main_center_0_lblSaleLocation"]/descendant-or-self::*/text()').extract_first() or None
                item['location'] = location

                # 5 Lot
                lot = response.xpath(
                    '//*[@id="main_center_0_lblLotNumber"]/descendant-or-self::*/text()').extract_first() or None
                item['lot'] = lot.split(" ")[0].strip()
                # 6 Images
                main_image = response.xpath(
                    '//*[@id="main_center_0_imgCarouselMain"]/li[1]/a/@href').extract_first() or None
                other_images = response.xpath(
                    '//*[@id="imgCarouselThumb"]/li/a/@href').extract() or None
                item['images'] = main_image
                if other_images is not None:
                    for i, img in enumerate(other_images, 0):
                        if i > 0:
                            item['images'] = item['images'] + ',' + img
                # 7 Title
                title_info = response.xpath(
                    '//*[@id="main_center_0_lblLotPrimaryTitle"]/b/text()').extract()
                if not title_info:
                    title_info = response.xpath(
                        '//*[@id="main_center_0_lblLotPrimaryTitle"]/text()').extract()
                title = ""
                for title_c in title_info:
                    title = title + " " + title_c
                item['title'] = title.strip()

                # 8 Description
                description = response.xpath(
                    '//*[@id="main_center_0_lblLotDescription"]/descendant-or-self::*/text()').extract() or None
                item['description'] = description
                price_text = response.xpath(
                    '//*[@id="main_center_0_lblPriceEstimatedPrimary"]/descendant-or-self::*/text()').extract_first() or None
                if price_text is not None:
                    lot_currency = price_text.split('-')[0].strip()[0:4]
                    est_min_price = price_text.split(
                        '-')[0].strip()[4:].replace(",", "")
                    est_max_price = price_text.split(
                        '-')[1].strip()[4:].replace(",", "")
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
                sold_text = response.xpath(
                    '//*[@id="main_center_0_lblPriceRealizedPrimary"]/descendant-or-self::*/text()').extract_first() or None
                if sold_text is not None:
                    sold_currency = sold_text[0:4]
                    sold_price = sold_text[4:].replace(",", "")
                item['sold_price'] = sold_price

                # 13 Sold Price Dollar
                item['sold_price_dollar'] = 0
                item["sold"] = 1
                # 14  URL
                item['url'] = response.url
                item["status"] = "Success"
            except Exception as e:
                item['status'] = "Failed"
                logging.error(
                    "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
                logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                              response.url, traceback.format_exc())
            item['total_lots'] = response.meta.get("lots")
            item["auction_url"] = response.meta.get("auction_url")
            item["job"] = self.job
            yield item

    def parsev2(self, response):
        item = WatchItem()

        try:
            # 1 House Name
            item['house_name'] = 5

            # 2 Auction Name
            name = response.xpath(
                '//div[contains(@class, "generic-sale-header-container")]//div[contains(@class, "title")]/descendant-or-self::*/text()').extract_first().strip() or None
            item['name'] = name

            date_location_text = response.xpath(
                '//div[contains(@class, "date-location-container")]/span/text()').extract()
            location = date_location_text[0] or None
            date_pre = date_location_text[2]

            date = date_pre.split("-")[-1].strip()
            # 3 Date
            item['date'] = datetime.strptime(
                date.strip(), '%d %B %Y').strftime('%b %d,%Y')

            # 4 Location
            item['location'] = location

            # 5 Lot
            lot = response.xpath(
                '//div[@class="lot-number"]/span/text()').extract()[0].strip().split(" ")[-1]
            item['lot'] = lot.split(" ")[0].strip()

            # 6 Images
            images = response.xpath(
                '//div[contains(@class, "lotdetail-imgholder")]/div/@href').extract() or None
            item['images'] = images

            # 7 Title
            title_info = response.xpath(
                '//div[@class="bid-panel"]/div/div[@class="title"]/b').extract()
            if title_info:
                title = title_info[0]
            else:
                title = response.xpath(
                    '//div[@class="bid-panel"]/div/div[@class="title"]/text()').extract()[0].strip()

            item['title'] = title

            # 8 Description
            description_info = response.xpath(
                '//div[contains(@class, "lot-notes-row")]/descendant-or-self::*/text()').extract() or None
            description = ""
            for desc in description_info:
                description = description + desc
            item['description'] = description.strip()

            price_text = response.xpath(
                '//div[contains(@class, "estimated")]/descendant-or-self::*/text()').extract_first() or None
            if price_text is not None:
                lot_currency = price_text.split('-')[0].strip()[10:14]
                est_min_price = price_text.split(
                    '-')[0].strip()[14:].replace(",", "")
                est_max_price = price_text.split(
                    '-')[1].strip()[4:].replace(",", "")
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
            sold_price = response.meta.get("sold_price")
            item["sold_price"] = sold_price
            item["sold"] = 1

            # 13 Sold Price Dollar
            item['sold_price_dollar'] = 0

            # 14  URL
            item['url'] = response.url
            item["status"] = "Success"
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = response.meta.get("auction_url")
        item["job"] = self.job
        yield item

    def between(self, value, a, b):
        # Find and validate before-part.
        pos_a = value.find(a)
        print(f'\n\npos_a:::{pos_a}\n\n')
        if pos_a == -1:
            return ""
        # Find and validate after part.
        pos_b = value.rfind(b)
        if pos_b == -1:
            return ""
        # Return middle part.
        adjusted_pos_a = pos_a + len(a)
        if adjusted_pos_a >= pos_b:
            return ""
        return value[adjusted_pos_a:pos_b]

    def before(self, value, a):
        # Find first part and return slice before it.
        pos_a = value.find(a)
        if pos_a == -1:
            return ""
        return value[0:pos_a]
