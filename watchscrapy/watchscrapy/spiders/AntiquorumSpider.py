# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import traceback
from watchscrapy.items import WatchItem
from datetime import datetime
import math


class AntiquorumSpider(scrapy.Spider):
    name = "antiquorumSpider"
    allowed_domains = ["catalog.antiquorum.swiss"]
    # start_urls = ['https://catalog.antiquorum.swiss/auctions/324/lots']

    def __init__(self, url='', job=0, *args, **kwargs):
        super(AntiquorumSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    # def start_requests(self):
    #     # Provide a complete URL with the scheme (e.g., "http://" or "https://")
    #     start_urls = [
    #         'https://catalog.antiquorum.swiss/en/auctions/only_Online_auction_geneva_december_2022/lots']
    #     for url in start_urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        total_lots = response.xpath(
            '//h4[@class="d-inline align-middle"]/span/text()').extract_first().strip().split(" ")[0]

        logging.warn(
            "AntiquorumSpider; msg=Spider started;url= %s", response.url)
        lots_per_page = 20
        total_pages = math.ceil(int(total_lots)/lots_per_page)
        logging.warn("AntiquorumSpider; Total Pages = %s ; URL: %s;",
                     total_pages, response.url)
        for i in range(0, total_pages):
            absolute_url = response.url+"?page="+str(i+1)
            yield scrapy.Request(absolute_url, callback=self.parse_urls, meta={"auction_url": response.url, 'lots': total_lots})

    def parse_urls(self, response):
        products = response.xpath('//div[@id="products"]')
        url_list = products.xpath(
            '//div[@class="shadow mt-4"]/div[@class="row"]/div[@class="N_lots_thumbail col-sm p-2"]/div[@class="mt-4"]/a/@href').extract()
        sold_pre_list = products.xpath('//div[@class="row"]/div[@class="col"]')

        """ For sold only
        sold_list = []
        final_url_list = []
        for sel in range(len(url_list)):
            sold = sold_pre_list[sel].xpath('div[@class="N_lots_price mt-0"]').extract()
            if sold:
                final_url_list.append(url_list[sel])
        
        """
        final_url = []
        for url in url_list:
            final_url.append("https://" + self.allowed_domains[0] + url)
        logging.debug("AntiquorumSpider; msg=URLs to be Scraped %s;url= %s", len(
            final_url), response.url)
        for url in final_url:
            # print(f'\n\n---------------url:: {url}-------------------\n\n')
            yield scrapy.Request(url, callback=self.parse_item, meta={"auction_url": response.meta.get("auction_url"), "lots": response.meta.get("lots")})

    def parse_item(self, response):
        item = WatchItem()
        try:
            all_desc = response.xpath(
                '//div[@class="container"]/div/div[1]/div[2]')
            if all_desc is None:
                all_desc = response.xpath(
                    '//div[@class="container"]/div/div[1]/div[2]').extract()

            item['house_name'] = 1

            name = all_desc.xpath("//p[1]/text()").extract_first() or None
            item['name'] = name

            date_location = all_desc.xpath(
                "//p[3]/text()").extract_first() or None
            date_location_list = date_location.split(",")
            date = date_location_list[-2] + date_location_list[-1]

            item['date'] = datetime.strptime(
                date.strip(), '%b %d %Y').strftime('%b %d,%Y')

            location = date_location_list[0] or None
            item['location'] = location

            lot = all_desc.xpath(
                '//h3/text()').extract_first().strip().split(" ") or None
            lot_number = re.findall(r'\d+', lot[1])[0]
            item['lot'] = lot_number

            # images_url = response.xpath(
            #     '//div[@class="container"]/div[@class="container"]/div/div/div[1]/div[2]/a/@href').extract()

            images_url = response.xpath(
                '/html/body/div[10]/div[2]/div[1]/div[3]/div[3]/a[1]/@href').extract()[0]

            item['images'] = images_url

            title = all_desc.xpath('//strong/p/text()').extract_first()
            if not title:
                title = all_desc.xpath(
                    '//strong/div/font/strong/text()').extract_first()
            if not title:
                title = all_desc.xpath(
                    '//strong/div/strong/text() | //strong/div/text()').getall() or []
                title = ' '.join(title)
            item['title'] = title.strip()

            desc = all_desc.xpath('//p').extract() or None
            description = ""
            for i in range(4, len(desc)):
                if "color" not in desc[i]:
                    description = description + desc[i]
                    continue
                else:
                    break

            raw_table_data = all_desc.xpath(
                'div[@class="row"]/div/div/div/table').extract()
            table_data = ""
            if raw_table_data:
                table_data = "Table:: " + \
                    re.sub("\t", "", re.sub("\n", "", raw_table_data[0]))

            desciption = description + table_data

            notes = response.xpath(
                '//div[@class="container"]/div[@class="container"]/div/div[2]/div/text()').extract()
            if notes:
                descrption = desciption + notes[0]

            item['description'] = description

            min_max_price = all_desc.xpath(
                "//h4[1]/text()").extract_first().strip().split(" ")
            est_min_price = est_max_price = 0
            lot_currency = ""
            if len(min_max_price) > 3:
                est_min_price = min_max_price[1].replace(",", "")
                est_max_price = min_max_price[3].replace(",", "")
                lot_currency = min_max_price[0]

            item['est_min_price'] = est_min_price
            item['est_max_price'] = est_max_price
            item['lot_currency'] = lot_currency

            sold_info = all_desc.xpath("//h4[2]/text()").extract_first()
            sold = sold_price = sold_price_dollar = 0

            if "Sold" in sold_info:
                sold = 1
                sold_price = sold_info.strip().split(" ")[2].replace(",", "")

            item["sold"] = sold
            item['sold_price'] = sold_price
            item['sold_price_dollar'] = sold_price_dollar
            item['url'] = response.url
            item['status'] = "Success"
            item['total_lots'] = response.meta.get("lots")
            logging.info(
                "AntiquorumSpider; msg=Crawling Processed;url= %s", response.url)
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "AntiquorumSpider; msg=Crawling Failed;url= %s", response.url)
            logging.debug("AntiquorumSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
        item["auction_url"] = response.meta.get("auction_url")
        item["job"] = self.job
        return item
