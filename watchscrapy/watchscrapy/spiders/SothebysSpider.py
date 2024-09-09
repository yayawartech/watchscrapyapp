import re
import time
import json
import scrapy
import logging
import traceback
from scrapy import signals
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from WatchInfo.settings import DEBUG
from watchscrapy.items import WatchItem
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SothebysSpider(scrapy.Spider):
    name = "sothebysSpider"
    allowed_domains = ["www.sothebys.com"]

    def __init__(self, url='', job='', *args, **kwargs):
        super(SothebysSpider, self).__init__(*args, **kwargs)
        # self.start_urls = [
        # 'https://www.sothebys.com/en/buy/auction/2024/fine-watches-3']
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
                "SothebysSpider; msg=Spider started; url= %s", source_url)
            # use set to avoid duplicates
            lots_urls = set()
            time.sleep(4)

            self.browser.get(response.url)
            time.sleep(4)

            logging.warning(
                "SothebysSpider; msg=Trying to load lots in next pages; url= %s", source_url)
            try:
                accept_cookie = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[4]/div[2]/div/div[1]/div/div[2]/div/button[2]'))
                )
                accept_cookie.click()
                logging.warn("---- Cookie accepted----")
                time.sleep(5)
            except NoSuchElementException:
                logging.warn("---- Cookie not accepted----")
                time.sleep(5)
            while True:

                # Accept Cookie popup
                try:
                    lot_number = self.browser.find_element(
                        By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/span/div[4]/p[1]').text
                    # Use regular expression to extract numeric value
                    match = re.search(r'\d+', lot_number)

                    # Extract the matched numeric value
                    if match:
                        extracted_number = int(match.group())
                        lot_number = extracted_number
                    else:
                        logging.warn("No numeric value found in the string")

                    # Find the parent element by XPath
                    parent_element = self.browser.find_element(
                        By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div[1]')

                    # Find all div elements inside the parent
                    div_elements = parent_element.find_elements(
                        By.XPATH, './/div')

                    # Iterate over each div element to find the 'a' tag and extract href attribute
                    for div in div_elements:
                        try:
                            # Find 'a' tag inside the div
                            a_tag = div.find_element(By.XPATH, './/a')

                            # Get the href attribute value
                            href_value = a_tag.get_attribute('href')
                            lots_urls.add(href_value)
                        except NoSuchElementException:
                            # If 'a' tag is not found in the div, skip it
                            continue
                    

                    # waiting for Next button to be available for 10 seconds.
                    try:
                        next_button = WebDriverWait(self.browser, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div[2]/nav/ul/li[6]/button'))
                        )
                    except Exception:
                        next_button = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
                            (By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div[2]/nav/ul/li[5]/button'))
                        )

                    # if next_button is not enabled, it means we reached to the last page.
                    if not next_button.is_enabled():
                        break
                    else:
                        next_button.click()
                        time.sleep(5)
                # raised by WebDriverWait if next button not found on the page.
                except TimeoutException as e:
                    logging.warning(
                        "SothebysSpider; msg=Did not found next button on the page. Assuming there is only one page. url=%s", source_url)
                    break
                # raised by browser.find_elements_by_css_selector, if links are not found in the page
                except NoSuchElementException as e:
                    logging.warning(
                        "SothebysSpider; msg=Could not find Lot Url links.")
                    break
                # any other generic exceptions
                except Exception as e:
                    logging.exception(
                        "Exception occured while trying to collect lot urls.")
                    break

            total_lots = len(lots_urls)
            logging.warning(
                "SothebysSpider; msg=Loading Complete. Found %d lots. url= %s", total_lots, source_url)

            page_source = self.browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            script = soup.find(
                'script', {'type': 'application/ld+json'}).string
            pre_data = json.loads(script)

            try:
                date = pre_data['@graph'][0]['startDate'].split("T")[0]
            except:
                date = pre_data['@graph'][0]['endDate'].split("T")[0]
            location = pre_data['@graph'][0]['location']['name']

            for i, url in enumerate(lots_urls):
                yield scrapy.Request(url, dont_filter=True, callback=self.parseBS, meta={'url': url, 'browser': self.browser, 'source_url': source_url, 'date': date, 'location': location, 'lots': total_lots})
                # break

        except Exception as e:
            item = WatchItem()
            item['status'] = "Failed"
            logging.error(
                "SothebysSpider; msg=Crawling Failed > %s;url=%s", str(e), source_url)
            logging.error("SothebysSpider; msg=Crawling Failed;url=%sError=%s",
                          traceback.format_exc(), source_url)
            yield item

    def parseBS(self, response):
        url = response.meta.get('url')
        browser = response.meta.get('browser')
        source_url = response.meta.get('source_url')
        logging.warn(
            "SothebysSpider; msg=Crawling going to start;url= %s", url)
        item = WatchItem()
        try:
            browser.get(url)
            time.sleep(5)
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # 1 House Name
            item['house_name'] = 9

            # 3 Date
            item['date'] = datetime.strptime(response.meta.get(
                'date'), '%Y-%m-%d').strftime('%b %d,%Y')

            # 4 Location
            item['location'] = response.meta.get('location')

            # 5 Lot
            lot_number_info = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[2]/div[1]/nav/p[2]').text

            # lot_number_list = re.findall(r'\d{4}', lot_number_info)
            lot_number_list = re.findall(r'Lot\s*(\d+)', lot_number_info)

            lot_number = lot_number_list[0] if lot_number_list else None

            item['lot'] = lot_number

            # logging.warn("====>lot : " + item['lot'])
            # 6 Images
            try:
                # Find the parent element by XPath
                parent_element = browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[5]/div[1]/div[1]/div/div')

                # Find all div elements inside the parent
                div_elements = parent_element.find_elements(
                    By.XPATH, './/div')

                images = []

                # Iterate over each div element to find the 'a' tag and extract href attribute
                for div in div_elements:
                    try:
                        button = div.find_element(By.XPATH, './/button')
                        div_ = button.find_element(By.XPATH, './/div')
                        img = div_.find_element(By.XPATH, './/img')
                        img_src = img.get_attribute('src')
                        images.append(img_src)

                    except NoSuchElementException:
                        continue
            except NoSuchElementException:
                logging.warn('\n--- parent_element not found ----\n')

            item['images'] = images

            # 7 Title
            try:
                auction_name = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[6]/div/div[2]/div[1]/div[1]/div/h1').text
                title = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[6]/div/div[2]/div[1]/div[1]/div/p').text.strip()
                if title.upper() == "OFFERED WITHOUT RESERVE":
                    raise ValueError(
                        "Title is 'Offered Without Reserve', aborting.")

            except Exception as e:
                full_title = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[6]/div/div[2]/div[1]/div[1]/div/h1').text
                title = full_title.strip()
                auction_name = full_title.split(" | ")[0].strip()
            item['name'] = auction_name
            item['title'] = title

            # 8 Description
            description = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[7]/div[3]').text

            item['description'] = description

            estimation = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div/div/div[4]/div/div[6]/div/div[2]/div[2]/div/div/div[2]/p[2]').text

            if estimation is not None:
                # Split the estimation string by space
                parts = estimation.split()

                # Extracting the minimum and maximum prices
                est_min_price = parts[0]
                est_max_price = parts[2]
                lot_currency = parts[3]
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
            sold = 0
            try:
                parent_sold_price = soup.find(
                    text=re.compile('^Lot sold:')).parent.parent
                sold_price_info = parent_sold_price.findChildren()[1]
                sold_price = sold_price_info.text
                if sold_price is not None:
                    sold_price = sold_price.replace(',', '')
                    sold = 1
                else:
                    sold_price = 0
                item['sold_price'] = sold_price
            except:
                sold_price_info = 0
                item['sold_price'] = 0

            item['sold'] = sold
            item['sold_price_dollar'] = None

            # 14  URL
            item['url'] = url
            item["status"] = "Success"
            logging.debug(
                "SothebysSpider; msg=Crawling Completed > %s;url= %s", item, url)
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "SothebysSpider; msg=Crawling Failed > %s;url= %s", str(e), url)
            logging.error(
                "SothebysSpider; msg=Crawling Failed;url= %s;Error=%s", url, traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = source_url
        item["job"] = self.job
        return item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SothebysSpider, cls).from_crawler(
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
