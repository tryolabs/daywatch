# -*- coding: utf-8 -*-

import os
import sys

DIRNAME = os.path.abspath(os.path.dirname(__file__).decode('utf-8'))
PROJECT_SRC_DIR = DIRNAME + '/../../../'

sys.path.append(PROJECT_SRC_DIR)

# Be able to access Django settings too
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

DEBUG = False
LOG_LEVEL = 'DEBUG'
LOG_ENABLED = True

BOT_NAME = 'item_scraper'

SPIDER_MODULES = [
    'core.scraper.item_scraper.spiders',
]

NEWSPIDER_MODULE = 'item_scraper.spiders'
DEFAULT_ITEM_CLASS = 'item_scraper.items.DealItem'
USER_AGENT = "Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0"

USER_AGENT_LIST = [
    'Mozilla/5.0 (X11; U; SunOS sun4u; en-US; rv:1.7.7) Gecko/20050421',
    'Mozilla/5.0 (X11; Linux x86_64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.7) Gecko/20050427 Red Hat/1.7.7-1.1.3.4',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.7) Gecko/20050420 Debian/1.7.7-2',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.7) Gecko/20050414',
    'Mozilla/5.0 (X11; U; Linux i686; de-AT; rv:1.7.7) Gecko/20050415',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr-FR; rv:1.7.7) Gecko/20050414',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.7) Gecko/20050414',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; de-AT; rv:1.7.7) Gecko/20050414',
    'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.7.7) Gecko/20050414',
    'Mozilla/5.0 (Windows; U; Windows NT 5.0; de-AT; rv:1.7.7) Gecko/20050414'
]

ITEM_PIPELINES = {
    'core.scraper.item_scraper.pipelines.CheckMissingValuesPipeline': 100,
    'core.scraper.item_scraper.pipelines.PrintPipeline': 200,
    'core.scraper.item_scraper.pipelines.StorePipeline': 300,
}

PROXY_SPIDERS = []

HTTP_PROXY = 'http://user:pass@us.proxymesh.com:31280/'

DOWNLOADER_MIDDLEWARES = {
    'core.scraper.item_scraper.middleware.RandomUserAgentMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': 500,
    # 'item_scraper.middleware.SelectiveProxyMiddleware': HTTP_PROXY,
}

SPIDER_MIDDLEWARES = {
    'core.scraper.item_scraper.middleware.DisallowUrlsMiddleware': 400,
}

DOWNLOAD_DELAY = 0.1

DEFAULT_ITEM_LOADERS = []

EXTRA_ITEM_LOADERS = []
