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


class PhillipsSpider(scrapy.Spider):
    name = "phillipsSpider"
    allowed_domains = ["www.phillips.com"]
    start_urls = ['https://www.phillips.com/auctions/auction/NY080119']

    def __init__(self, url='', job='', *args, **kwargs):
        super(PhillipsSpider, self).__init__(*args, **kwargs)
        # self.start_urls = url.split(",")
        print(f'\n\n\n--------- 1. start_urls:: {self.start_urls} -------\n\n')
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        # setup = Setup.objects.first()
        # SELENIUM_CHROMEDRIVER_PATH = setup.chromedriver
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('headless')
        browser = webdriver.Chrome(options=options)
        browser.set_window_size(1440, 900)
        return browser

    def start_requests(self):
        print(f'\n\n\n---------2. start_urls:: {self.start_urls} -------\n\n')

        self.browser = self.sel_configuration()
        print(f'\n\n\n---------3. self.sel_configuration() -------\n\n')

        self.browser.get(self.start_urls[0])
        print(f'\n-- 4. self.browser.get({self.start_urls[0]})---')

        time.sleep(10)
        self.browser.find_element(
            By.XPATH, '/html/body/div[1]/header/nav/ul[2]/li/button').click()

        time.sleep(5)
        redirected_url = self.browser.current_url

        self.login(redirected_url)
        print("Redirected URL:", redirected_url)

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

# ====================================
    def parse(self, response):
        print(f'\n\n------- Inside parse::: --------- \n\n')
        print(f'\n\n\n---------5. start_urls:: {response.url} -------\n\n')

        logging.warn(
            "PhillipsSpider; msg=Spider started;url= %s", response.url)
        self.browser.get(response.url)
        time.sleep(10)
        number_of_lots = self.browser.find_element(By.XPATH,
                                                   '/html/body/div[2]/div/div[2]/div/div/div/div[2]/header/nav/div[1]').text

        all_lots = re.search(r'\d+', number_of_lots).group()

        print(f'\n\n\n---------6. all_lots:: {all_lots} -------\n\n')

        auction_details = response.xpath('//div[@class="auction-details"]')
        print(f'\nauction_details:: {auction_details}\n')
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
            select_element = self.browser.find_element(
                By.XPATH, '/html/body/div[2]/div/div[2]/div/div/div/div[2]/header/nav/div[2]/select')

            options = select_element.find_elements(By.TAG_NAME, "option")
            url_info = [option.get_attribute(
                "value") for option in options if option.get_attribute("value")]

            print(f'\n\n-- url_info:: {url_info} --\n')
            if select_element:
                for url in url_info:
                    yield scrapy.Request(url, callback=self.parse_details, meta={'lot': lot, 'name': name, 'date': date, 'location': location, 'base_url': url_info[0], 'auction_url': response.url, 'lots': total_lots})

    def parse_details(self, response):
        print(f'\n\n------- Inside parse_details::: --------- \n\n')
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

            # desc = lot.xpath('a/p/span/text()').extract()

            # 6 Images
            auction_code = base_url.rsplit('/', 1)
            image_url = response.xpath(
                "//meta[@property='og:image']/@content").extract()
            item["images"] = image_url[0]

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
            item["title"] = title[0]

            # 8 Description
            description = ""

            short_desc = response.xpath(
                "//meta[@name='description']/@content").extract_first()
            description = description + "\n"
            desc = response.xpath(
                '//ul[@class="lot-page__details__list"]/li[1]/p').extract() or None
            if desc is None:

                desc = response.xpath(
                    '/html/body/div[2]/div/div[2]/div/div[1]/div[3]/ul/li[2]/p').extract()
            print(f'\n------ desc:: {desc[0]} ---\n')

            description = description + desc[0]
            essay_info = response.xpath(
                '//div[@class="lot-essay"]/p/text()').extract()
            print(f'\n------ essay_info:: {essay_info} ---\n')
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
            sold_price = sold = 0
            sold_price_info = response.xpath(
                '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[5]/text()').extract() or None
            if sold_price_info is None:
                sold_price_info = response.xpath(
                    '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[3]/text()').extract()
            
            # 12 Sold Price
            if sold_price:
                lot_currency = sold_price_info[1]
                item["sold_price"] = sold_price_info[2]

                item["lot_currency"] = lot_currency
            else:
                item['sold_price'] = 0
                item['lot_currency'] = ""
            print("\n----2. Sold Price:", sold)
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

    def login(self, redirected_url):
        print(f'\n--- inside login ---\n')
        print(f'\nredirected_url:: {redirected_url}\n')
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
            print(f"\n\n----- login successful -----\n\n\n")
        except Exception as e:
            logging.error(
                "PhillipsSpider; msg=Login Failed > %s;url= %s", str(e), login_url)
            logging.error(
                "PhillipsSpider; msg=Login Failed;url= %s;Error=%s", login_url, traceback.format_exc())

        return True
# itsmeyoursujan@gmail.com
# Phillips@123
