# -*- coding: utf-8 -*-

import re

from core.models import Currency, Country, STATUS_CRITICAL
from core.scraper.item_scraper.errors import raise_missing_value, PARSING_ERROR


DISCOUNT_REGEXP = r"(.*\s|^)(?P<discount>(\-)?[0-9]+(\.[0-9]+)?)(\s)*%(\s.*|$)"

FLOAT_REGEXP = r"(\s*)(?P<float>(\-)?(\s*)([0-9]+,)?[0-9]+(\.[0-9]+)?)(\s*)"
INTEGER_REGEXP = r"(.*\s|^)(?P<integer>(\-)?[0-9]+)(\s.*|$)"

GMAP_REGEXP = r"(center|ll|q|markers)*=([+-]*\d+\.\d+),( )*([+-]*\d+\.\d+)"

PRICE_REGEXP_LEFT = r"(.*\s|^)"
PRICE_REGEXP_RIGHT = r"(\s)*(?P<price>(\-)?[0-9]+(\.[0-9]+)?)(\s.*|$)"


def make_price_regex(currency_regex):
    """Return the regexp for a price, given the regex for a particular currency.

    """
    return PRICE_REGEXP_LEFT + currency_regex + PRICE_REGEXP_RIGHT


def parse_float_discount(text):
    m = re.match(DISCOUNT_REGEXP, text, flags=re.DOTALL)
    return float(m.group("discount"))


def parse_float_price(text, country, decimal_mark):
    if decimal_mark == ',':
        text = text.replace('.', '').replace(',', '.')
    else:
        text = text.replace(',', '')

    m = re.match(make_price_regex(r"\$"), text, flags=re.DOTALL)
    if m:
        country = Country.objects.get(code=country)
        return (float(m.group("price")),
                Currency.objects.get(country=country))

    for curr in Currency.objects.all():
        m = re.match(make_price_regex(curr.regex), text, flags=re.DOTALL)
        if m:
            return (float(m.group("price")), curr)

    raise Exception("Price not matched: " + text)


def parse_en_float_str(text):
    m = re.search(FLOAT_REGEXP, text, flags=re.DOTALL)
    s = m.group("float").replace(',', '')
    return re.subn('\s*', '', s)[0]


def parse_int(text):
    m = re.match(INTEGER_REGEXP, text, flags=re.DOTALL)
    return int(m.group("integer"))


def parse_discount(text, loader_context):
    try:
        return parse_float_discount(text)
    except Exception as e:
        raise_missing_value(
            spider_name=loader_context['spider_name'],
            field_name='discount',
            url=loader_context['url'],
            exception=e,
            level=STATUS_CRITICAL,
            message="Could not parse discount from '%s'" % text,
            category=PARSING_ERROR
        )
        return None


def parse_sold_count(text, loader_context):
    try:
        text = text.replace(",", "").replace(".", "")
        n = parse_int(text)
        return n
    except Exception as e:
        raise_missing_value(
            spider_name=loader_context['spider_name'],
            field_name='sold_count',
            url=loader_context['url'],
            exception=e,
            level=STATUS_CRITICAL,
            message="Could not parse sold count from '%s'" % text,
            category=PARSING_ERROR
        )
        return None


def parse_price_currency(text, loader_context):
    try:
        data = parse_float_price(text, loader_context['country'],
                                 loader_context['decimal_mark'])
        return data
    except Exception as e:
        raise_missing_value(
            spider_name=loader_context['spider_name'],
            field_name='price',
            url=loader_context['url'],
            exception=e,
            level=STATUS_CRITICAL,
            message="Could not parse price from '%s'." % text,
            category=PARSING_ERROR
        )
        return None


def whitespace_trimmer(text, loader_context):
    """
    Removes all whitespace at either end of the string and replaces every
    substring with more than one internal space with a single space.
    Example: '  foo   bar baz   ' -> 'foo bar baz'
    """
    return re.sub(r'\s+', ' ', text.strip())


def parse_google_map(text, loader_context):
    """Returns a (lat,long) pair of floats from a Google Maps URL."""
    latlong = re.search(GMAP_REGEXP, text)
    if latlong:
        if len(latlong.groups()) == 4:
            return (float(latlong.groups()[-3]), float(latlong.groups()[-1]))
        else:
            return (float(latlong.groups()[-2]), float(latlong.groups()[-1]))
    else:
        return None
