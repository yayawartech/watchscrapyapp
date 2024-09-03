# -*- coding: utf-8 -*-
import scrapy
import re
import json
import logging
import traceback
from datetime import datetime
from watchscrapy.items import WatchItem
from selenium.common.exceptions import NoSuchElementException


class BukowskisSpider(scrapy.Spider):
    name = "bukowskisSpider"
    allowed_domains = ["www.bukowskis.com"]

    def __init__(self, url='', job='', *args, **kwargs):
        super(BukowskisSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def start_requests(self):
        # start_urls = ['https://www.bukowskis.com/en/auctions/F215/lots']
        # https://www.bukowskis.com/en/auctions/627/lots
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # -1 because, there is a span called as next or previous
        pagination = response.xpath('//nav[@class="c-pagination"]')
        page_numbers = 1
        if pagination:
            page_numbers = len(pagination[0].xpath('span'))
        total_lots = response.xpath(
            '//div[@class="c-lot-index__top-pagination-count"]/text()').extract()[0].split(" ")[0]

        logging.warn("BukowskisSpider; msg=Total Lots : %s ;url= %s",
                     total_lots, response.url)
        auction_url = response.url
        for page in range(page_numbers):
            absolute_url = response.url+"/page/"+str(page+1)
            yield scrapy.Request(absolute_url, callback=self.parse_urls, meta={"auction_url": auction_url, "lots": total_lots})

    def parse_urls(self, response):
        logging.warn(
            "BukowskisSpider; msg=Spider started;url= %s", response.url)
        try:
            all_lots = response.xpath(
                '//div[@class="c-lot-index__lots"]/div/div')

            # 2
            name = response.xpath(
                '//div[@class="c-headline-block"]/h1/text()').extract()[0]

            for lots in all_lots:
                url_segment = lots.xpath('a[1]/@href').extract()
                if url_segment:
                    final_url = "https://" + \
                        self.allowed_domains[0] + url_segment[0]

                    lot_number_text = lots.xpath(
                        '//*[@id="js-boost-target"]/div[2]/div[1]/div[4]/div[3]/div/text()').get()
                    if lot_number_text is None:
                        lot_number_text = lots.xpath(
                            '/html/body/div[2]/div[2]/div[1]/div[3]/div[3]/div').get()
                    match = re.search(r'(\d+)', lot_number_text)
                    if match:
                        lot_number = int(match.group(1))
                    else:
                        lot_number = None  # or some default value if no match is found

                    items = {'name': name, 'lot_number': lot_number, 'auction_url': response.meta.get(
                        "auction_url"), 'lots': response.meta.get("lots")}

                    yield scrapy.Request(final_url, callback=self.parse_lot_url, meta=items)
        except Exception as e:
            item = WatchItem()
            item['url'] = response.url
            item['status'] = "Failed"
            logging.error(
                "BukowskisSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.error("BukowskisSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
            yield item

    def parse_lot_url(self, response):

        item = WatchItem()
        try:
            # 1 HouseName
            house_name = 4
            item["house_name"] = house_name

            # 2 Name
            name = response.meta.get("name")
            item["name"] = name

            # 3 Date
            # date = response.meta.get("date")

            date = response.xpath(
                '//*[@id="js-boost-target"]/div[2]/div[1]/div[4]/div[4]/div[1]/div[1]/div[2]/div/time/div[1]/text()').get()
            if date:
                date = date.replace("\xa0", " ")
            else:
                date = "Jan 01, 1900"
            final_date = datetime.strptime(
                date.strip(), '%b %d, %Y').strftime('%b %d,%Y')
            item["date"] = final_date
            location = response.xpath(
                '//*[@id="js-boost-target"]/div[2]/div[1]/div[4]/div[4]/details[2]/div[1]/div/div[2]/div[1]/text()').extract()

            item["location"] = " ".join(location)

            # 5 Lot Number
            lot_number = response.meta.get("lot_number")

            item["lot"] = lot_number

            # 6 images
            images = []
            parent_element = response.xpath(
                '/html/body/div[2]/div[2]/div[1]/div[4]/div[2]/div/div[4]/div') or None
            if parent_element is None:
                parent_element = response.xpath(
                    "/html/body/div[2]/div[2]/div[1]/div[3]/div[2]/div/div[4]/div")
            for elem in parent_element:
                a_tag = elem.xpath('.//a')
                div = a_tag.xpath(".//div")
                img = div.xpath(".//img")
                img_url = img.xpath('@src').extract()
                images.append(img_url)
            item['images'] = img_url

            # 7 title

            title = response.xpath(
                '//*[@id="js-boost-target"]/div[2]/div[1]/div[4]/div[1]/div/div[1]/h1/text()').get() or None
            if title is None:
                title = response.xpath(
                    '/html/body/div[2]/div[2]/div[1]/div[3]/div[1]/div/div[2]/h1/text()').get()
            item["title"] = title

            # 8 Description

            description = response.xpath(
                '//*[@id="js-boost-target"]/div[2]/div[1]/div[4]/div[3]/div[3]/text()').extract()
            if not description:
                description = response.xpath(
                    '/html/body/div[2]/div[2]/div[1]/div[3]/div[4]/div[3]/p[1]/text()').extract()

            description = " ".join(description)
            item["description"] = description

            # 9 Lot Currency

            # estimation_info_elements = response.xpath(
            #     "/html/body/div[2]/div[2]/div[1]/div[3]/div[3]/div[2]/div[1]/div[2]/div[3]/text()").extract()
            estimation_info_elements = response.xpath(
                "/html/body/div[2]/div[2]/div[1]/div[3]/div[3]/div[2]/div[1]/div[2]/div[1]/text()").extract()
            if estimation_info_elements:
                estimation_info = estimation_info_elements[0]
                # Extract currency by splitting on whitespace and taking the last part
                currency = estimation_info.split()[-1].strip()

                # Remove the currency part from the string and split by '-' to get the price range
                price_range = estimation_info.rsplit(maxsplit=1)[0]
                min_price_str, max_price_str = price_range.split('-')

                # Remove non-breaking spaces and extra whitespace, then convert to integers
                min_price = int(re.sub(r'\D', '', min_price_str).strip())
                max_price = int(re.sub(r'\D', '', max_price_str).strip())
                item['lot_currency'] = currency
                item["est_min_price"] = min_price
                item["est_max_price"] = max_price
            else:
                estimation_info_elements = response.xpath(
                    '//*[@id="js-boost-target"]/div[2]/div[1]/div[4]/div[4]/div[1]/div[5]/div[2]/text()').extract() or None
                if estimation_info_elements:
                    item['lot_currency'] = estimation_info_elements[-1]
                    estimation_info = estimation_info_elements[0].replace(
                        "\xa0", " ")
                else:
                    # Fallback to the alternative XPath if the first one is empty
                    estimation_info_elements = response.xpath(
                        '/html/body/div[2]/div[2]/div[1]/div[3]/div[3]/div[2]/div[1]/text()').extract()

                    if estimation_info_elements:
                        estimation_info = estimation_info_elements[0].replace(
                            "\xa0", " ")
                    else:
                        # Set a default value or handle the absence of estimation_info
                        estimation_info = ""

                # 10 Est min Price
                est_min_price = 0
                estimation = ""
                if estimation_info:
                    estimation = estimation_info.replace(
                        estimation_info.split(" ")[-1], "").strip().split("-")
                    if estimation:
                        est_min_price = estimation[0].strip().replace(" ", "")

                item["est_min_price"] = est_min_price

                # 11 Est max Price
                est_max_price = 0
                try:
                    if len(estimation) > 1:
                        est_max_price = estimation[1].strip().replace(" ", "")
                except ValueError:
                    est_max_price = 0
                item["est_max_price"] = est_max_price

            # 12 sold
            sold_info = response.xpath(
                '//div[@class="c-live-lot-show-info__final-price-amount"]/text()')
            if sold_info:
                sold_price = sold_info[0].extract().replace(
                    "SEK", "").replace("\xa0", "")
                item["sold_price"] = sold_price
                item["sold"] = 1
            else:
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
                "BukowskisSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.error("BukowskisSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = response.meta.get("auction_url")
        item["job"] = self.job
        yield item
