import scrapy
import re
import logging
import traceback
from datetime import datetime
import re
from watchscrapy.items import WatchItem
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class PhillipsSpider(scrapy.Spider):
    name = "phillipsSpider"
    allowed_domains = ["www.phillips.com"]
    # start_urls = ['https://www.phillips.com/auctions/auction/NY080119']

    def __init__(self, url='', job='', *args, **kwargs):
        super(PhillipsSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        print(f'\n\n\n--------- 1. start_urls:: {self.start_urls} -------\n\n')
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('headless')
        browser = webdriver.Chrome(options=options)
        browser.set_window_size(1440, 900)
        return browser

    def start_requests(self):
        self.browser = self.sel_configuration()
        self.browser.get(self.start_urls[0])
        time.sleep(10)
        self.browser.find_element(
            By.XPATH, '/html/body/div[1]/header/nav/ul[2]/li/button').click()

        time.sleep(5)
        redirected_url = self.browser.current_url

        self.login(redirected_url)

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

# ====================================
    def parse(self, response):
        
        logging.warn(
            "PhillipsSpider; msg=Spider started;url= %s", response.url)
        self.browser.get(response.url)
        time.sleep(10)
        number_of_lots = self.browser.find_element(By.XPATH,
                                                   '/html/body/div[2]/div/div[2]/div/div/div/div[2]/header/nav/div[1]').text

        all_lots = re.search(r'\d+', number_of_lots).group()

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

        date_info = date_location[1].split(" ")
        date_str = date_info[-3] + " " + date_info[-2] + " " + date_info[-1]

        date = datetime.strptime(
            date_str.strip(), '%d %B %Y').strftime('%b %d,%Y')

        # 4 Location
        location = date_location[0].strip()

        for lot in all_lots:
            select_element = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div/div[2]/div/div/div/div[2]/header/nav/div[2]/select')

            options = select_element.find_elements(By.TAG_NAME, "option")
            url_info = [option.get_attribute(
                "value") for option in options if option.get_attribute("value")]

            if select_element:
                for url in url_info:
                    yield scrapy.Request(url, callback=self.parse_details, meta={'lot': lot, 'name': name, 'date': date, 'location': location, 'base_url': url_info[0], 'auction_url': response.url, 'lots': total_lots})

    def parse_details(self, response):
        self.browser.get(response.url)
        time.sleep(5)
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
            print(f'\n\n ---- lot_number_info:: {lot_number_info} --\n\n')
            lot_number = re.findall(r'\d+', lot_number_info)[0]
            item["lot"] = lot_number
            title = response.xpath(
                '//h1[@class="lot-page__lot__maker__name"]/text()').extract()

            # 6 Images

            try:
                parent_element = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div')

                div_elements = parent_element.find_elements(
                    By.XPATH, './/div')
                images = []

                # Iterate over each div element to find the 'a' tag and extract href attribute
                for div in div_elements:
                    try:
                        inner_div = div.find_element(By.XPATH, './/div')
                        img = inner_div.find_element(By.XPATH, './/img')
                        img_src = img.get_attribute('src')
                        images.append(img_src)

                    except NoSuchElementException:
                        continue
            except NoSuchElementException:
                logging.warn(f'\n--- parent_element not found ----\n')

            item["images"] = images

            item["title"] = title[0]

            # 8 Description
            description = ""
            
            description = description + "\n"
            desc = response.xpath(
                '//ul[@class="lot-page__details__list"]/li[1]/p').extract() or None
            if desc is None:

                desc = response.xpath(
                    '/html/body/div[2]/div/div[2]/div/div[1]/div[3]/ul/li[2]/p').extract()
            

            description = description + desc[0]
            essay_info = response.xpath(
                '//div[@class="lot-essay"]/p/text()').extract()
            
            essay = ""
            for para in essay_info:
                essay = essay + para
            description = description + "\n" + essay
            # soup = BeautifulSoup(html_content, 'html.parser')

            item["description"] = description

            # 10 Estimate Min Price
            # 11 Estimate Max Price
            est_min_price = est_max_price = 0
            estimation = response.xpath(
                '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[2]/text()').extract() or None

            if estimation is None and estimation[0] != '$':
                estimation = response.xpath(
                    '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[4]/text()').extract()
            est_min_price = estimation[1]
            est_max_price = estimation[3]
            
            item["est_min_price"] = est_min_price
            item["est_max_price"] = est_max_price

            # 9 Lot Currency
            sold = 0
            sold_price_info = response.xpath(
                '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[3]/text()').extract() or None
            if sold_price_info is None:
                sold_price_info = response.xpath(
                    '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[5]/text()').extract()
            # 12 Sold Price
            if sold_price_info:
                lot_currency = sold_price_info[1]
                sold_price_without_comma = sold_price_info[2].replace(',', '')
                item["sold_price"] = sold_price_without_comma

                item["lot_currency"] = lot_currency
                sold = 1
            else:
                item['sold_price'] = 0
                item['lot_currency'] = ""
            item["sold"] = sold
            # 13 Sold Price Dollar

            item["sold_price_dollar"] = None

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

    def login(self, redirected_url):
        login_url = redirected_url
        time.sleep(2)
        try:
            self.browser.get(login_url)
            time.sleep(3)

            username = self.browser.find_element(By.XPATH, '//*[@id=":r1:"]')
            username.send_keys('itsmeyoursujan@gmail.com')
            password = self.browser.find_element(By.XPATH, '//*[@id=":r2:"]')
            password.send_keys('Phillips@123')

            time.sleep(5)
            # login button
            self.browser.find_element(
                By.XPATH, '//*[@id=":r3:"]').click()
            time.sleep(5)
            logging.info(f"\n----- login successful -----\n")
        except Exception as e:
            logging.error(
                "PhillipsSpider; msg=Login Failed > %s;url= %s", str(e), login_url)
            logging.error(
                "PhillipsSpider; msg=Login Failed;url= %s;Error=%s", login_url, traceback.format_exc())

        return True
# itsmeyoursujan@gmail.com
# Phillips@123
