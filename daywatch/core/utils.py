# -*- coding: utf-8 -*-

from lxml import etree
import urllib
import urllib2
import logging
import time

from django.db.models.fields import BigIntegerField, DecimalField, FloatField, \
  IntegerField, PositiveIntegerField, PositiveSmallIntegerField, \
  SmallIntegerField

def make_logger():
    """Return a logger instance."""

    return logging.getLogger('django.request')


logger = make_logger()


def percentage(n, total):
    """If `total`=100 and `n`=50 => 50%"""

    if n is None:
        return 0
    else:
        return (n*100)/total


def datetime_to_unix(datetime):
    """Return the Unix timestamp (integer) corresponding to the datetime."""

    return int(time.mktime(datetime.timetuple()))


BASE_URL = r'http://query.yahooapis.com/v1/public/yql?q='
QUERY = urllib.quote('select * from yahoo.finance.xchange where pair in ("')
QUERY_SUFFIX = '")&env=store://datatables.org/alltableswithkeys'


def convert_currency(currency_from, currency_to):
    """The conversion rate from currency_from to currency_to, both of which must be
    ISO codes.

    """

    try:
        query = BASE_URL + QUERY + currency_from + currency_to + QUERY_SUFFIX
        data = etree.XML(urllib2.urlopen(query).read())
        rate = data.xpath('//Rate')[0].text
        return float(rate)
    except:
        logger.error("Can't convert currencies: %s -> %s", currency_from,
                     currency_to)

# Class tools

def field_list(model_class):
    """Return a list of (field_name, field_type) tuples for every field in the
    class.
    """
    return [(field.name, type(field)) for field in model_class._meta.fields]

def numeric_field_list(model_class):
    """Return a list of field names for every numeric field in the class."""

    def is_numeric(type):
        return type in [BigIntegerField, DecimalField, FloatField, IntegerField,
                        PositiveIntegerField, PositiveSmallIntegerField,
                        SmallIntegerField]

    fields = []
    for (field, type) in field_list(model_class):
        if is_numeric(type):
            fields += [field]
    return fields
