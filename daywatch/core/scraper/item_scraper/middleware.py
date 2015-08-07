# -*- coding: utf-8 -*-

import base64
import random
from urllib import unquote
from urllib2 import _parse_proxy
from urlparse import urlunparse, urlparse, ParseResult

from scrapy import log
from scrapy.http import Request

from .settings import PROXY_SPIDERS
from .settings import HTTP_PROXY
from .settings import USER_AGENT_LIST


class SelectiveProxyMiddleware(object):
    def __init__(self):
        self.proxy = self.parse_proxy(HTTP_PROXY, 'http')

    def parse_proxy(self, url, orig_type):
        proxy_type, user, password, hostport = _parse_proxy(url)
        proxy_url = urlunparse((proxy_type or orig_type, hostport, '',
                                '', '', ''))

        if user and password:
            user_pass = '%s:%s' % (unquote(user), unquote(password))
            creds = base64.b64encode(user_pass).strip()
        else:
            creds = None

        return creds, proxy_url

    def process_request(self, request, spider):
        if spider.name in PROXY_SPIDERS:
            creds, proxy = self.proxy
            request.meta['proxy'] = proxy
            if creds:
                request.headers['Proxy-Authorization'] = 'Basic ' + creds


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua = random.choice(USER_AGENT_LIST)
        if ua:
            request.headers.setdefault('User-Agent', ua)


class DisallowUrlsMiddleware(object):
    def process_spider_output(self, response, result, spider):
        for x in result:
            if isinstance(x, Request) and hasattr(spider, 'disallow_urls'):
                if self.should_follow(x, spider):
                    yield x
                else:
                    log.msg("Filtered URL %s: " % (x.url),
                            level=log.DEBUG, spider=spider)
            else:
                yield x

    def should_follow(self, response, spider):
        parsed = urlparse(response.url)
        url = ParseResult(
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            None,
            None
        )
        url = url.geturl()
        return url not in spider.disallow_urls


from selenium import webdriver
from scrapy.http import HtmlResponse


class SeleniumMiddleware(object):

    def __init__(self):
        self.driver = webdriver.PhantomJS()

    def process_request(self, request, spider):

        if spider.USE_SELENIUM:
            url = request._get_url()
            self.driver.get(url)
            return HtmlResponse(url, body=self.driver.page_source, encoding='utf-8')

