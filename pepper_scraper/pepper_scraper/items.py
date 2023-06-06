# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PepperScraperUrl(scrapy.Item):
    link = scrapy.Field()


class PepperScraperItem(scrapy.Item):
    title = scrapy.Field()
    price_before_discount = scrapy.Field()
    price_after_discount = scrapy.Field()
    hotness = scrapy.Field()
    comments = scrapy.Field()
    username = scrapy.Field()
    category = scrapy.Field()
    link = scrapy.Field()
    percentage_change_in_price = scrapy.Field()
    place_of_bargain_price = scrapy.Field()