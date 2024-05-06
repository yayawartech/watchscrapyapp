# -*- coding: utf-8 -*-
import scrapy
import re
import json
import logging,traceback
import datetime

from watchscrapy.items import WatchItem


class DorotheumSpider(scrapy.Spider):
    name = "dorotheumSpider"
    allowed_domains = ["www.dorotheum.com"]
    
    def __init__(self, url='',job='', *args, **kwargs):
        super(DorotheumSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def start_requests(self):
        start_urls = ['https://www.dorotheum.com/en/a/93739/']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        logging.warn("DorotheumSpider; msg=Spider started;url= %s",response.url)
        try:
            all_lots = response.xpath('//div[@id="lot-list-container"]/ul/li[@class="flex-row table-row no-list-style"]')
            total_lots = len(all_lots)
            logging.warn("DorotheumSpider; msg=Total Lots: %s;url= %s",total_lots,response.url)

            #2
            name_info = response.xpath('//h1[@class="headline"]/text()').extract()
            if not name_info:
                name_info = response.xpath('//div[@class="global-side-spacing"]/ul/li[3]/text()').extract()[0].split("-")
            
            name = name_info[0].strip()
            #3
            container_info = response.xpath('//div[@class="blue-container"]')
            if not container_info:
                container_info = response.xpath('//div[@class="yellow-container"]')

            date = response.xpath('//div[@class="global-side-spacing"]/ul/li[3]/text()').extract()[0].split("-")[-1].strip()
            
            #4
            location_pre_info = container_info.xpath('p/a/span/text()')
            if not location_pre_info:
                location_pre_info = container_info.xpath('p/a/text()')
                if not location_pre_info:
                    location = "Online"
                else:
                    location = location_pre_info[0].extract().strip()
            else:
                location = location_pre_info[0].extract().strip()

            for lots in all_lots:
                url_segment = lots.xpath('div[2]/a/@href').extract()[0]
                final_url = "https://" + self.allowed_domains[0] + url_segment
                lot_number_info = lots.xpath('div[2]/a/div/p/text()').extract()[0].strip().split(" ")
                lot_number = lot_number_info[2].split("-")[0]

                if lot_number == "+":
                    lot_number = lot_number_info[-2]
                items = {'name':name,'date':date,'location':location,'lot_number':lot_number,'auction_url':response.url,'lots':total_lots}
                yield scrapy.Request(final_url,callback=self.parse_url,meta=items)
        except Exception as e:
            item = WatchItem()
            item['auction_url'] = response.url
            item['status'] = "Failed"
            logging.error("DorotheumSpider; msg=Crawling Failed > %s;url= %s",str(e),response.url)
            logging.debug("DorotheumSpider; msg=Crawling Failed;url= %s;Error=%s",response.url,traceback.format_exc())
            yield item

    def parse_url(self,response):
        item = WatchItem()

        try:
            #1 HouseName
            house_name = 6
            item["house_name"] = house_name

            #2 Name
            name = response.meta.get("name")
            item["name"] = name

            #3 Date
            date = response.meta.get("date")
            item["date"] = datetime.datetime.strptime(date, '%d.%m.%Y').strftime('%b %d,%Y')

            #4 Location
            location = response.meta.get("location")
            item["location"] = location

            #5 Lot Number
            lot_number = response.meta.get("lot_number")
            item["lot"] = lot_number

            #6 Images
            images_info = '{"val":'+response.xpath('//div[@class="zoomify"]/@data-json')[0].extract()+'}'
            images_info_json = json.loads(images_info)
            images_list = images_info_json["val"]

            img_list = []
            for images in images_list:
                image_url_segment = "https://"+self.allowed_domains[0] + "/"+images["bild"]
                img_list.append(image_url_segment)

            # item["images"] = img_list
            item["images"] = img_list[0]
            
            #7 title
            title = response.xpath('//h2[@class="headline"]/text()').extract()[0].strip()
            item["title"] = title
        
            #8 Description
            # desc = response.xpath('//div[@class="mobile-hidden"]/div/p/text()').extract()[0].strip()
            desc = response.xpath('//div[@class="mobile-hidden"]/div/p/text()').extract()
            desc= " ".join(desc)
            # //*[@id="bild-box"]/div[2]/div[1]/p
            print(f'\n\ndesc:: {desc} \n\n')
            spec_desc_info = response.xpath('//div[@class="mobile-hidden"]/p/text()').extract()
            spec_desc = ""
            if spec_desc_info:
                spec_desc = spec_desc_info[0].strip()

            item["description"] = desc + "/n" + spec_desc

            price_info = response.xpath('//div[@id="auktion-details"]/div[@class="row"]/div[1]')
            all_price = price_info.xpath('dl/dd/span/text()').extract()


            #9 Lot Currency
            lot_currency = all_price[0].split(" ")[0]
            item["lot_currency"] = lot_currency

            #10 Est min Price
            sold = 0
            sold_price = 0
            if len(all_price) > 1:
                est_min_price = all_price[1].split(" ")[1].split(".")[0].replace(",","")
                sold = 1
                sold_price = all_price[0].split(" ")[1].split(".")[0].replace(",","")
            else:
                est_min_price = all_price[0].split(" ")[1].split(".")[0].replace(",","")
            item["est_min_price"] = est_min_price

            #11 Est max Price
            item["est_max_price"] = 0
            
            #12 sold
            item["sold"] = sold
            
            #13 sold_price
            item["sold_price"] = sold_price

            #14 sold_price_dollar
            item["sold_price_dollar"] = 0

            #15 url
            item["url"] = response.url
            item["status"] = "Success"
        except Exception as e:
            item['status'] = "Failed"
            logging.error("DorotheumSpider; msg=Crawling Failed > %s;url= %s",str(e),response.url)
            logging.debug("DorotheumSpider; msg=Crawling Failed;url= %s;Error=%s",response.url,traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = response.meta.get("auction_url")
        item["job"] = self.job
        yield item

# Images are in array. Either store in array or store just single image