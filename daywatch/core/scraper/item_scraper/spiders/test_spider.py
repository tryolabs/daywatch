# -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders.crawl import Rule
from scrapy.selector import Selector

from fields import *

from dailydeal_spider import DailyDealSpider
from base import Extractor, hash


def ensure_protocol(url):
    return 'http:' + url


class TestSpider(DailyDealSpider):
    country = 'us'
    name = 'test_spider'
    main_domain = 'dailysteals.com'
    allowed_domains = [main_domain]
    main_url = 'http://www.dailysteals.com/'

    rules = (
        # Deals
        Rule(
            SgmlLinkExtractor(restrict_xpaths='//h4[contains(@class,"product-title")]',
                              process_value=lambda url: ensure_protocol(url)),
            callback='get_item',
            follow=False
        ),
    )

    has_main_offer = False
    decimal_mark = DECIMAL_MARK_PERIOD

    price_currency_xpath = '//div[@itemprop="price"]//text()'

    extractors = {
        F_ID: Extractor(xpath='//a[contains(@class,"btn-cart")]/@data-itemid'),
        F_OFFER: Extractor(xpath='//h1[@itemprop="name"]//text()'),
        F_DISCOUNT: Extractor(xpath='//dl[@class="discount"]//text()'),
        F_SOLD: Extractor(xpath='//div[contains(@class, "coupons-bought")]/text()'),
        F_DESC: Extractor(xpath='//div[@class="merchant-content"]//text()'),
        F_CITY: Extractor(xpath='//div[@class="zone"]//text()'),
        F_M_NAME: Extractor(xpath='//div[@class="side-merchant"]/span/b/text()'),
        F_M_WEBSITE: Extractor(xpath='//div[@class="side-merchant"]//a/@href'),
        F_M_ADDRESS: Extractor(xpath='//div[@class="adress-info"]//text()'),
        # F_M_LAT: Extractor(xpath='//div[@class="adress-info"]/img/@src',
        #                    fn=lambda matches, r, s:
        #                    matches[0].split('%7C')[1].split(',')[0]),
        # F_M_LON: Extractor(xpath='//div[@class="adress-info"]/img/@src',
        #                    fn=lambda matches, r, s:
        #                    matches[0].split('%7C')[1].split(',')[1])
    }
