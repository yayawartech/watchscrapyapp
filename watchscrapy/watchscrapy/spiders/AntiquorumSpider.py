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

            try:
                title = self.get_title(response)
                if title:
                    # print(f'\n-- title:: {title} --\n url:: {response.url}')
                    item['title'] = title
            except:
                item['title'] = None

            data = ""
            col = response.xpath('/html/body/div[10]/div[2]/div[2]/div[2]')

            # Iterate through each <p> tag
            for p in col.xpath('.//p'):
                # Extract the key from <strong> within the <p>
                key = p.xpath('./strong/text()').get(default='').strip()

                # Extract the value from the remaining text within the <p>
                value_parts = p.xpath('./text()[normalize-space()]').getall()
                value = ' '.join(value_parts).strip()

                # Combine key and value
                if key and value:
                    data += f"{key}: {value}<br/>"

            item['description'] = data.strip()

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

    def get_title(self, response):
        try:
            all_xpaths = ['/html/body/div[10]/div[2]/div[1]/div[2]/p[4]/text()',
                          '/html/body/div[10]/div[2]/div[1]/div[2]/div[1]/strong/text()',
                          '/html/body/div[10]/div[2]/div[1]/div[2]/div[2]/text()', '/html/body/div[10]/div[2]/div[1]/div[2]/div[1]']
            for one_xpath in all_xpaths:
                try:
                    element = response.xpath(one_xpath).extract()
                    if element:
                        title_text = element[0].strip()
                        if title_text:
                            return title_text
                except Exception as e:
                    pass
        except Exception as e:

            logging.warn(f"An error occurred while getting the title: {e}")

        return None
