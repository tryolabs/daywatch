# -*- coding: utf-8 -*-

import django.utils.timezone as tz
from scrapy.exceptions import DropItem
from colorama import Fore, Back, Style
from django.db import transaction

from errors import raise_missing_value, DATABASE_ERROR
from core.models import TestItem, SITE_MODEL, ITEM_MODEL, MERCHANT_MODEL, \
    SoldCount, STATUS_CRITICAL, STATUS_WARNING
from core.general import FIELD_FINISHED
from spiders.fields import F_M_NAME, F_M_LAT, F_M_LON, F_M_ADDRESS, F_M_PHONE, \
    F_M_WEBSITE, F_M_EMAIL

SOLD_COUNT_LOG_PERIOD = 15

MERCHANT_FIELDS = [F_M_NAME, F_M_LAT, F_M_LON, F_M_ADDRESS, F_M_PHONE,
                   F_M_WEBSITE, F_M_EMAIL]


def extract_item_data(deal):
    """Separate deal and merchant data."""

    merchant = {}
    for field in MERCHANT_FIELDS:
        if field in deal:
            merchant[field.replace('merchant_', '')] = deal[field]
            del deal[field]

    if 'merchant_city' in deal:
        del deal['merchant_city']

    deal['date_time'] = tz.now()
    return deal, merchant


def find_existing_merchant(merchant):
    """Find a Merchant object from the data in a merchant data dictionary."""

    try:
        return MERCHANT_MODEL.objects.get(name=merchant['name'])
    except:
        return None


@transaction.autocommit
def store_item(item, spider):
    """Store an item in the database."""

    # This field won't go into the database, so we can get rid of it
    if FIELD_FINISHED in item:
        del item[FIELD_FINISHED]

    try:
        # Find the merchant
        deal, merchant = extract_item_data(dict(item))
        merchant_obj = find_existing_merchant(merchant)
        if not merchant_obj:
            merchant_obj = MERCHANT_MODEL.objects.create(**merchant)
        deal['merchant'] = merchant_obj

        if hasattr(spider, 'site_id') and spider.site_id == -1:
            # If a site_id was not provided, we assume is user is testing the
            # spider, so we just create a TestItem
            TestItem.objects.create(**deal)
        else:
            # Otherwise, store the item model
            deal['site_id'] = spider.site_id
            deal_id = ITEM_MODEL.objects.create(**deal)
            if 'sold_count' in deal:
                log_data = {'deal': deal_id,
                            'date': deal['date_time'],
                            'value': deal['sold_count']}
                log = SoldCount.objects.create(**log_data)
    except Exception as e:
        raise_missing_value(
            spider_name=spider.name,
            url=item['url'],
            exception=e,
            level=STATUS_CRITICAL,
            message="Failed to store item.",
            category=DATABASE_ERROR
        )


class CheckMissingValuesPipeline(object):
    """Check if the item is missing key values, and if so, log the error and drop
    it."""

    def defines_xpath(self, spider, key):
        return (hasattr(spider, key + '_xpath') and
                (getattr(spider, key + '_xpath') != ''))

    def process_item(self, item, spider):
        for key in item.fields:
            url = item.get('url')
            if not item.get(key) and self.defines_xpath(spider,
                                                        key):
                if key == 'hash_id':
                    raise_missing_value(
                        spider_name=spider.name,
                        field_name=key,
                        url=url,
                        level=STATUS_CRITICAL,
                        message="Missing Item hash ID.",
                        category=DATABASE_ERROR
                    )
                    raise DropItem
                else:
                    raise_missing_value(
                        spider_name=spider.name,
                        field_name=key,
                        url=url,
                        level=STATUS_WARNING,
                        message="Missing field.",
                        category=DATABASE_ERROR
                    )
        return item


class PrintPipeline(object):
    """When processing a deal, pretty-print the important information to the console
    with some color.
    """

    def process_item(self, item, spider):
        print('%s%s%s %s%s (%s %s%s%s, %s)' %
              (Fore.GREEN,
               item['hash_id'][:10],
               Fore.RESET+Style.BRIGHT,
               item['offer'],
               Style.RESET_ALL,
               item['currency'],
               Fore.YELLOW+Style.DIM,
               item['price'],
               Fore.RESET+Style.RESET_ALL,
               item['discount'] if 'discount' in item else '?'))
        return item


class StorePipeline(object):
    """Store every item that comes along into the database."""

    def process_item(self, item, spider):
        store_item(item, spider)
        return item


class DuplicatesPipeline(object):
    """Filter out duplicate objects."""

    def spider_opened(self, spider):
        self.duplicates[spider.name] = set([])

    def spider_closed(self, spider):
        del self.duplicates[spider.name]

    def process_item(self, item, spider):
        if not (item[FIELD_HASH_ID] in self.duplicates[spider.name]):
            self.duplicates[spider.name].add(item[FIELD_HASH_ID])
            return item
        else:
            raise DropItem
