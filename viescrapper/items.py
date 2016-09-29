# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VieItem(scrapy.Item):
    id_civiweb = scrapy.Field()
    job_title = scrapy.Field()
    url = scrapy.Field()
    company = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    duration = scrapy.Field()
    published_date = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    start_date = scrapy.Field()
    degrees = scrapy.Field()
    languages = scrapy.Field()
    experience_required = scrapy.Field()
    skill_fields = scrapy.Field()
    scrapped_time = scrapy.Field()
