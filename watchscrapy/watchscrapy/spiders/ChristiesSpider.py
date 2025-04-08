import re
import time
import scrapy
import logging
import traceback
from scrapy import signals
from datetime import datetime
from selenium import webdriver
from scrapy.spiders import Spider
from WatchInfo.settings import DEBUG
from watchscrapy.items import WatchItem
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class ChristiesSpider(scrapy.Spider):
    name = "christiesSpider"
    allowed_domains = ["www.christies.com", "onlineonly.christies.com"]

    def __init__(self, url='', job='', *args, **kwargs):
        super(ChristiesSpider, self).__init__(*args, **kwargs)
        # self.start_urls = [
        # 'https://onlineonly.christies.com/s/watches-online-top-time/lots/3229']
        # https://www.christies.com/en/auction/only-watch-29184

        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        if not DEBUG:
            # options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

            # Setup the WebDriver using webdriver_manager and pass the options
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=options)
        browser.set_window_size(1920, 1080)
        return browser

    def start_requests(self):
        # time.sleep(5)
        self.browser = self.sel_configuration()
        print("Starting requests...")
        for url in self.start_urls:
            # url += "&loadall=true&page=2&sortby=LotNumber" if '?' in url else "?loadall=true&page=2&sortby=LotNumber"
            # url += "?loadall=true&page=2&sortby=LotNumber"
            print(f"\n----Requesting URL: {url}")
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("Parsing response...")
        url = response.url
        self.browser.get(response.url)
        time.sleep(5)

        # Accept Cookie popup
        print("Accepting cookies...")
        try:

            accept_cookie = self.find_element_with_multiple_xpaths(self.browser, [
                '/html/body/div[4]/div[2]/div/div/div[2]/div/div/button[2]',
            ])
            accept_cookie.click()
            logging.warn("---- Cookie accepted----")
            time.sleep(5)
        except Exception as e:
            logging.warn(f"--accept_cookie not found --\n")

        item = WatchItem()
        lots_urls = set()
        try:
            # 1 House Name
            time.sleep(5)
            # 2 Auction Name
            try:
                name = self.find_element_with_multiple_xpaths(self.browser, [
                    '/html/body/main/div/chr-auction-header-next/header/div/div[2]/div[1]/h1',
                    '/html/body/main/div[2]/chr-auction-header-next/header/div/div[2]/div[1]/h1',
                ])
                if name:
                    name = name.text
            except Exception as e:
                logging.warning(f"Error: {e} -- for url: {url} --\n")

            print(f"\n\n----Auction Name: {name}---\n\n")

            # 3 Date
            try:
                # Try to find the element containing the date (first XPath)
                date = self.browser.find_element(By.XPATH,
                                                 '/html/body/main/div/chr-auction-header-next/header/div/div[2]/div[1]/div/p/strong').text
                print(f"\n\n----Date: {date}---\n\n")

                # Check if the date is found and matches the regex pattern
                match = re.search(r'\d{2} [A-Z]{3} \d{4}', date)
                if match:
                    date_string = match.group()
                else:
                    print("Date format not found in the text")
                    date_string = None
            except NoSuchElementException:
                # If the first XPath doesn't work, fall back to the second one
                date = self.browser.find_element(
                    By.XPATH, '/html/body/main/div[2]/chr-auction-header-next/header/div/div[2]/div[1]/div/p/strong').text
                print(f"\n\n----Date (Fallback): {date}---\n\n")

                # Check if the date is found and matches the regex pattern
                match = re.search(r'\d{1,2} [A-Z]{3} \d{4}', date)  # Changed to \d{1,2} for one or two digits
                if match:
                    date_string = match.group()
                else:
                    print("Date format not found in the fallback text")
                    date_string = None

            # If we found a valid date string, convert it
            if date_string:
                # Convert the date string to a datetime object
                date_obj = datetime.strptime(date_string, '%d %b %Y')

                # Format the datetime object into the desired format
                formatted_date = date_obj.strftime('%b %d,%Y')
                print(f"Formatted Date: {formatted_date}")
            else:
                print("Failed to extract a valid date.")

            # 4 Location
            try:
                location = self.browser.find_element(
                    By.XPATH, '/html/body/div[1]/chr-auction-header-next/header/div/div[2]/div[2]/div/div/div/span').text
            except NoSuchElementException:
                location = self.browser.find_element(
                    By.XPATH, '/html/body/main/div[2]/chr-auction-header-next/header/div/div[2]/div[2]/div/div/div/span').text
            print(f"\n\n----Location: {location}---\n\n")
            # 5 Lot
            # Find the parent element by XPath
            try:
                parent_element = self.browser.find_element(
                    By.XPATH, '/html/body/div[1]/chr-auction-results-view/main/section/div/ul')
            except NoSuchElementException:
                parent_element = self.browser.find_element(
                    By.XPATH, '/html/body/main/chr-auction-results-view/main/section/div/ul')
            # Find all div elements inside the parent
            li_elements = parent_element.find_elements(
                By.XPATH, './/li')

            # Iterate over each div element to find the 'a' tag and extract href attribute
            for li in li_elements:
                try:
                    # Find 'a' tag inside the div
                    a_tag = li.find_element(
                        By.XPATH, './/chr-lot-tile/div[2]/div[2]/h2/a')
                    if a_tag:
                        # Get the href attribute value

                        href_value = a_tag.get_attribute('href')
                        lots_urls.add(href_value)

                except NoSuchElementException:
                    # If 'a' tag is not found in the div, skip it
                    continue
            time.sleep(5)

            lot_string_element = self.find_element_with_multiple_xpaths(self.browser, [
                '/html/body/div[1]/chr-page-nav/nav/div/ul/li[2]/a',
                '/html/body/main/nav/div/div[2]/ul/li[2]/a'
            ])

            # Execute JavaScript to get the text content
            lot_string_text = self.browser.execute_script(
                "return arguments[0].textContent;", lot_string_element)
            if lot_string_element is not None:

                match = re.search(r'\((\d+)\)', lot_string_text)
                if match:
                    lot_number = match.group(1)
                    lot = int(lot_number)
                else:
                    logging.warn("\n Number not found in the string.\n")
                    lot = None  # or some default value or handle the case where number is not found
            else:
                logging.warn("\n Element not found.\n")
                lot = None  # or handle the case where the element is not found

            time.sleep(5)
            print(f"\n\n----Lot Number: {len(lots_urls)}---\n\n")
            for url in lots_urls:
                yield scrapy.Request(url, dont_filter=True, callback=self.parseBS, meta={'url': url, 'browser': self.browser, 'date': formatted_date, 'name': name, 'location': location, 'lots': lot})
        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), url)
            logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                          response.url, traceback.format_exc())

    def parseBS(self, response):
        url = response.meta.get('url')

        logging.warn(
            "ChristiesSpider; msg=Crawling going to start;url= %s", url)
        item = WatchItem()
        item['name'] = response.meta.get('name')
        item['house_name'] = 5
        item['date'] = response.meta.get('date')
        item['location'] = response.meta.get('location')
        item['lot'] = response.meta.get('lots')
        try:
            self.browser.get(url)
            time.sleep(5)

            # 7 Title

            try:
                title = self.get_title()
                if title:
                    item['title'] = title
            except:
                item['title'] = None

            # 6 Images
            images = []
            try:
                time.sleep(5)
                click_more_button = self.find_element_with_multiple_xpaths(self.browser, [
                    '/html/body/main/div[2]/div/div/div[2]/div/div[1]/div/div/chr-lot-header-gallery-button/div',
                    '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[1]/div/div/chr-lot-header-gallery-button/div',
                ])
                if click_more_button is not None:
                    logging.warn(
                        f'\nclick_more_button found for url:: {url}\n')
                    try:
                        try:
                            self.browser.execute_script(
                                "arguments[0].scrollIntoView(true);", click_more_button)
                            self.browser.execute_script(
                                "arguments[0].click();", click_more_button)

                        except Exception:
                            logging.warn(f'\n--Cannot click more button: \n')

                        time.sleep(5)
                        # parent_element_ul activates when more button is clicked otherwise not
                        parent_element_ul = self.find_element_with_multiple_xpaths(self.browser, [
                            '/html/body/div[2]/chr-gallery-provider/chr-modal/div/div/div/div/chr-gallery/div[1]/ul',
                            '/html/body/div[5]/chr-gallery-provider/chr-modal/div/div/div/div/chr-gallery/div[1]/ul',
                            "/html/body/div[4]/chr-gallery-provider/chr-modal/div/div/div/div/chr-gallery/div[1]/ul"
                        ])

                        if parent_element_ul:

                            child_elem_li = parent_element_ul.find_elements(
                                By.XPATH, './/li')
                            img_elem = self.get_image_urls_from_elements(
                                child_elem_li)
                            images.extend(img_elem)
                    except NoSuchElementException as e:
                        logging.warn(
                            f'\n-- Error Occured:: {e} \n for url:: {url} \n')

                else:

                    active_image = self.find_element_with_multiple_xpaths(self.browser, [
                        '/html/body/main/div[2]/div/div/div[2]/div/div[2]/div/chr-lot-header-gallery-button/div/div/div/div/img',
                        '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[2]/div/chr-lot-header-gallery-button/div/div/chr-image/div/img',
                        '/html/body/div[2]/div[4]/div[1]/chr-lot-header/div/div[2]/div/div[2]/div/chr-lot-header-gallery-button/div/div/chr-image/div/img'
                    ])
                    if active_image:

                        img1 = active_image.get_attribute("src")
                        index = img1.find('?')
                        modified_url = img1[:index] if index != -1 else img1
                        images.append(modified_url)

                    # get other images
                    try:
                        parent_element = self.find_element_with_multiple_xpaths(self.browser, [
                            '/html/body/main/div[2]/div/div/div[2]/div/div[1]/div',
                            '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[1]/div',
                            '/html/body/div[2]/div[4]/div[1]/chr-lot-header/div/div[2]/div/div[1]/div'
                        ])
                    except Exception as e:
                        logging.warn(f"Error: {e} -- for url: {url} --\n")

                    if parent_element:
                        child_elem = parent_element.find_elements(
                            By.XPATH, './/chr-lot-header-gallery-button')
                        for chr_lot in child_elem:
                            div_1 = chr_lot.find_element(By.XPATH, './/div')
                            div_2 = div_1.find_element(By.XPATH, './/div')
                            try:
                                chr_image = div_2.find_element(
                                    By.XPATH, './/chr-image')
                                div_3 = chr_image.find_element(
                                    By.XPATH, './/div')

                            except NoSuchElementException:
                                div_3 = div_2.find_element(By.XPATH, './/div')
                            img = div_3.find_element(By.XPATH, './/img')
                            image_url = img.get_attribute("src")
                            index = image_url.find('?')
                            # Remove everything after the '?' character
                            modified_url = image_url[:index] if index != - \
                                1 else image_url
                            images.append(modified_url)

            except Exception as e:
                logging.warn(f"Error:: {e} -- for url: {url} --\n")
            item['images'] = images

            # 8 Description
            try:
                description = self.find_element_with_multiple_xpaths(self.browser, [
                    '/html/body/div[2]/div[3]/div[2]/div[2]/div[1]/div[1]/div[1]/div/chr-lot-details/section/div/chr-accordion/div/chr-accordion-item/div/fieldset/div',
                    '/html/body/main/div[3]/div[2]/div/div[1]/div/section/div/chr-accordion/div/chr-accordion-item[1]/div/fieldset/div/span',
                    '/html/body/div[2]/div[4]/div[2]/div[2]/div[1]/div[1]/div[1]/div/chr-lot-details/section/div/chr-accordion/div/chr-accordion-item[1]/div/fieldset/div',
                ])
            except Exception as e:
                logging.warn(f"Error: {e} -- for url: {url} --\n")
            item['description'] = description.text

            try:
                estimation = self.get_estimation()

            except Exception as e:
                logging.warn(f"Error:::: {e} -- for url: {url} --\n")
            if estimation:

                # Split the estimation string by spaces
                parts = estimation.split()

                # Extract the lot currency
                lot_currency = parts[0]

                # Extract the minimum and maximum prices
                est_min_price = parts[1]
                est_max_price = parts[4]

            else:
                lot_currency = None
                est_min_price = 0
                est_max_price = 0

            # 9 Lot Currency
            item['lot_currency'] = lot_currency
            # 10 Est Min Price
            item['est_min_price'] = est_min_price
            # 11 Est Max Price
            item['est_max_price'] = est_max_price

            # 12 Sold Price
            try:
                sold_price = self.find_element_with_multiple_xpaths(self.browser, [
                    '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[2]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[1]/span[2]',
                    '/html/body/main/div[2]/div/div/div[2]/div/div[3]/div/div[3]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[1]/span[2]'
                ])
                if sold_price:
                    sold_price = sold_price.text
                    parts = sold_price.split()
                    sold_price_value = parts[1]

                    sold_price_without_comma = sold_price_value.replace(
                        ',', '')
                    item['sold_price'] = sold_price_without_comma
                    item["sold"] = 1
                else:
                    sold_price = 0
                    item['sold'] = 0
                    item['sold_price'] = 0
            except Exception:
                sold_price = 0
                item['sold'] = 0
                item['sold_price'] = 0

            item['sold_price_dollar'] = None

            # 14  URL
            item['url'] = url
            item["status"] = "Success"

        except Exception as e:
            item['status'] = "Failed"
            logging.error(
                "ChristiesSpider; msg=Crawling Failed > %s;url= %s", str(e), url)
            logging.debug("ChristiesSpider; msg=Crawling Failed;url= %s;Error=%s",
                          url, traceback.format_exc())

        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = url
        item["job"] = self.job
        print(f"\n\n----Item scraped: {item}---\n\n")
        yield item

    def get_estimation(self):
        xpaths = [
            '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[2]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[2]/div[2]/span',
            '/html/body/main/div[2]/div/div/div[2]/div/div[3]/div/div[3]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[2]/div[2]/span',
            '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[2]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[1]/div[2]/span',
            '/html/body/div[2]/div[4]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[2]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[2]/div[2]/span',
            '/html/body/div[2]/div[4]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[2]/chr-lot-header-dynamic-content/chr-loader-next/div/div[1]/div/div[1]/div/div[1]/div[2]/span'
        ]

        for xpath in xpaths:
            try:
                estimation = self.browser.find_element(By.XPATH, xpath)
                if estimation:
                    return estimation.text
            except NoSuchElementException:
                continue  # Try the next XPath
        return None

    def get_title(self):
        try:
            wait = WebDriverWait(self.browser, 10)
            xpaths = ['/html/body/main/div[2]/div/div/div[2]/div/div[3]/div/span',
                      '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[1]/div/span',
                      '/html/body/div[2]/div[3]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[1]/span', '/html/body/div[2]/div[4]/div[1]/chr-lot-header/div/div[2]/div/div[3]/div/section[1]/span']
            for xpath in xpaths:
                try:
                    element = wait.until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    if element:
                        title_text = element.text.strip()
                        if title_text:
                            return title_text

                except Exception as e:
                    pass
        except Exception as e:

            logging.warn(f"An error occurred while getting the title: {e}")

        return None

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
                # element = wait.until(
                #     EC.visibility_of_element_located(
                #         (By.XPATH, xpath))
                # )
                element = wait.until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )

                if element:
                    return element

            except Exception as e:
                continue
        return None

    def get_image_urls_from_elements(self, elements):
        """
        Extracts image URLs from a list of elements.

        Args:
            elements: A list of elements to extract URLs from.

        Returns:
            A list of image URLs.
        """
        images = []
        for elem in elements:
            try:
                chr_lot = elem.find_element(
                    By.XPATH, './/chr-gallery-image-zoom')
                div_elem = chr_lot.find_element(By.XPATH, './/div')
                img = div_elem.find_element(By.XPATH, './/img')

                image_url = img.get_attribute("src")
                index = image_url.find('?')
                modified_url = image_url[:index] if index != -1 else image_url
                images.append(modified_url)
            except NoSuchElementException:
                continue
        return images

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ChristiesSpider, cls).from_crawler(
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
