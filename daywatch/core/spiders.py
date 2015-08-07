# -*- coding: utf-8 -*-

import os
import warnings
import importlib
from datetime import datetime
from django.utils import timezone

from core.models import Run, ErrorLog, ITEM_MODEL
from core.utils import make_logger

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings

from scraper.item_scraper.spiders.spiders import SPIDERS

os.environ.setdefault('SCRAPY_SETTINGS_MODULE',
                      'core.scraper.item_scraper.settings')

logger = make_logger()


def run_spider_instance(spider_class, site_id, main_url):
    """Run a spider given its spider class. For example, importing the TestSpider
and passing it to this function will run it."""
    spider = spider_class(site_id=site_id, main_url=main_url)
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.configure()
    # Scrapy uses a deprecated Twisted interface. Until the fix makes it to a
    # new version (>0.24.4), we'll use this so deprecation warnings don't
    # clutter the output
    crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    crawler.crawl(spider)
    crawler.start()
    reactor.run()


class SpiderImportError(Exception):

    def __init__(self, spider_name, error):
        self.spider_name = spider_name
        self.error = error

    def __unicode__(self):
        return "Error importing spider '%s': %s" % (self.spider_name,
                                                    self.self_error)


def import_spider(spider_name, class_name):
    path = 'core.scraper.item_scraper.spiders.' + spider_name
    module = importlib.import_module(path)

    if hasattr(module, class_name):
        return getattr(module, class_name)
    else:
        return None


def find_spider_class(spider_name):
    for name, class_name in SPIDERS:
        if name == spider_name:
            return import_spider(spider_name, class_name)
    else:
        raise NoSuchSpider(spider_name)


def run_spider(spider_name, site_id, main_url):
    spider = find_spider_class(spider_name)
    run_spider_instance(spider, site_id, main_url)


def associate_errors(site, start, end, count):
    '''Find all errors logged by `site`'s spider between `start` and `end`, and
    make them point to the associated spider `Run`.'''
    run = Run.objects.create(start=start, end=end, site=site, scraped=count)
    for log in ErrorLog.objects.filter(date_time__gte=start,
                                       date_time__lte=end,
                                       site=site):
        log.run = run
        log.save()
    run.save()


def run_site_spider(site):
    start_time = timezone.now()
    start_item_count = ITEM_MODEL.objects.filter(site=site).count()
    logger.info('Running spider %s' % site.spider_name)
    run_spider(site.spider_name, site.id, site.url)
    end_time = timezone.now()
    end_item_count = ITEM_MODEL.objects.filter(site=site).count()
    item_count = end_item_count - start_item_count
    if item_count < 0:
        item_count = 0
    associate_errors(site, start_time, end_time, item_count)
