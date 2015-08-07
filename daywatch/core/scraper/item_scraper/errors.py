# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import traceback
import django.utils.timezone as tz
from datetime import datetime
from colorama import Fore, Back, Style

from core.models import ErrorLog, SITE_MODEL, STATUS_UNKNOWN


CATEGORY_ERROR = "Category"
DATABASE_ERROR = "Database"
PARSING_ERROR = "Parsing"
UNKNOWN_ERROR = "Unknown"


ERROR_CATEGORIES = sorted([
    CATEGORY_ERROR,
    DATABASE_ERROR,
    PARSING_ERROR,
    UNKNOWN_ERROR
])


STATUS_OK = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2
STATUS_UNKNOWN = 3


class SpiderException(Exception):
    """Represents an error that happens when scraping a site."""

    def __init__(self, spider_name, field_name='<Unknown field>',
                 url='<Unknown URL>', exception=None, level=STATUS_UNKNOWN,
                 message="", category=UNKNOWN_ERROR):
        self.spider_name = spider_name
        self.field_name = field_name
        self.url = url
        self.level = level
        self.ex_name = exception.__class__.__name__ if exception else None
        self.ex_msg = message

        self.time = tz.now()

        message_tuple = (self.field_name, self.ex_name, self.ex_msg, self.url)
        color_tuple = (Fore.RED,) + message_tuple + (Fore.RESET,)

        self.message = "%s: %s (%s). URL: %s" % message_tuple
        self.color_message = "%s%s: %s (%s). URL: %s%s" % color_tuple

        self.category = category
        self.trace = traceback.format_exc()

    def log(self):
        """Print the message to the console."""
        print(self.color_message, file=sys.stderr)

    def store(self):
        """Create an ErrorLog object from the information in the exception and save it
in the database."""

        ErrorLog.objects.create(
            site=SITE_MODEL.objects.get(spider_name=self.spider_name),
            date_time=self.time,
            exception_name=self.ex_name,
            exception_message=self.ex_msg,
            category=self.category,
            exception_trace=self.trace[:200],
            error_level=self.level,
        )

    def __unicode__(self):
        return repr(self.message)


class SpiderMissingValueException(SpiderException):
    pass


def raise_missing_value(spider_name, field_name='<Unknown field>',
                        url='<Unknown URL>', exception=None,
                        level=STATUS_UNKNOWN, message="",
                        category=UNKNOWN_ERROR):
    """Create and store a missing value exception."""

    ex = SpiderMissingValueException(spider_name=spider_name,
                                     field_name=field_name,
                                     url=url,
                                     exception=exception,
                                     level=level,
                                     message=message,
                                     category=category)
    ex.log()
    ex.store()
