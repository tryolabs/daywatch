# -*- coding: utf-8 -*-

from item_scraper.base import Extractor
from item_scraper.parsers import parse_google_map


def parse_gmap(match):
    return parse_google_map(match, None)


def lat(xpath):
    """Extract the latitude from an XPath to a Google Map."""

    return Extractor(xpath=xpath, fn=lambda matches, response:
                     parse_google_map(matches[0], None)[0])


def lon(xpath):
    """Extract the longitude from an XPath to a Google Map."""

    return Extractor(xpath=xpath, fn=lambda matches, response:
                     parse_google_map(matches[0], None)[1])
