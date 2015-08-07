# -*- coding: utf-8 -*-

"""This module implements functions for analyzing sets of items and sites to
produce statistical reports or simply data for plotting
"""

from django.db.models import Sum

from core.models import SITE_MODEL, ITEM_MODEL, Category
from core.utils import percentage


# Utilities


def count(qs):
    """Count a queryset, or list of items."""
    try:
        return qs.count()
    except:
        return len(qs)


def distinct_sites(items):
    """A list of distinct sites that appear in `items`."""
    return [SITE_MODEL.objects.get(id=site['site']) for site in
            items.values('site').distinct()]


def distinct_categories(items):
    """A list of distinct categories that appear in `items`."""

    def get_category(id):
        if id:
            return Category.objects.get(id=id)
        else:
            return None

    categories = [get_category(category['category']) for category in
                  items.values('category').distinct()]

    return [category for category in categories if category]


# Analytics Panel functions


def site_items_per_category(items):
    """For every category, a list of (site,items) pairs with the items site has sold
    in that category.

    """
    data = {}
    for category in distinct_categories(items):
        category_items = items.filter(category=category)
        sites = distinct_sites(category_items)
        data[category.name] = []
        for site in sites:
            site_items = category_items.filter(site=site)
            data[category.name] += [(site,
                                     site_items)]
    return data


def category_items_per_site(items):
    """For every site, a list of (category,items) pairs with the items for that
    category.

    """
    data = {}
    for site in distinct_sites(items):
        site_items = items.filter(site=site)
        categories = distinct_categories(site_items)
        data[site.name] = []
        for category in categories:
            category_items = site_items.filter(site=site)
            data[site.name] = [(category,
                                category_items)]
    return data


def items_per_site(items):
    """For every distinct site in items, a list of (site,items) pairs with the items
    sold by that site.

    """
    return [(site, items.filter(site=site)) for site in
            distinct_sites(items)]


def items_per_cat(items):
    """For every distinct category in items, a list of (category,items) pairs with
    the items sold in that category.

    """
    return [(cat, items.filter(category=cat)) for cat in
            distinct_categories(items)]


# Sales


def total_sales(items):
    """The total sales for all items."""
    try:
        return items.aggregate(total=Sum('sold_count',
                                         field='sold_count*price'))['total']
    except:
        return sum([item.sold_count*item.price for item in
                    items if
                    item.sold_count is not None and
                    item.price is not None])


def sales_per_site(items):
    """The total sales for every site in `items`."""
    return [(site, total_sales(site_items))
            for site, site_items in items_per_site(items)]


def sales_per_category(items):
    """The total sales for every category in items."""
    return [(cat, total_sales(cat_items))
            for cat, cat_items in items_per_cat(items)]


def category_sales_per_site(items):
    """For every site, a (category, count) pair with the sales for the category by
    that site.

    """
    return [(site,
             [(cat, total_sales(cat_items)) for cat, cat_items in
              categories])
            for site, categories in
            category_items_per_site(items).iteritems()]


def site_sales_per_category(items):
    """For every category, a (site, count) pair with the sales for the site in that
    cateogory.

    """
    return [(site,
             [(cat, total_sales(cat_items)) for cat, cat_items in
              categories])
            for site, categories in
            site_items_per_category(items).iteritems()]


def sales_share_by_site(items):
    """Each site's share in the sales volume."""
    total = total_sales(items)
    return [(site, percentage(sold, total))
            for site, sold in sales_per_site(items)]


def sales_share_per_category(items):
    """Each category's share in the sales volume."""
    total = total_sales(items)
    return [(cat, percentage(sold, total))
            for cat, sold in sales_per_category(items)]

# Number of items offered


def offered_per_site(items):
    """The number of items offerd per site."""
    return [(site, count(site_items))
            for site, site_items in items_per_site(items)]


def offered_per_category(items):
    """The number of items offerd per category."""
    return [(cat, count(cat_items))
            for cat, cat_items in items_per_cat(items)]


def category_offered_per_site(items):
    """For every site, a (category, count) pair with the number of items offered for
    the category by that site.

    """
    return [(site,
             [(cat, count(cat_items)) for cat, cat_items in
              categories])
            for site, categories in
            category_items_per_site(items).iteritems()]


