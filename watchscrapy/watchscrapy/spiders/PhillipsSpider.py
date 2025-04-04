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
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class PhillipsSpider(scrapy.Spider):
    name = "phillipsSpider"
    allowed_domains = ["www.phillips.com"]
    # start_urls = ['https://www.phillips.com/auctions/auction/NY080119']
    # https://www.phillips.com/auctions/auction/HK090321

    def __init__(self, url='', job='', *args, **kwargs):
        super(PhillipsSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        if not DEBUG:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

            # Setup the WebDriver using webdriver_manager and pass the options
            service = Service(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service, options=options)
            return browser
        else:
            # browser = webdriver.Chrome(options=options)
            # return browser
            options = Options()
            # options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

            # Setup the WebDriver using webdriver_manager and pass the options
            service = Service(ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service, options=options)
            return browser

    def start_requests(self):
        self.browser = self.sel_configuration()
        self.browser.get(self.start_urls[0])
        time.sleep(5)
        # accept cookies
        try:
            accept_cookies = self.browser.find_element(
                By.XPATH, '/html/body/div[4]/div[2]/div/div[1]/div/div[2]/div/button[3]')
            accept_cookies.click()
        except Exception as e:
            logging.warn(f"\n Exceptionn :: {e} -\n")

        self.browser.find_element(
            By.XPATH, '/html/body/div[1]/header/div[1]/div[2]/button').click()

        time.sleep(10)
        redirected_url = self.browser.current_url
        time.sleep(5)

        self.login(redirected_url)        
        time.sleep(10)
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

# ====================================
    def parse(self, response):
        item = WatchItem()

        logging.warn(
            "PhillipsSpider; msg=Spider started;url= %s", response.url)

        time.sleep(10)
        try:

            number_of_lots = self.browser.find_element(By.XPATH,
                                                       '/html/body/div[2]/div/div[2]/div/div/div/div[2]/header/nav/div[1]').text
            # number_of_lots = self.browser.find_element(By.XPATH,
            #                                            '/html/body/div[2]/div/div/div[2]/div/div/div/div[2]/header/nav/div[1]').text
            logging.warn(f'\n--number_of_lots:: {number_of_lots} ---\n')
            all_lots = re.search(r'\d+', number_of_lots).group()

            # auction_details = response.xpath('//div[@class="auction-details"]')
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
            date_str = date_info[-3] + " " + \
                date_info[-2] + " " + date_info[-1]

            date = datetime.strptime(
                date_str.strip(), '%d %B %Y').strftime('%b %d,%Y')
            # 4 Location
            location = date_location[0].strip()
            time.sleep(5)
            wait = WebDriverWait(self.browser, 10)
            try:
                parent_element_ul = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '/html/body/div[2]/div/div[2]/div/div/div/div[2]/ul'))
                )
            except Exception as e:
                logging.warn(f"\n Exceptionn :: {e} -\n")
            all_lis = parent_element_ul.find_elements(By.XPATH, './/li')

            lots_urls = []
            for i in all_lis:
                div_elem = i.find_element(By.XPATH, './/div')
                try:
                    a_tag = div_elem.find_element(By.XPATH, './/a')
                except NoSuchElementException:
                    continue

                href_value = a_tag.get_attribute('href')
                lots_urls.append(href_value)

            for url in lots_urls:
                yield scrapy.Request(url, callback=self.parse_details, meta={'name': name, 'date': date, 'location': location, 'auction_url': response.url, 'lots': total_lots})
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), url)
            logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())

    def parse_details(self, response):
        self.browser.get(response.url)
        time.sleep(5)
        item = WatchItem()
        try:

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
            try:
                title1 = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/div[1]/a/h1').text
                title2 = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/h1').text
                item["title"] = f'{title1} \n{title2}'
            except NoSuchElementException:
                title2 = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/h1').text
                item["title"] = title2
            # 6 Images

            try:
                images = []
                active_image = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/img')
                active_image_src = active_image.get_attribute('src')
                images.append(active_image_src)
                parent_element = self.browser.find_element(
                    By.XPATH, '/html/body/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div')

                div_elements = parent_element.find_elements(
                    By.XPATH, './/div')
                # Iterate over each div element to find the 'a' tag and extract href attribute
                for div in div_elements:
                    try:
                        inner_div = div.find_element(By.XPATH, './/div')
                        img = inner_div.find_element(By.XPATH, './/img')
                        img_src = img.get_attribute('src')
                        if img_src not in images:
                            images.append(img_src)

                    except NoSuchElementException:
                        continue
            except NoSuchElementException:
                logging.warn(f'\n--- parent_element not found ----\n')
            item["images"] = images

            # 8 Description
            description = ""

            # description = description + "\n"
            # desc = ""
            try:
                description += self.find_element_with_multiple_xpaths(self.browser, [
                    '/html/body/div[2]/div/div[2]/div/div[1]/div[3]/ul/li[2]/p',
                    '/html/body/div[2]/div/div[2]/div/div[1]/div[3]/ul/li[1]/p',
                ])
            except Exception as e:
                logging.warn(f"Cannot get description for url: {response.url}")

            essay_info = response.xpath(
                '//div[@class="lot-essay"]/p/text()').extract()

            essay = ""
            for para in essay_info:
                essay = essay + para
            description = description + "\n" + essay

            item["description"] = description

            est_min_price = est_max_price = 0
            try:
                estimation = self.get_estimation()
            except NoSuchElementException as e:
                logging.warn(f"Error:::: {e} -- for url: {response.url} --\n")
            if estimation:
                # Define regex pattern to match numbers with optional currency symbols
                pattern = r'[\$€£¥]?([\d,]+)[\s-]*([\d,]+)'

                # Initialize variables to store min and max prices
                est_min_price = "0"
                est_max_price = "0"

                # Search for matches in the estimation string
                matches = re.findall(pattern, estimation)

                # Process the first match found (assuming first line is what we need)
                if matches:
                    est_min_price = matches[0][0].replace(',', '')
                    est_max_price = matches[0][1].replace(',', '')

                item["est_min_price"] = est_min_price
                item["est_max_price"] = est_max_price

            # 9 Lot Currency
            sold = 0
            try:
                sold_price_info = response.xpath(
                    '/html/body/div[2]/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[3]/text()').extract()

            except NoSuchElementException:
                sold_price_info = response.xpath(
                    '/html/body/div[2]/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[5]/text()').extract()
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
                sold = 0
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
            time.sleep(3)

            username = self.browser.find_element(By.XPATH, '//*[@id=":r1:"]')
            username.send_keys('itsmeyoursujan@gmail.com')
            password = self.browser.find_element(By.XPATH, '//*[@id=":r2:"]')
            password.send_keys('Phillips@123')

            time.sleep(5)
            # login button
            wait = WebDriverWait(self.browser, 10)

            # self.browser.find_element(
            #     By.XPATH, '//*[@id=":r3:"]').click()
            login_button = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id=":r3:"]'))
            )
            login_button.click()
            time.sleep(15)
            logging.info(f"\n----- login successful -----\n")
        except Exception as e:
            logging.error(
                "PhillipsSpider; msg=Login Failed > %s;url= %s", str(e), login_url)
            logging.error(
                "PhillipsSpider; msg=Login Failed;url= %s;Error=%s", login_url, traceback.format_exc())

        return True
# itsmeyoursujan@gmail.com
# Phillips@123

    def find_element_with_multiple_xpaths(self, browser, xpaths):
        """
        Tries to find an element using multiple XPaths.

        Args:
            browser: The WebDriver instance.
            xpaths: A list of XPaths to try.

        Returns:
            The found element or None if none of the XPaths work.
        """
        wait = WebDriverWait(browser, 10)
        for xpath in xpaths:
            try:
                # elem = browser.find_element(By.XPATH, xpath)
                element = wait.until(
                    EC.visibility_of_element_located(
                        (By.XPATH, xpath))
                )
                if element:
                    desc_text = element.text.strip()
                    if desc_text:
                        return desc_text

            except Exception:
                continue
        return None

    def get_estimation(self):
        xpaths = [
            '/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[2]',
            '/html/body/div[2]/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[2]',
            '/html/body/div[2]/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/p[4]'
        ]

        for xpath in xpaths:
            try:
                estimation = self.browser.find_element(By.XPATH, xpath).text
                if estimation:
                    return estimation
            except NoSuchElementException:
                continue  # Try the next XPath
        return None
