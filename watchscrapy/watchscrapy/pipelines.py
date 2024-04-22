from scrapy.exporters import CsvItemExporter
from scrapy import signals
from watchapp.models import AuctionHouse, Auction, Lot, Job
import logging
import traceback
from datetime import datetime
from django.utils import timezone
import requests
import json
from .s3_operations import S3Operations
from django.conf import settings
import os


class WatchscrapyPipeline(object):
    def __init__(self):
        job = ""
        base_rate = {}
        rates = self.get_base_rate()

    def close_spider(self, spider):
        logging.warn(
            "WatchExtraction; msg=All Data Extraction  has been Completed;")
        job = Job.objects.get(name=self.job)
        job.status = "Completed"
        job.end_time = timezone.now()
        job.save()

    def process_item(self, item, spider):
        auct_url = item["auction_url"]
        try:
            self.job = item["job"]
            # if item["status"] == "Failed":
            #    self.status = "Failed"

            prev_auction = Auction.objects.filter(
                url=item["auction_url"]).first()
            # MB - save the latest job for the lot
            if prev_auction:
                auction_id = prev_auction.pk
                prev_auction.job = self.job
                prev_auction.save()
            else:
                auction = Auction()
                auction.job = self.job
                auction.name = item["name"]
                auction.date = datetime.strptime(
                    item["date"].strip(), '%b %d,%Y').strftime('%Y-%m-%d')
                auction.place = item["location"]
                auction.url = item["auction_url"]
                auction.actual_lots = int(item["total_lots"])
                auction.auction_house_id = item["house_name"]
                auction.save()
                auction_id = auction.pk

            prev_lot = Lot.objects.filter(url=item["url"])
            if prev_lot:
                prev_lot.delete()

            lot = Lot()
            lot.job = self.job
            lot.url = item["url"]
            lot.status = item["status"]
            lot.lot_number = item["lot"]
            lot.title = item["title"]
            lot.description = item["description"]
            lot.estimate_min_price = item["est_min_price"]
            lot.estimate_max_price = item["est_max_price"]
            lot.lot_currency = item["lot_currency"]
            lot.sold = item["sold"]
            lot.sold_price = item["sold_price"]
            lot.images = item["images"]

            # download this image and save locally
            s3_ops = S3Operations(lot.images)

            save_path = os.path.join(
                settings.BASE_DIR, 'static', 'tempImages', lot.job, str(lot.lot_number))

            s3_image_url = s3_ops.download_image(save_path)
            print(f'\n\n s3_image_url:: {s3_image_url}\n\n')
            
            lot.s3_image = s3_image_url
            if item["lot_currency"] == "N/A":
                sold_price_usd = 0
            else:
                sold_price_usd = self.get_usd_amount(
                    item["lot_currency"], item["sold_price"])
            lot.sold_price_dollar = sold_price_usd

            lot.auction_id = auction_id
            lot.save()
            logging.info(
                "WatchExtraction; msg=Processing Completed; url= %s", item["url"])
        except Exception as e:
            logging.error(
                "WatchExtraction; msg=Processing Failed > %s; url= %s", str(e), item["url"])
            logging.error("WatchExtraction; msg=Processing Failed; url= %s; Error: %s",
                          item["url"], traceback.format_exc())
        return item

    def get_base_rate(self):
        # response = requests.get("https://api.exchangeratesapi.io/latest?base=USD")
        # respj = json.loads(response.text)
        # self.base_rate = respj["rates"]
        self.base_rate = {"rates": 130, 'base_currency': 130}

    def get_usd_amount(self, base_currency, price):
        usd_price = 0
        if base_currency == "€":
            base_currency = "EUR"
        if base_currency == "&#163;":
            base_currency = "GBP"
        if base_currency == "$":
            base_currency = "USD"
        if base_currency == "HK$":
            base_currency = "HKD"
        if base_currency and base_currency in self.base_rate.keys():
            rate = self.base_rate[base_currency]
            if rate > 0:
                usd_price = int(price)/rate
        return round(usd_price)