def site_offered_per_category(items):
    """For every category, a (site, count) pair with the number of items offered by
    the site in that category.

    """
    return [(site,
             [(cat, count(cat_items)) for cat, cat_items in
              categories])
            for site, categories in
            site_items_per_category(items).iteritems()]


def offered_share_by_site(items):
    """Each site's share in the number of offered items."""
    total = count(items)
    return [(site, percentage(sold, total))
            for site, sold in offered_per_site(items)]


def offered_share_per_category(items):
    """Each category's share in the number of offered items."""
    total = count(items)
    return [(site, percentage(sold, total))
            for site, sold in offered_per_category(items)]


# Number of items sold


def total_sold(items):
    """Total number of items sold for all items."""
    return items.aggregate(total=Sum('sold_count'))['total']


def sold_per_site(items):
    """Number of items sold per site."""
    return [(site, total_sold(site_items))
            for site, site_items in items_per_site(items)]


def sold_per_category(items):
    """Number of items sold per category."""
    return [(cat, total_sold(cat_items))
            for cat, cat_items in items_per_cat(items)]


def category_sold_per_site(items):
    """For every site, a (category, count) pair with the number of items sold in
    that category by the site.

    """
    return [(site,
             [(cat, total_sold(cat_items)) for cat, cat_items in
              categories])
            for site, categories in
            category_items_per_site(items).iteritems()]


def site_sold_per_category(items):
    """For every category, a (site, count) pair with the number of items sold by the
    site in that category.

    """
    return [(site,
             [(cat, total_sold(cat_items)) for cat, cat_items in
              categories])
            for site, categories in
            category_items_per_site(items).iteritems()]


def sold_share_by_site(items):
    """Each site's share in the number of items sold."""
    total = total_sold(items)
    return [(site, percentage(sold, total))
            for site, sold in sold_per_site(items)]


def sold_share_per_category(items):
    """Each category's share in the number of items sold."""
    total = total_sold(items)
    return [(site, percentage(sold, total))
            for site, sold in sold_per_category(items)]


# Classes


class ItemAnalysis(object):
    """Base class for all item analyses."""


class SalesAnalysis(ItemAnalysis):
    """Sales analysis on a collection of items."""

    def __init__(self, items):
        self.sales = total_sales(items)
        self.result_type_per_site = sales_per_site(items)
        self.result_type_per_cat = sales_per_category(items)
        self.cat_result_type_per_site = category_sales_per_site(items)
        self.site_result_type_per_cat = site_sales_per_category(items)
        self.result_type_share_per_site = sales_share_by_site(items)
        self.result_type_share_per_cat = sales_share_per_category(items)


class OfferedAnalysis(ItemAnalysis):
    """Offered count analysis on a collection of items."""

    def __init__(self, items):
        self.result_type_per_site = offered_per_site(items)
        self.result_type_per_cat = offered_per_category(items)
        self.cat_result_type_per_site = category_offered_per_site(items)
        self.site_result_type_per_cat = site_offered_per_category(items)
        self.result_type_share_per_site = offered_share_by_site(items)
        self.result_type_share_per_cat = offered_share_per_category(items)


class SoldAnalysis(ItemAnalysis):
    """Sold count analysis on a collection of items."""

    def __init__(self, items):
        self.result_type_per_site = sold_per_site(items)
        self.result_type_per_cat = sold_per_category(items)
        self.cat_result_type_per_site = category_sold_per_site(items)
        self.site_result_type_per_cat = site_sold_per_category(items)
        self.result_type_share_per_site = sold_share_by_site(items)
        self.result_type_share_per_cat = sold_share_per_category(items)


# Trends Panel functions


def items_sum(items, field):
    """Take a list of items, and return the sum of a given field."""
    if items:
        sum = 0
        for item in items:
            value = getattr(item, field)
            if type(value) in (int, float):
                sum += value
        return sum
    else:
        return None


def items_average(items, field):
    """Take a list of items, and return the average of a given field."""
    sum = items_sum(items, field)
    if sum:
        len = items.count()
        return sum/len
    else:
        return None
