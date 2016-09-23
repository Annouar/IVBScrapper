# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VieItem(scrapy.Item):
    id_civiweb = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    company = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    duration = scrapy.Field()
    published_time = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    start_time = scrapy.Field()
