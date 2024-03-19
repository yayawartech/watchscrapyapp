# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import traceback
from datetime import datetime
import re

from watchscrapy.items import WatchItem


class PhillipsSpider(scrapy.Spider):
    name = "phillipsSpider"
    allowed_domains = ["www.phillips.com"]
    start_urls = ['https://www.phillips.com/auctions/auction/NY080119']

    def __init__(self, url='', job='', *args, **kwargs):
        super(PhillipsSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def parse(self, response):

        logging.warn(
            "PhillipsSpider; msg=Spider started;url= %s", response.url)
        all_lots = response.xpath(
            '//div[@class="auction-page__grid"]/ul/li[@class="lot single-cell"]/div[@class="phillips-lot"]')
        auction_details = response.xpath('//div[@class="auction-details"]')
        total_lots = response.xpath(
            '//div[@class="auction-page__grid__nav__info"]/text()').extract_first().split(" ")[1].strip()
        logging.debug("PhillipsSpider; msg=Total Lots: %s;url= %s",
                      len(all_lots), response.url)
        logging.debug("PhillipsSpider; msg=Total Lots: %s;url= %s",
                      total_lots, response.url)
        # 2 Auction Name
        name = response.xpath(
            '//h1[@class="auction-page__hero__title"]/text()').extract()[0].strip()

        date_location = response.xpath(
            '//span[@class="auction-page__hero__date"]/text()').extract()[0].strip().split("Auction")

        # 3 Date
        """
        if "M" in date_location[-1].upper():
            date_info = date_location[-4].split("-")[-1] + " " + date_location[-3] + " " + date_location[-2]
        else:
            date_info = date_location[-3].split("-")[-1] + " " + date_location[-2] + " " + date_location[-1]
        
        date = datetime.strptime(date_info.strip(),'%d %B %Y').strftime('%b %d,%Y')
        #4 Location
        location = date_location[0].strip()
        """

        # 3 Date

        date_info = date_location[1].split(" ")
        date_str = date_info[-3] + " " + date_info[-2] + " " + date_info[-1]

        date = datetime.strptime(
            date_str.strip(), '%d %B %Y').strftime('%b %d,%Y')

        # 4 Location
        location = date_location[0].strip()

        for lot in all_lots:
            url_info = lot.xpath(
                'div[@class="phillips-lot__image"]/a[@class="detail-link"]/@href').extract()
            if url_info:
                yield scrapy.Request(url_info[0], callback=self.parse_details, meta={'lot': lot, 'name': name, 'date': date, 'location': location, 'base_url': url_info[0], 'auction_url': response.url, 'lots': total_lots})

    def parse_details(self, response):
        item = WatchItem()
        try:
            lot = response.meta.get('lot')
            base_url = response.meta.get('base_url')
            # 1 House Name
            house_name = 8
            item["house_name"] = house_name

            # 2 Auction Name
            name = response.meta.get('name')
            item["name"] = name

            # 3 Date
            date = response.meta.get('date')
            item["date"] = date

            # 4 Location
            location = response.meta.get('location')
            item["location"] = location

            # 5 Lot
            lot_number_info = response.xpath(
                "//h3[@class='lot-page__lot__number']/text()").extract_first()
            lot_number = re.findall(r'\d+', lot_number_info)[0]
            item["lot"] = lot_number
            title = response.xpath(
                '//h1[@class="lot-page__lot__maker__name"]/text()').extract()

            # desc = lot.xpath('a/p/span/text()').extract()

            # 6 Images
            auction_code = base_url.rsplit('/', 1)
            image_url = response.xpath(
                "//meta[@property='og:image']/@content").extract()
            item["images"] = image_url

            """
            if artist:
                title = artist
            else:
                title = lot_number   
            #7 Title
            if desc:
                title = artist + "-" + desc[1]
                if len(desc) > 2 and desc[len(desc)-1]!=" ":
                    title = title + "-" + desc[3]
            """
            item["title"] = title

            # 8 Description
            description = ""

            short_desc = response.xpath(
                "//meta[@name='description']/@content").extract_first()
            description = description + "\n"
            desc = response.xpath(
                '//ul[@class="lot-page__details__list"]/li[1]/p').extract()[0]
            description = description + desc
            essay_info = response.xpath(
                '//div[@class="lot-essay"]/p/text()').extract()
            essay = ""
            for para in essay_info:
                essay = essay + para
            description = description + "\n" + essay
            item["description"] = description

            # 10 Estimate Min Price
            # 11 Estimate Max Price
            estimation = lot.xpath(
                'a/p[@class="phillips-lot__description__estimate"]/text()').extract()
            est_min_price = est_max_price = 0
            if estimation:
                est_min_price = estimation[2].replace(",", "")
                est_max_price = estimation[4].replace(",", "")
            item["est_min_price"] = est_min_price
            item["est_max_price"] = est_max_price

            # 9 Lot Currency
            # 12 Sold Price

            sold_price_info = lot.xpath(
                'a/p[@class="phillips-lot__sold"]/text()').extract()
            sold_price = sold = 0
            lot_currency = ""
            if len(sold_price_info) > 1:
                sold = 1
                sold_price = sold_price_info[-1].replace(",", "")
                lot_currency = sold_price_info[-2]
            item["sold_price"] = sold_price
            item["lot_currency"] = lot_currency
            item["sold"] = sold
            # 13 Sold Price Dollar
            sold_price_dollar = 0
            item["sold_price_dollar"] = sold_price_dollar

            # 14  URL
            item['url'] = response.url

            item['status'] = "Success"
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "PhillipsSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.debug("PhillipsSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = response.meta.get("auction_url")
        item["job"] = self.job
        yield item
