# -*- coding: utf-8 -*-

from django.conf import settings

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, Identity, Compose, Join
from scrapy.item import Item, Field

from parsers import whitespace_trimmer, parse_discount, parse_sold_count,\
    parse_en_float_str, parse_price_currency
from errors import raise_missing_value, PARSING_ERROR

from spiders.fields import F_ID, F_OFFER, F_PRICE, F_CURRENCY, F_URL, F_DESC

from core.models import MISSING_VALUE, ITEM_MODEL, Currency, SITE_MODEL, \
    STATUS_CRITICAL

CRITICAL_FIELDS = [F_ID, F_OFFER, F_DESC]


class DaywatchItem(Item):
    '''This item contains the fields from both the ITEM_MODEL
    and the MERCHANT_MODEL. They are stored in different database
    objects in the pipeline'''

    # Item
    offer = Field()
    url = Field()
    hash_id = Field()
    description = Field()
    raw_html = Field()
    image_url = Field()
    date_time = Field()
    category = Field()
    site = Field()
    # DealItem
    currency = Field()
    price = Field()
    discount = Field()
    sold_count = Field()
    city = Field()
    end_date_time = Field()
    active = Field()
    # Merchant
    merchant_name = Field()
    merchant_lat = Field()
    merchant_lon = Field()
    merchant_address = Field()
    merchant_phone = Field()
    merchant_website = Field()
    merchant_email = Field()


class DaywatchLoader(ItemLoader):
    '''
    Base ItemLoader. Users can create a custom loader to handle certain fields
    of the project item model.
    '''
    default_input_processor = Identity()
    default_output_processor = TakeFirst()


class DealLoader(DaywatchLoader):

    offer_out = Compose(Join(), whitespace_trimmer)
    discount_out = Compose(Join(), parse_discount)
    sold_count_out = Compose(Join(), parse_sold_count)
    description_out = Compose(Join(), whitespace_trimmer)
    is_main_deal_out = Compose(TakeFirst(), int)

    city_out = Compose(Join(), whitespace_trimmer)
    merchant_name_out = Compose(Join(), whitespace_trimmer)
    merchant_city_out = Join()
    merchant_lat_out = Compose(TakeFirst(), parse_en_float_str)
    merchant_lon_out = Compose(TakeFirst(), parse_en_float_str)
    merchant_address_out = Compose(Join(), whitespace_trimmer)
    merchant_postcode_out = Join()
    merchant_phone_out = Join(";")
    merchant_website_out = TakeFirst()
    merchant_email_out = Join()

    def load_price_currency(self, xpath, spider_name=''):
        try:
            text = ' '.join(self.selector.xpath(xpath).extract())
            (price, currency) = parse_price_currency(text, self.context)
            self.add_value(F_PRICE, price)
            self.add_value(F_CURRENCY, currency)
        except Exception as e:
            self.add_value(F_PRICE, MISSING_VALUE)
            site = SITE_MODEL.objects.get(spider_name=spider_name)

            self.add_value(F_CURRENCY, site.country.currency)
            raise_missing_value(
                spider_name=self.context['spider_name'],
                field_name=F_PRICE,
                url=self.context[F_URL],
                exception=e,
                level=STATUS_CRITICAL,
                message="Could not load price and currency.",
                category=PARSING_ERROR
            )

    def load_price_currency_from_str(self, text):
        try:
            (price, currency) = parse_price_currency(text, self.context)
            self.add_value(F_PRICE, price)
        except Exception as e:
            self.add_value(F_PRICE, MISSING_VALUE)
            raise_missing_value(
                spider_name=self.context['spider_name'],
                field_name=F_PRICE,
                url=self.context[F_URL],
                exception=e,
                level=STATUS_CRITICAL,
                message="Could not load price and currency.",
                category=PARSING_ERROR
            )

ITEM_LOADER = DealLoader
