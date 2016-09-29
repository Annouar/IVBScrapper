# -*- coding: utf-8 -*-

import pymongo  # $ pip install pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log


class MongoDBPipeline(object):
    """
    Pushes scraped data from civiweb to our mongo database
    """

    def __init__(self):
        """
        Constructor intialise mongodb connection
        """
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]
        log.msg(u'Connected to MongoDB {0}, using "{1}/{2}"'.format(
            settings['MONGODB_SERVER'],
            settings['MONGODB_DB'],
            settings['MONGODB_COLLECTION']))

        # Index on id_civiweb field to avoid duplicated offers in DB (raise a pymongo.errors.DuplicateKeyError exception
        # if we try to insert an existing document)
        self.collection.ensure_index([('id_civiweb', 1)], unique=True)

    def process_item(self, item, spider):
        """
        Validate item , and save it to mongodb
        """
        # Check if item fields are not empty
        # valid_data = True
        # for data in item:
        #     if not data:
        #         raise DropItem(u"Missing {0}!".format(data))

        # If item is not empty, store it in mongodb
        try:
            self.collection.insert(dict(item))
            self.collection.cr
            log.msg(u"Civiweb_offer (ref:{0}) added to MongoDB Database!".format(item['id_civiweb']), level=log.DEBUG, spider=spider)
        except pymongo.errors.DuplicateKeyError:
            raise DropItem(u"Item already exists {'id_civiweb':%s, 'job_title':%s}" % (item['id_civiweb'], item['job_title']) )

        return item
