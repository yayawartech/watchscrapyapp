# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import traceback
import requests
import json
from watchscrapy.items import WatchItem
from scrapy.http import HtmlResponse
from datetime import datetime


class ArtcurialSpider(scrapy.Spider):
    name = "artcurialSpider"
    allowed_domains = ["www.artcurial.com"]
    # start_urls = ['https://www.artcurial.com/en/sale-m1093-fine-watches']
    
    def __init__(self, url='', job='', *args, **kwargs):
        super(ArtcurialSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    # def start_requests(self):
    #     # Provide a complete URL with the scheme (e.g., "http://" or "https://")
    #     start_urls = ['https://www.artcurial.com/en/sale-m1106-le-temps-est-feminin']
    #     for url in start_urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(f'\n--------------new_url:: INSIDE PARSE ------------------\n')
        logging.warn(
            "ArtcurialSpider; msg=Spider started;url= %s", response.url)
        try:
            general_info = response.xpath(
                '//div[@id="sticky-infos"]/p/span/text()').extract()[0].strip().split("-")
            # 2
            name = general_info[0].strip()
            # 3
            date = general_info[1].strip()
            # 4
            location = "Online"

            nid = response.xpath(
                '//head/link[@rel="shortlink"]/@href').extract()[0].split("/")[-1]
            new_url = "https://" + \
                self.allowed_domains[0] + \
                "/en/ajax/load-more?_format=json&nid=" + nid + "&context=sale"
            print(f'\n--------------new_url:: {new_url}------------------\n')
            resp = requests.get(new_url)
            respj = json.loads(resp.text)
            htmlr = HtmlResponse(
                url="test", body=respj["html"], encoding='utf-8')

            auction_url = response.url

            all_lots = htmlr.xpath(
                '//div[contains(@class,"mosaic__item col-xs-10 col-sm-6 col-lg-4")]')
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
