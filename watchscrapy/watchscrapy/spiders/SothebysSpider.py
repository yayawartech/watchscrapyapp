# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import FormRequest
import re, json, pprint
from datetime import datetime
import time

## additions
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import logging,traceback

from bs4 import BeautifulSoup
from watchscrapy.items import WatchItem
from watchapp.models import Setup

from scrapy import signals


class SothebysSpider(scrapy.Spider):
    name = "sothebysSpider"
    allowed_domains = ["www.sothebys.com"]
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'

    def __init__(self, url='',job='', *args, **kwargs):
        super(SothebysSpider, self).__init__(*args, **kwargs)
        self.start_urls = url.split(",")
        self.job = job

    def sel_configuration(self):
        # Selenium Configuration
        setup = Setup.objects.first()
        SELENIUM_CHROMEDRIVER_PATH = setup.chromedriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36")
        browser = webdriver.Chrome(executable_path=SELENIUM_CHROMEDRIVER_PATH, chrome_options=options)
        browser.set_window_size(1440, 900)
        return browser

    def start_requests(self):
        for source_url in self.start_urls:
            try:
                logging.warn("SothebysSpider; msg=Spider started; url= %s",source_url)
                # use set to avoid duplicates
                lots_urls = set() 

                self.browser.get(source_url)
                time.sleep(5)

                # if the lots are in grid view, first toggle them to list view
                try:
                    view_toggle = self.browser.find_element_by_xpath(r'//span[@aria-label="List view"]')
                    #BREAKPOINT: CSS CLASS

                    if view_toggle.get_attribute("class").strip() != "css-1b67vvn":
                        logging.warning("SothebysSpider; msg=Toggling list view; url = %s", source_url)
                        view_toggle.click()
                        time.sleep(5)
                except:
                    view_toggle = self.browser.find_element_by_xpath(r'//button[@aria-label="List view"]')
                    #BREAKPOINT: CSS CLASS
                    if "button-module_button_secondary_active__31n1P" not in view_toggle.get_attribute("class").strip():
                        logging.warning("SothebysSpider; msg=Toggling list view; url = %s", source_url)
                        view_toggle.click()
                        time.sleep(5)

                # try to load lots in all pages by clicking Next button at the end of each page
                logging.warning("SothebysSpider; msg=Trying to load lots in next pages; url= %s", source_url)
                while True:
                    self.scrollAndLoad(self.browser)
                    try:
                        #BREAKPOINT: CSS CLASS
                        # collecting links in this page
                        links = self.browser.find_elements_by_css_selector("a.css-1um49bp")
                        for link in links:
                            lots_urls.add(link.get_attribute("href"))
                        
                        #waiting for Next button to be available for 10 seconds.
                        next_button = WebDriverWait(self.browser, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Next"]'))
                        )
                        
                        #if next button is not enabled, it means we reached to the last page.
                        if not next_button.is_enabled():
                            break
                        else:
                            next_button.click()
                            time.sleep(5)
                    #raised by WebDriverWait if next button not found on the page.
                    except TimeoutException as e:
                        logging.warning("SothebysSpider; msg=Did not found next button on the page. Assuming there is only one page. url=%s", source_url)
                        break
                    #raised by browser.find_elements_by_css_selector, if links are not found in the page
                    except NoSuchElementException as e:
                        logging.warning("SothebysSpider; msg=Could not find Lot Url links.")
                        break
                    #any other generic exceptions
                    except Exception as e:
                        logging.exception("Exception occured while trying to collect lot urls.")
                
                total_lots = len(lots_urls)
                logging.warning("SothebysSpider; msg=Loading Complete. Found %d lots. url= %s", total_lots, source_url)

                page_source = self.browser.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                script = soup.find('script',{'type': 'application/ld+json'}).string
                pre_data = json.loads(script)
                try:
                    date = pre_data[0]['startDate'].split("T")[0]
                except:
                    date = pre_data[0]['endDate'].split("T")[0]
                location = pre_data[0]['location']['name']

                for i, url in enumerate(lots_urls):
                    yield scrapy.Request("https://www.google.com",dont_filter=True,callback=self.parseBS, meta={'url':url,'browser':self.browser,'source_url':source_url,'date':date,'location':location,'lots':total_lots})
                    #break

            except Exception as e:
                item = WatchItem()
                item['status'] = "Failed"
                logging.error("SothebysSpider; msg=Crawling Failed > %s;url=%s",str(e),source_url)
                logging.error("SothebysSpider; msg=Crawling Failed;url=%sError=%s",traceback.format_exc(),source_url)
                yield item

    def parseBS(self,response):
        url = response.meta.get('url')
        browser = response.meta.get('browser')
        source_url = response.meta.get('source_url')
        logging.warn("SothebysSpider; msg=Crawling going to start;url= %s",url)
        item = WatchItem()
        try:
            browser.get(url)
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            #logging.warn(page_source)
            
            #1 House Name
            item['house_name'] = 9

            #2 Auction Name
            #BREAKPOINT: CSS CLASS
            item['name'] = soup.find('a', {'href': '.'}).text
            logging.warn("====>name : "+ item['name'])
            
            #3 Date
            item['date'] = datetime.strptime(response.meta.get('date'),'%Y-%m-%d').strftime('%b %d,%Y')

            #4 Location
            item['location'] = response.meta.get('location')

            #5 Lot
            lot_number_info = soup.find(id='lot-detail-navigator-lot-number').text
            # lot_number_info = soup.find('span', {'class': 'css-yxsueo'}).text
            item['lot'] = re.findall(r'\d+',lot_number_info)[0]
            logging.warn("====>lot : "+ item['lot'])
            #6 Images
            #BREAKPOINT: CSS CLASS
            images = soup.find_all('img', attrs= {'alt': re.compile("^View ")})
            images_links = ""
            logging.warn("====>Images : "+ str(len(images)))
            for image in images:
                images_links = image['src'] + "," + images_links
            
            item['images'] = images_links

            #7 Title
            # item['title'] = soup.find('h1', {'class': 'css-dzom6s'}).text
            try:
                item['title'] = soup.find(attrs={'property': 'og:title'}).get('content') #soup.find('h1', {'aria-label': 'Lot title'}).text
                logging.warn("====>title : "+ item['title'])
            except:
                artist = soup.find('h1', {'aria-label': 'Lot artist'}).text
                title = soup.find('p', {'aria-label': 'Lot title'}).text
                item['title'] = "{} {}".format(artist, title)


            #8 Description
            #BREAKPOINT: CSS CLASS
            description = soup.find('div', id='collapsable-container-DescriptionSection')
            
            if not description:
                #BREAKPOINT: CSS CLASS
                description = soup.find('div', {'class': 'css-1ewow1l'})
            item['description'] = description.text

            logging.warn("====>description : "+ item['description'])

            # price_text = soup.find('div', {'class': 'css-10l5lxu'}).find_all('span', {'class': 'css-7qyd39-label-regular'}) #version 2
            # price_text = soup.find('span', {'class': 'css-1g8ar3q'}).text #version 1
            #BREAKPOINT: CSS CLASS

            parent_price = soup.find(text = 'Estimate: ').parent.parent
            #logging.warn(parent_price)
            #logging.warn("====>findChildren : "+ str(parent_price.findChildren()))
            price_text = parent_price.text 
            #soup.find("div", {'class': 'css-10l5lxu'}).find_all('p')
            
            logging.warn("====>price_text : "+ price_text)
            if price_text is not None:
                
                price_text = price_text.replace('Estimate: ', '')
                price_text = price_text.replace('-', '')
                lot_currency = price_text.strip()[-3:]
                est_min_price = price_text[:-3].split('to')[0].strip()
                est_max_price = price_text[:-3].split('to')[1].strip()
            else:
                lot_currency = None
                est_min_price = None
                est_max_price = None
               
            #9 Lot Currency
            item['lot_currency'] = lot_currency
            logging.warn("====>lot_currency : "+ item['lot_currency'])  

            #10 Est Min Price
            item['est_min_price'] = est_min_price.replace(",","")
            logging.warn("====>est_min_price : "+ str(item['est_min_price']))

            #11 Est Max Price 
            item['est_max_price'] = est_max_price.replace(",","")
            logging.warn("====>est_max_price : "+ str(item['est_max_price']))

            #12 Sold Price
            #BREAKPOINT: CSS CLASS
            parent_sold_price = soup.find(text= re.compile('^Lot sold:')).parent.parent
            sold_price_info = parent_sold_price.findChildren()[1]
            #sold_price_info = soup.find('span', {'class': "css-1nkk3t4"})
            sold = sold_price = 0
            if sold_price_info:
                sold_price = sold_price_info.text.replace(",", "")
                #BREAKPOINT: CSS CLASS
                sold_currency =parent_sold_price.findChildren()[2].text
                #sold_currency = soup.find('span', {'class': "css-65xq9y"}).text
                sold = 1
            item['sold_price'] = sold_price
            logging.warn("====>sold_price : "+ str(item['sold_price']))
            item['sold'] = sold
            #13 Sold Price Dollar
            item['sold_price_dollar'] = 0

            #14  URL
            item['url'] = url
            item["status"] = "Success"
            logging.debug("SothebysSpider; msg=Crawling Completed > %s;url= %s",item,url)
        except Exception as e:
            item['status'] = "Failed"
            logging.error("SothebysSpider; msg=Crawling Failed > %s;url= %s",str(e),url)
            logging.error("SothebysSpider; msg=Crawling Failed;url= %s;Error=%s",url,traceback.format_exc())
        item['total_lots'] = response.meta.get("lots")
        item["auction_url"] = source_url
        item["job"] = self.job
        return item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SothebysSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider

    #signal fired when spider first opens 
    #used for creating a chrome browser instance
    def spider_opened(self, spider):
        logging.warning("Setting up resources...")
        self.browser = self.sel_configuration()

    #singal fired when spider closes
    #used for cleaning up resources
    def spider_closed(self, spider):
        logging.warning("Cleaning up resources...")
        self.browser.close()

    #scroll to the end of the page
    def scrollAndLoad(self,browser):
        SCROLL_PAUSE_TIME = 0.5

        # Get scroll height
        last_height = browser.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load content
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

