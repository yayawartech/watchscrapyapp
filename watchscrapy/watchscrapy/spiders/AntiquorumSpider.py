import re
import math
import scrapy
import logging
import traceback
from datetime import datetime
from watchscrapy.items import WatchItem


class AntiquorumSpider(scrapy.Spider):
    name = "antiquorumSpider"
    allowed_domains = ["catalog.antiquorum.swiss"]
    # start_urls = ['https://catalog.antiquorum.swiss/auctions/324/lots']

    def __init__(self, url='', job=0, *args, **kwargs):
        super(AntiquorumSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

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

        final_url = []
        for url in url_list:
            final_url.append("https://" + self.allowed_domains[0] + url)
        logging.debug("AntiquorumSpider; msg=URLs to be Scraped %s;url= %s", len(
            final_url), response.url)
        for url in final_url:
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

            name = response.xpath(
                "/html/body/div[10]/div[2]/div[1]/div[2]/p[1]/text()").extract()
            name_title = " ".join(name)
            item['name'] = name_title

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

            parent_element = response.xpath(
                '/html/body/div[10]/div[2]/div[1]/div[3]/div[3]').extract()
            images = []

            for html_text in parent_element:
                # Parse the HTML text using Scrapy's Selector
                selector = scrapy.Selector(text=html_text)

                # Extract URLs using XPath
                a_tags = selector.xpath('.//a')
                for a_tag in a_tags:
                    img_url = a_tag.xpath('./@href').get()
                    images.append(img_url)

            item['images'] = images

            title = response.xpath(
                "/html/body/div[10]/div[2]/div[1]/div[2]/p[4]/text()").extract()

            # Check if the primary extraction was successful
            if title:
                item['title'] = title[0].strip()
            else:
                # Attempt to extract title from alternative XPaths
                title1 = response.xpath(
                    "/html/body/div[10]/div[2]/div[1]/div[2]/div[1]/strong/text()").extract()
                title2 = response.xpath(
                    '/html/body/div[10]/div[2]/div[1]/div[2]/div[2]/text()').extract()

                # Initialize an empty string for title
                combined_title = ""

                # Combine title1 if present
                if title1:
                    combined_title += title1[0].strip()

                # Combine title2 if present
                if title2:
                    combined_title += title2[0].strip()

                # Set item['title'] if any title was found
                if combined_title:
                    item['title'] = combined_title
                else:
                    # Handle case where no title could be found
                    item['title'] = 'Title not found'

            data = ""
            col = response.xpath('/html/body/div[10]/div[2]/div[2]/div[2]')

            data += f"Brand: {col.xpath(
                'p/strong[contains(text(), "Brand")]/following-sibling::text()').get()}\n"
            data += f"Model: {col.xpath(
                'p/strong[contains(text(), "Model")]/following-sibling::text()').get()}\n"
            data += f"Reference: {col.xpath(
                'p/strong[contains(text(), "Reference")]/following-sibling::text()').get()}\n"
            data += f"Year: {col.xpath(
                'p/strong[contains(text(), "Year")]/following-sibling::text()').get()}\n"
            data += f"Calibre: {col.xpath(
                'p/strong[contains(text(), "Calibre")]/following-sibling::text()').get()}\n"
            data += f"Case No.: {col.xpath(
                'p/strong[contains(text(), "Case No.")]/following-sibling::text()').get()}\n"
            data += f"Bracelet: {col.xpath(
                'p/strong[contains(text(), "Bracelet")]/following-sibling::text()').get()}\n"
            data += f"Diameter: {col.xpath(
                'p/strong[contains(text(), "Diameter")]/following-sibling::text()').get()}\n"
            data += f"Signature: {col.xpath(
                'p/strong[contains(text(), "Signature")]/following-sibling::text()').get()}\n"
            data += f"Accessories: {col.xpath(
                'p/strong[contains(text(), "Accessories")]/following-sibling::text()').get()}\n"
            description = data

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
            sold = sold_price = 0

            if "Sold" in sold_info:
                sold = 1
                sold_price = sold_info.strip().split(" ")[2].replace(",", "")

            item["sold"] = sold
            item['sold_price'] = sold_price
            item['sold_price_dollar'] = None
            item['url'] = response.url
            item['status'] = "Success"
            item['total_lots'] = response.meta.get("lots")
            logging.info(
                "AntiquorumSpider; msg=Crawling Processed;url= %s", response.url)
        except Exception as e:
            item['status'] = "Failed"

            logging.error("AntiquorumSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
        item["auction_url"] = response.meta.get("auction_url")
        item["job"] = self.job
        return item

    def clean_description(self, description):
        # Remove leading and trailing whitespace
        description = description.strip()

        # Replace multiple spaces with a single space
        description = re.sub(r'\s+', ' ', description)

        # Remove extra whitespace around slashes and hyphens
        description = re.sub(r'\s*([-\/])\s*', r'\1', description)

        return description
