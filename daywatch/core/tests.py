# -*- coding: utf-8 -*-

import random
import math
from datetime import datetime, timedelta

from django.test import TestCase
from django.conf import settings
from scrapy import http

from core.models import SITE_MODEL, ITEM_MODEL, Country, Run, ErrorLog, \
    STATUS_UNKNOWN
from core.scraper.item_scraper.spiders import base
from core.utils import percentage, datetime_to_unix, field_list, \
    numeric_field_list

# Utilities


class TestUtilities(TestCase):
    def test_percentage(self):
        self.assertEqual(percentage(1, 10), 10)

    def test_datetime_to_unix(self):
        stamp = datetime(year=2001, month=9, day=9, hour=01, minute=46,
                         second=40)
        self.assertEqual(datetime_to_unix(stamp),
                         1000000000)

    def test_field_list(self):
        fields = ['id', 'name', 'image_path', 'url', 'spider_name',
                  'spider_enabled', 'host_name', 'country', 'shows_sold_count']
        full_fields = field_list(SITE_MODEL)
        self.assertEqual([name for (name, cls) in full_fields], fields)

    def test_numeric_field_list(self):
        fields = ['price', 'discount', 'sold_count']
        self.assertEqual(numeric_field_list(ITEM_MODEL), fields)

# Duplicate removal tests


class TestDuplicateRemoval(TestCase):
    """Test that the duplicate detector works."""

    ITEM_NUM = 5

    def make_duplicate():
        return ITEM_MODEL(offer='Duplicate',
                          price=1,
                          discount=30,
                          sold_count=50,
                          city='Singapore')

    def make_non_duplicate(price):
        # Vary any one of the fields that the duplicate detector tests
        return ITEM_MODEL(offer='Non-Duplicate',
                          price=price,
                          discount=30,
                          sold_count=50,
                          city='Singapore')

    def setup(self):
        # Create duplicates (Only one of these should remain)
        for i in range(1, self.ITEM_NUM):
            self.make_duplicate().save()
        # Create non-duplicates
        for i in range(1, self.ITEM_NUM):
            self.make_non_duplicate(10 * i).save()

    def test_remove_duplicates(self):
        # Make sure all the duplicates were removed
        pass

    def test_keep_non_duplicates(self):
        # Make sure there are no false positives
        pass

# Extractor tests


def resp(text):
    return http.Response(url='http://tryolabs.com',
                         body=text)


class TestExtractorXpath(TestCase):
    def setUp(self):
        self.resp = resp('''
          <body>
            <ul>
              <li class="first odd">1</li>
              <li class="second even">2</li>
              <li class="third odd">3</li>
            </ul>
          </body>
        ''')

    def test_odd(self):
        ext = base.Extractor(xpath='//li[contains(@class,"odd")]/text()')
        self.assertEqual(ext.extract(self.resp), ['1', '3'])

    def test_even(self):
        ext = base.Extractor(xpath='//li[contains(@class,"even")]/text()')
        self.assertEqual(ext.extract(self.resp), ['2'])

    def test_third(self):
        ext = base.Extractor(xpath='//li[contains(@class,"third")]/text()')
        self.assertEqual(ext.extract(self.resp), ['3'])


class TestExtractorRegexp(TestCase):
    def setUp(self):
        self.text = resp("The value of 'pi' is approximately 3.14")
        self.html = resp('''<p>123 Foo Road, San Jose, CA.<br>
            <strong>Phone: 555-1234</strong></p>''')

    def test_regexp1(self):
        ext = base.Extractor(regexp=r'\'(.*)\'')
        self.assertEqual(ext.extract(self.text), ['pi'])

    def test_regexp2(self):
        ext = base.Extractor(regexp=r'(\d+.+\d+)')
        self.assertEqual(ext.extract(self.text), ['3.14'])

    def test_address(self):
        ext = base.Extractor(regexp=r'(\d+[^,]+),')
        self.assertEqual(ext.extract(self.html), ['123 Foo Road'])

    def test_phone(self):
        ext = base.Extractor(xpath='//strong/text()', regexp=r'\d+-\d+')
        self.assertEqual(ext.extract(self.html), [['555-1234']])


class TestExtractorFn(TestCase):
    def setUp(self):
        self.text = resp('''<ul>
                              <li>first</li>
                              <li>second</li>
                              <li>third</li>
                            </ul>
                            <p>
                                The value of 'pi' is approximately 3.14
                            </p>
                            ''')
        self.map = {'first': 1, 'second': 2, 'third': 3}

    def test_process(self):
        ext = base.Extractor(xpath='//li/text()',
                             fn=lambda matches, r, s:
                             [self.map[m] * 3 for m in matches])
        self.assertEqual(ext.extract(self.text), [3, 6, 9])


class TestExtractorSimultaneous(TestCase):
    def setUp(self):
        self.text = resp('''<p>
                                The value of 'pi' is approximately 3.14
                            </p>
                            ''')
        self.html = resp('''<p>123 Foo Road, San Jose, CA.<br>
            <strong>Phone: 555-1234</strong></p>''')

    def test_all1(self):
        ext = base.Extractor(xpath='//p/text()', regexp=r'(\d+.+\d+)',
                             fn=lambda matches, r, s:
                             math.trunc(float(matches[0][0])))
        self.assertEqual(ext.extract(self.text), 3)

    def test_all2(self):
        ext = base.Extractor(xpath='//p[not(child::string)]/text()',
                             regexp=r'(\d+[^.]+).',
                             fn=lambda matches, r, s: matches[0])
        self.assertEqual(ext.extract(self.html),
                         ['123 Foo Road, San Jose, CA'])

# Item and Spider tests


class TestItems(TestCase):

    def create_test_site(self, site_name, spider_name):
        country = Country.objects.get(name='Uruguay')
        return SITE_MODEL.objects.create(name=site_name,
                                         url='http://groupon.com',
                                         spider_name=spider_name,
                                         spider_enabled=True,
                                         host_name=settings.HOST_NAME,
                                         country=country,
                                         shows_sold_count=True)

    def create_run_data(self, site):
        """Given a site, create runs and error logs every day for the last ten
        days.
        """

        def create_test_error(time, category):
            return ErrorLog.objects.create(site=site,
                                           date_time=time,
                                           category=category,
                                           error_level=STATUS_UNKNOWN)

        def generate_categories(categories):
            out = []
            for category in categories:
                out += [category] * random.randint(1, 10)
            return out

        def rand_int():
            return int(random.randint(10, 100))

        objects = []

        today = datetime.today()
        for hour in [today - timedelta(days=n) for n in range(0, 24)]:
            start = hour
            end = hour
            run = Run.objects.create(site=site,
                                     start=start,
                                     end=end,
                                     offers=rand_int())
            categories = generate_categories(["Database", "Category",
                                              "Unknown", "HTML", "Offer",
                                              "Merchant"])
            errors = [create_test_error(start, cat)
                      for cat in categories]

            random.shuffle(errors)

            # To minimize the overhead of SQL inserts, objects are added to a
            # list and then shipped to the database all at once
            objects += [offers, run] + errors

        print "Saving objects"
        for obj in objects:
            obj.save()

    def setUp(self):
        # sites = [self.create_test_site(name, '')[0]
        #          for name in ['TestCompany' + letter
        #                       for letter in ['A', 'B', 'C']]]
        # for site in sites:
        #     self.create_run_data(site)
        self.test_site = self.create_test_site('Test', 'test-spider')
