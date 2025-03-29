# -*- coding: utf-8 -*-
import re
import time
import scrapy
import logging
import traceback
from datetime import datetime
from selenium import webdriver
from WatchInfo.settings import DEBUG
from watchscrapy.items import WatchItem
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException


class ArtcurialSpider(scrapy.Spider):
    name = "artcurialSpider"
    allowed_domains = ["www.artcurial.com"]
    # start_urls = [
    #     'https://www.artcurial.com/en/sales/vente-fr-3484-modern-vintage-watches-online']
    # https://www.artcurial.com/en/sales/vente-mc-70-le-temps-est-feminin

    def __init__(self, url='', job='', *args, **kwargs):
        super(ArtcurialSpider, self).__init__(*args, **kwargs)
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
        self.login(self.browser)
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"browser": self.browser})

    def parse(self, response):
        logging.warn(
            "ArtcurialSpider; msg=Spider started;url= %s", response.url)
        browser = response.meta.get('browser')
        try:
            browser.get(response.url)

            time.sleep(20)

            name = browser.find_element(By.XPATH,
                                        '/html/body/div/div/div/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[1]/div/div/div/h1').text
            # 3
            try:
                date_string = browser.find_element(By.XPATH,
                                                   '//*[@id="app"]/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/div[2]/div/a/span').text
            except NoSuchElementException:
                date_string = browser.find_element(
                    By.XPATH, '/html/body/div/div/div/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/div/a/span').text
            full_date_and_time = date_string.split(" at ")
            full_date = full_date_and_time[0]

            partial_date = datetime.strptime(full_date, '%B %d, %Y')
            date = partial_date.strftime('%b %d,%Y')

            # 4
            location = "Online"
            auction_url = response.url

            all_lots_elements = browser.find_elements(
                By.XPATH, '//*[@id="app"]/div/main/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[2]/td[1]/h5')
            # Extracting text content from each element in the list
            all_lots = [element.text for element in all_lots_elements]
            all_lots = int(all_lots[0].split()[0])

            total_lots = all_lots

            logging.warn("ArtcurialSpider; msg=Total Lots: %s;url= %s",
                         all_lots, response.url)

            button_xpath = '/html/body/div/div/div/div/main/div/div[1]/div/div[2]/div/div/div/div/div/div[2]/div[1]/button'

            while True:
                try:
                    # Wait for the element to be present in the DOM
                    more_button = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, button_xpath))
                    )

                    # Check if the button is disabled by checking its 'disabled' attribute
                    is_disabled = more_button.get_attribute(
                        'disabled') is not None

                    if is_disabled:
                        logging.warn(
                            "More button is disabled, breaking the loop.")
                        break
                    else:
                        logging.warn("More button is enabled, clicking it.")
                        more_button.click()
                        time.sleep(5)  # Wait 5 seconds before the next attempt

                except EC.NoSuchElementException:
                    # If the button is not found, break the loop
                    logging.warn("More button not found, breaking the loop.")
                    break
                except Exception as e:
                    # Handle any other exceptions
                    logging.warn(f"An unexpected exception occurred: {e}")
                    break

            elem = '/html/body/div/div/div/div/main/div/div[1]/div/div[2]/div/div/div/div/div/div[1]'
            logging.warn(f'\n--- total_lots:: {total_lots} ---\n')

            all_urls = []
            try:
                for i in range(1, total_lots+1):
                    my_new_elem = f'{elem}/div[{i}]'
                    elem1 = browser.find_element(By.XPATH, my_new_elem)

                    a_tag = elem1.find_element(By.XPATH, './/a')
                    my_new_url = a_tag.get_attribute("href")
                    logging.warn(f'\n-- my_new_url:: {my_new_url} --\n')

                    all_urls.append(my_new_url)
                    lot_number = my_new_url.split('/')[-1]

                items = {'name': name, 'date': date, 'location': location,
                         'lot_number': lot_number, 'auction_url': auction_url, 'lots': total_lots, 'browser': browser}
                for new_url in all_urls:
                    yield scrapy.Request(new_url, callback=self.parse_url, meta=items)
            except NoSuchElementException:
                logging.warn(f'\n-- element not found --\n')
            except StaleElementReferenceException:
                logging.warn("\n--- StaleElementReferenceException ---\n")

        except Exception as e:
            item = WatchItem()
            item['url'] = response.url
            item['status'] = "Failed"
            logging.error(
                "ArtcurialSpider; msg=Crawling Failed > %s;url= %s", str(e), auction_url)
            logging.error("ArtcurialSpider; msg=Crawling Failed;url= %s;Error=%s",
                          auction_url, traceback.format_exc())
            yield item

    def parse_url(self, response):
        logging.warn(f"\nInside parse_url with url:: {response.url}\n")
        browser = response.meta.get("browser")
        item = WatchItem()
        try:
            # 1 HouseName
            house_name = 2
            item["house_name"] = house_name

            # 2 Name
            name = response.meta.get("name")
            item["name"] = name

            # 3 Date
            date = response.meta.get("date")
            item['date'] = date
            # item["date"] = datetime.strptime(
            # date.strip(), '%d %B %Y').strftime('%b %d,%Y')

            # 4 Location
            location = response.meta.get("location")
            item["location"] = location

            # 5 Lot Number
            lot_number = response.meta.get("lot_number")

            item["lot"] = re.findall(r'\d+', str(lot_number))[0]
            browser.get(response.url)
            time.sleep(10)
            try:
                parent_element = WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/main/div/section/div[1]/div[2]/div[1]/section/section/div/ul')))
                child_elements = parent_element.find_elements(
                    By.XPATH, './/li')
                images = []

                url_pattern = r'url\("([^"]+)"\)'

                for li in child_elements:
                    try:
                        div_1 = li.find_element(By.XPATH, './/div')
                        div_list = div_1.find_elements(By.XPATH, './/div')

                        for i in div_list:
                            try:
                                image_url_style = i.get_attribute('style')

                                match = re.search(
                                    url_pattern, image_url_style)
                                if match:
                                    url = match.group(1)
                                    img_url = url.split("?")

                                    images.append(img_url[0])

                            except NoSuchElementException:
                                continue
                    except NoSuchElementException:
                        continue
                logging.warn(
                    f'\nimage:: {images} -- from url:: {response.url} --\n')
                item["images"] = images
            except NoSuchElementException:
                logging.error("Parent element not found")
                return
            title = browser.find_elements(
                By.XPATH, '/html/body/div/div/div/div/main/div/section/div[1]/div[2]/div[3]/div/div[1]/div/div[2]/div[1]/div/h4')

            title = [element.text for element in title]
            item["title"] = "".join(title)

            # 8 Description
            description = browser.find_elements(
                By.XPATH, '//*[@id="app"]/div/main/div/section/div[1]/div[2]/div[2]/div[2]/div/div/div')
            description = [element.text for element in description]
            description = " ".join(description)

            # Remove all single quotes
            text_without_single_quotes = description.replace("'", "")

            # Remove all double quotes
            text_without_quotes = text_without_single_quotes.replace(
                '"', '')
            item["description"] = text_without_quotes

            estimation_info = browser.find_elements(
                By.XPATH, '//*[@id="app"]/div/main/div/section/div[1]/div[2]/div[3]/div/div[1]/div/div[2]/div[2]/span')
            estimation_info = [element.text for element in estimation_info]
            # 9 Lot Currency
            # Assuming the currency symbols are €, $, or £
            pattern = r'Estimation : (\d{1,3}(?:\s\d{3})*)\s*€\s*-\s*(\d{1,3}(?:\s\d{3})*)\s*€'

            # Initialize variables to store extracted information
            est_min_price = 0
            est_max_price = 0
            lot_currency = None

            # Extracting information from each estimation info
            for info in estimation_info:
                match = re.search(pattern, info)
                if match:
                    # Extract estimated min and max prices and the currency
                    est_min_price = match.group(1).replace(' ', '')
                    est_max_price = match.group(2).replace(' ', '')
                    # lot_currency = match.group(3)

            item["est_min_price"] = est_min_price

            # 11 Est max Price
            item["est_max_price"] = est_max_price

            item["lot_currency"] = '€'
            # 12 sold
            sold_price = 0
            try:
                sold_price = browser.find_element(
                    By.XPATH, '/html/body/div/div/div/div/main/div/section/div[1]/div[2]/div[3]/div/div[1]/div/div[3]/div[1]/div/div/div').text
                # price = int(re.sub(r'\D', '', sold_price[0]))
                cleaned_price = sold_price.replace(
                    " ", "").replace("€", "")

                item['sold_price'] = int(cleaned_price)
                item['sold'] = 1
            except:
                item["sold"] = 0
                item["sold_price"] = 0

            # 14 sold_price_dollar
            item["sold_price_dollar"] = None

            # 15 url
            item["url"] = response.url
            item["status"] = "Success"
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ArtcurialSpider; msg=Crawling Failed > %s;url= %s", str(e), response.url)
            logging.error("ArtcurialSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = response.meta.get("auction_url")
        item["job"] = self.job
        yield item

    def login(self, browser):
        login_url = 'https://www.artcurial.com/en/login'
        try:
            browser.get(login_url)
            time.sleep(5)
            browser.find_element(
                By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div[1]/button').click()
            time.sleep(5)
            
            username = browser.find_element(By.XPATH, '//*[@id="username"]')
            username.send_keys('manjul@gmail.com')
            password = browser.find_element(By.XPATH, '//*[@id="password"]')
            password.send_keys('Artcurial@123')

            time.sleep(5)
            # login button
            browser.find_element(
                By.XPATH, '/html/body/div/main/section/div/div/div/form/div[2]/button').click()
            time.sleep(5)
            logging.info("\n----- login successful -----\n")
        except Exception as e:
            logging.error(
                "HeritageSpider; msg=Login Failed > %s;url= %s", str(e), login_url)
            logging.error(
                "HeritageSpider; msg=Login Failed;url= %s;Error=%s", login_url, traceback.format_exc())

        return True
