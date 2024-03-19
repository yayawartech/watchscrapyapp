# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WatchItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #1
	house_name = scrapy.Field()
	#2
	name = scrapy.Field()
	#3
	date = scrapy.Field()
	#4
	location = scrapy.Field()
	#5
	lot = scrapy.Field()
	#6
	images = scrapy.Field()
	#7
	title = scrapy.Field()
	#8
	description = scrapy.Field()
	#9
	lot_currency = scrapy.Field()
	#10
	est_min_price = scrapy.Field()
	#11
	est_max_price = scrapy.Field()
	#12
	sold = scrapy.Field()
	#13
	sold_price = scrapy.Field()
	#14
	sold_price_dollar = scrapy.Field()
	#15
	url = scrapy.Field()
	#16 
	status = scrapy.Field()
	#17
	job = scrapy.Field()
	#18
	auction_url  = scrapy.Field()
	#19
	total_lots = scrapy.Field()
	
	#1 HouseName
    #2 Name
    #3 Date
    #4 Location
    #5 Lot
    #6 Images
    #7 title
    #8 Description
    #9 Lot Currency
    #10 Est min Price
    #11 Est max Price
    #12 sold
    #13 sold_price
    #14 sold_price_dollar
    #15 url
