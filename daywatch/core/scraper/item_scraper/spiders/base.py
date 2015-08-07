from datetime import datetime
import re
import hashlib

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector

from core.scraper.item_scraper.items import CRITICAL_FIELDS, ITEM_LOADER, \
    DaywatchItem
from django.conf import settings
from core.scraper.item_scraper.errors import SpiderException, \
    raise_missing_value
from core.models import MISSING_VALUE, Category, Country, STATUS_WARNING, \
    STATUS_UNKNOWN, STATUS_CRITICAL
from fields import F_ID, F_OFFER, DECIMAL_MARK_COMMA
from core.utils import make_logger
from core.monkeylearn import classify


from fields import *


logger = make_logger()


class Extractor():
    '''
    NOTE: When using both a function and a regular expression, remember the
    regexp happens before, then the list of matches is sent to the function.

    - extractor algorithm:
        - xpath:
            - regexp:
                - call fn(regexp_matches(xpath_results),response,self)
            - no regexp:
                - call fn([xpath_results],response,self)
        - no xpath:
            - regexp:
                - call fn([regexp_matches],response,self)
            - no regexp:
                - call fn([],response,self)
    '''

    def __init__(self, xpath=None, fn=lambda match, resp, self: match,
                 regexp=None):
        self.xpath = xpath
        self.fn = fn
        self.regexp = regexp

    def extract(self, response):
        if self.xpath is None:
            # No xpath
            if self.regexp is None:
                # No regexp
                # Call fn with the Response
                return self.fn([], response, self)
            else:
                # Run the regexp on the raw HTML
                matches = re.findall(self.regexp, response.body)
                if matches:
                    return self.fn(matches if matches else [],
                                   response, self)
                else:
                    return []
        else:
            # Has xpath
            hxs = Selector(text=response.body)
            results = hxs.xpath(self.xpath).extract()
            if self.regexp is None:
                # No regexp, just send the xpath results
                if results:
                    return self.fn(results, response, self)
                else:
                    return []
            else:
                # Run the regexp on each result
                # the following iterates over the xpath matches, compiles a
                # list of strings that match the regexp, and returns the list
                # of those lists
                if results:
                    regexp_matches = [re.findall(self.regexp, x)
                                      for x in results]
                    return self.fn([y for y in regexp_matches if y],
                                   response, self)
                else:
                    return []


def minimal_item(spider, response):
    hxs = Selector(response)
    item = DaywatchItem()
    l = DaywatchItem()
    l.add_value(F_RAW_HTML, response.body)
    l.add_value(F_URL, response.url)
    l.add_value(F_ID, response.url)
    return l


def hash(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()


class DayWatchSpider(CrawlSpider):
    start_urls = []
    forbidden_urls = []

    offer_xpath = '//title/text()'  # Default
    hash_id_xpath = ''
    description_xpath = ''
    image_url_xpath = ''
    finished_xpath = ''

    # If this selector fails, the Item will be dropped
    finished_xpath = ''

    decimal_mark = DECIMAL_MARK_COMMA

    fields_to_categorize = [F_DESC]
    calculated_fields = [F_CATEGORY]

    forbidden_urls = []

    extractors = {
        F_URL: Extractor(fn=lambda m, resp, s: resp.url),
        F_DATE_TIME: Extractor(fn=lambda m, r, s: datetime.now()),
        F_RAW_HTML: Extractor(fn=lambda m, resp, s:
                              resp.body.decode(resp.encoding)),
    }

    # Misc
    lang = ''
    has_main_offer = True

    def parse(self, response):
        """
        Redefine parse method so we both execute the rules AND still get the
        main offer.
        If a particular spider does not want to use this behavior it should
        specify the variable has_main_offer as False.
        """
        for req in super(DayWatchSpider, self).parse(response):
            yield req
        if self.has_main_offer:
            yield self.get_item(response, True)

    def __init__(self, *a, **kw):
        super(DayWatchSpider, self).__init__(*a, **kw)
        self.site_id = int(kw.get('site_id', '-1'))
        self.main_url = kw.get('main_url')
        self.start_urls.append(self.main_url)

    def load_price(self, loader, response):
        """
        Loads the price and currency from the price_xpath.
        """
        if not self.price_currency_xpath:
            loader.add_value(F_CURRENCY, MISSING_VALUE)
            site = SITE_MODEL.objects.get(spider_name=self.name)
            loader.add_value(F_PRICE, site.country.currency)
        else:
            loader.load_price_currency(self.price_currency_xpath, self.name)

    def load_raw_html(self, loader, response):
        loader.item[F_RAW_HTML] = response.body

    def load_url(self, loader, response):
        loader.item[F_URL] = response.url

    def load_category(self, loader, response):
        """
        Loads the category by applying a text classifier to the join of the
        fields_to_categorize.
        """
        item = loader.item
        try:
            item[F_CATEGORY] = monkeylearn.classify([content], lang_code)
        except:
            logger.error("Could not classify item '%s', assigning category 'Retail'",
                         item[F_ID])
            try:
                item[F_CATEGORY] = Category.objects.get(name='Retail')
            except:
                item[F_CATEGORY] = None
                logger.error('Could not find retail category.')

        return item

    def extract(self, loader, response):
        if self.extractors:
            for field, extractor in self.extractors.iteritems():
                loader.add_value(field, extractor.extract(response))
            if F_ID not in self.extractors.keys():
                loader.add_value(F_ID, loader.get_value(F_OFFER))

    def get_item(self, response, other=None):
        """
        The main callback used by the rules to extract data from an item.
        """
        hxs = Selector(response)
        item = DaywatchItem()
        loader = ITEM_LOADER(item=item, selector=hxs, spider_name=self.name,
                             url=response.url, country=self.country,
                             decimal_mark=self.decimal_mark)
        return self.load_all_fields(item, loader, response)

    def load_all_fields(self, item, loader, response):
        """
        Iterates over all the fields to load its values
        """
        # iterate over all the field names
        xpath_fields = list(set(item.fields.keys()) -
                            set(self.calculated_fields))
        # first load the fields that are extracted from xpaths
        for field_name in xpath_fields:
            self.load_field(field_name, loader, response)

        # load extractors
        self.extract(loader, response)
        item = loader.load_item()

        # then load the fields that are calculated on top of xpath fields
        for field_name in self.calculated_fields:
            self.load_field(field_name, loader, response)
        return loader.load_item()

    def load_field(self, field_name, loader, response):
        """
        Generic method to load fields with the item loader
        """
        try:
            method_name = 'load_' + field_name
            # if it is defined a custom method to load the field, call it
            # else, call the generic load_field method
            if (hasattr(self, method_name) and
                callable(getattr(self, method_name))):
                getattr(self, method_name)(loader, response)
            else:
                xpath = getattr(self, field_name + '_xpath', False)
                if not xpath:
                    loader.add_value(field_name, MISSING_VALUE)
                else:
                    loader.add_xpath(field_name, xpath)
        except Exception as e:
            error_level = STATUS_UNKNOWN
            if field_name in CRITICAL_FIELDS:
                error_level = STATUS_CRITICAL
            else:
                error_level = STATUS_WARNING
            raise_missing_value(self.name,
                                field_name=field_name,
                                url=response.url,
                                exception=e,
                                level=error_level,
                                message="Could not load field '%s'" % field_name)
