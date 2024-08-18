import re
import time
import scrapy
import logging
import traceback
from scrapy import signals
from datetime import datetime
from selenium import webdriver
from WatchInfo.settings import DEBUG
from watchscrapy.items import WatchItem
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class MonacolegendSpider(scrapy.Spider):
    name = "monacolegendSpider"
    allowed_domains = ["www.monacolegendauctions.com"]

    def __init__(self, url='', job='', *args, **kwargs):
        super(MonacolegendSpider, self).__init__(*args, **kwargs)
        # self.start_urls = [
        #     'https://www.monacolegendauctions.com/auction/exclusive-timepieces-33']

        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        if not DEBUG:
            options.add_argument('headless')
            service = Service('/usr/local/bin/chromedriver')
            browser = webdriver.Chrome(service=service, options=options)
        else:
            browser = webdriver.Chrome(options=options)
        browser.set_window_size(1440, 900)
        return browser

    def start_requests(self):
        self.browser = self.sel_configuration()
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        source_url = response.url
        try:
            logging.warn(
                "MonacolegendSpider; msg=Spider started; url= %s", source_url)

            self.browser.get(response.url)
            time.sleep(5)
            logging.warning(
                "MonacolegendSpider; msg=Trying to load lots in next pages; url= %s", source_url)
            try:
                button = self.browser.find_element(
                    By.XPATH, '/html/body/main/section[1]/div/div/div[1]/details')

                # Use JavaScript to add the 'open' attribute to the element
                self.browser.execute_script(
                    "arguments[0].setAttribute('open', 'open')", button)
                time.sleep(2)
                try:
                    end_lot_number = self.browser.find_element(
                        By.XPATH, '/html/body/main/section[1]/div/div/div[1]/details/ul/li[3]').text
                    last_lot_number = re.search(
                        r'Lots (\d+)\s+to\s+(\d+)', end_lot_number).group(2)
                except NoSuchElementException:
                    end_lot_number = self.browser.find_element(
                        By.XPATH, '/html/body/main/section[1]/div/div/div[1]/details/p').text

                    match = re.search(
                        r'Session III:[\s\S]*?lots \d+ to (\d+)', end_lot_number)

                    if match:
                        last_lot_number = int(match.group(1))

                        logging.warn(
                            f'\n--- last_lot_number:: {last_lot_number} ---\n\n')

            except TimeoutException as e:
                logging.warning(
                    "MonacolegendSpider; msg=Did not found next button on the page. Assuming there is only one page. url=%s", source_url)

            # raised by browser.find_elements_by_css_selector, if links are not found in the page
            except NoSuchElementException as e:
                logging.warning(
                    "MonacolegendSpider; msg=Could not find Lot Url links.")

            # any other generic exceptions
            except Exception as e:
                logging.exception(
                    "Exception occured while trying to collect lot urls.")

            total_lots = int(last_lot_number)
            logging.warning(
                "MonacolegendSpider; msg=Loading Complete. Found %d lots. url= %s", total_lots, source_url)

            date_and_location = self.browser.find_element(
                By.XPATH, '/html/body/main/section[1]/div/div/p').text

            # Extracting location using regular expression
            location_match = re.search(
                r'\|\s*([A-Za-z\s]+)', date_and_location)
            if location_match:
                location = location_match.group(1).strip()
            else:
                location = None

            # Extracting and formatting date using regular expression
            date_and_location_list = date_and_location.split(" ")

            day = date_and_location_list[0]
            month_match = date_and_location_list[3]
            month = datetime.strptime(month_match, '%B').strftime('%b')
            year = date_and_location_list[4]

            date = f"{month} {day},{year}"

            for i in range(total_lots):
                yield scrapy.Request("https://www.google.com", dont_filter=True, callback=self.parseBS, meta={'url': source_url + "/lot-" + str(int(i) + 1), 'browser': self.browser, 'source_url': source_url, 'date': date, 'location': location, 'lots': total_lots, 'lot_number': str(i + 1)})

        except Exception as e:
            item = WatchItem()
            item['status'] = "Failed"
            logging.error(
                "MonacolegendSpider; msg=Crawling Failed > %s;url=%s", str(e), source_url)
            logging.error("MonacolegendSpider; msg=Crawling Failed;url=%sError=%s",
                          traceback.format_exc(), source_url)
            yield item

    def parseBS(self, response):
        url = response.meta.get('url')
        browser = response.meta.get('browser')
        source_url = response.meta.get('source_url')
        logging.warn(
            "MonacolegendSpider; msg=Crawling going to start;url= %s", url)
        item = WatchItem()
        try:
            browser.get(url)
            time.sleep(5)
            # 1 House Name
            item['house_name'] = 10

            # 2 Auction Name
            item['name'] = self.browser.find_element(
                By.XPATH, '/html/body/main/section/div/div[1]/h2/a/span[1]').text

            # 3 Date

            item['date'] = response.meta.get('date')

            # 4 Location
            item['location'] = response.meta.get('location')

            # 5 Lot

            item['lot'] = response.meta.get('lot_number')
            # 6 Images
            images = []
            try:
                parent_element = self.browser.find_element(
                    By.XPATH, '/html/body/main/section/div/div[2]')
                img_figure2 = parent_element.find_elements(
                    By.XPATH, './/figure')

                for div in img_figure2:
                    try:
                        a_tag = div.find_element(By.XPATH, './/a')
                        a_href = a_tag.get_attribute('href')
                        images.append(a_href)
                    except NoSuchElementException:
                        continue
            except NoSuchElementException:
                logging.warn(f'\n--- parent_element not found ----\n')

            item['images'] = images

            # 7 Title
            title = self.browser.find_element(
                By.XPATH, '/html/body/main/section/div/div[3]/h1').text

            item['title'] = title

            # 8 Description
            description = self.browser.find_element(
                By.XPATH, '/html/body/main/section/div/div[3]/p[2]').text

            item['description'] = description

            estimation = self.browser.find_element(
                By.XPATH, '/html/body/main/section/div/div[3]/p[1]').text

            if estimation is not None:
                # Split the estimation string by the colon ':' to separate the label from the value
                _, prices = estimation.split(':')

                min_price, max_price = prices.split('–')

                lot_currency = min_price.strip()[0]

                est_min_price = min_price.strip()[1:]
                est_max_price = max_price.strip()
            else:
                lot_currency = None
                est_min_price = None
                est_max_price = None

            # 9 Lot Currency
            item['lot_currency'] = lot_currency

            # 10 Est Min Price
            item['est_min_price'] = est_min_price.replace(",", "")

            # 11 Est Max Price
            item['est_max_price'] = est_max_price.replace(",", "")

            # 12 Sold Price

            try:
                sold_price_string = self.browser.find_element(
                    By.XPATH, '/html/body/main/section/div/div[3]/p[2]').text

                price_match = re.search(r'€\s*([\d,]+)', sold_price_string)
                if price_match:
                    sold_price = price_match.group(1).replace(',', '')
                else:
                    sold_price = 0

            except:
                sold = 0

            if sold_price:
                sold_price = sold_price.replace(",", "")
                sold = 1
            else:
                sold = 0
            item['sold_price'] = sold_price

            item['sold'] = sold

            item['sold_price_dollar'] = None

            # 14  URL
            item['url'] = url
            item["status"] = "Success"
            logging.debug(
                "MonacolegendSpider; msg=Crawling Completed > %s;url= %s", item, url)
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "MonacolegendSpider; msg=Crawling Failed > %s;url= %s", str(e), url)
            logging.error(
                "MonacolegendSpider; msg=Crawling Failed;url= %s;Error=%s", url, traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = source_url
        item["job"] = self.job
        return item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MonacolegendSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened,
                                signal=signals.spider_opened)
        return spider

    # signal fired when spider first opens
    # used for creating a chrome browser instance
    def spider_opened(self, spider):
        logging.warning("Setting up resources...")
        self.browser = self.sel_configuration()

    # singal fired when spider closes
    # used for cleaning up resources
    def spider_closed(self, spider):
        logging.warning("Cleaning up resources...")
        self.browser.close()
