# -*- coding: utf-8 -*-

from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_delete, pre_delete

from south.modelsinspector import add_introspection_rules

from core.fields import MultiSelectField
from core.general import PANEL_CHOICES
from core.settings import HOST_NAME_CHOICES, DW_DATE_FORMAT
from core.utils import convert_currency

# South introspection rules for custom fields
add_introspection_rules([], [r'^core.fields.MultiSelectField'])

# World models


class Language(models.Model):
    """Represents a language, where `code` is the ISO language code and `name` is
    the (English) name of the language.

    """
    code = models.CharField(max_length=3)
    name = models.TextField(max_length=255)

    def __unicode__(self):
        return self.name


class Country(models.Model):
    """A country is where Sites are based. The `name` is the English name of the
    country, `timezone` the TZ database name of the country's main timezone
    (e.g., 'America/Chicago'), and `code` the ISO 3166-1 alpha-2 code of the
    country.

    The `lang` is the country spoken in the language. This is used by the
    classifier to choose an appropriate language for classifying items. The
    language option, however, can be overriden in particular spiders.

    """
    name = models.CharField(unique=True, max_length=255)
    timezone = models.CharField(unique=True, max_length=100)
    code = models.CharField(unique=True, max_length=5)
    lang = models.ForeignKey(Language)

    class Meta:
        verbose_name_plural = "countries"

    def __unicode__(self):
        return self.name


class Currency(models.Model):
    """The currency a price is shown in. A currency is associated to a `country`,
    has an ISO code `iso_code`, a matching regular expression `regex` and a name
    `text`.

    The `us_change` field represents the conversion rate to dollars. This is
    updated periodically using the `update_currencies` method.

    """
    country = models.OneToOneField(Country)
    iso_code = models.CharField(max_length=5)
    us_change = models.FloatField()
    regex = models.CharField(max_length=30, blank=True)
    text = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "currencies"

    def __unicode__(self):
        return self.text

    @classmethod
    def convert(cls, currency_from, currency_to):
        return convert_currency(currency_from, currency_to)

    @classmethod
    def update_currencies(cls):
        currency_list = Currency.objects.all()
        for currency in currency_list:
            currency.us_change = Currency.convert(currency.iso_code, 'USD')
            currency.save()
            # cache value for 25 hs
            cache.set(currency.currency, currency.us_change,
                      CURRENCY_UPDATE_TIMEOUT)

    @classmethod
    def currency_usd(cls, currencyFrom):
        change = cache.get(currencyFrom)
        if change is None:
            Currency.update_currencies()
            change = cache.get(currencyFrom)
        return change


# Account types
ACCOUNT_NONE = 'NONE'
ACCOUNT_TRIAL = 'TRIAL'
ACCOUNT_LITE = 'LITE'
ACCOUNT_FULL = 'FULL'

ACCOUNT_TYPE_CHOICES = (
    (ACCOUNT_NONE, 'None'),
    (ACCOUNT_TRIAL, 'Trial'),
    (ACCOUNT_LITE, 'Lite'),
    (ACCOUNT_FULL, 'Full'),
)

MISSING_VALUE = None


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    panel_access = MultiSelectField(max_length=300, choices=PANEL_CHOICES,
                                    null=True, blank=True)
    country_access = models.ManyToManyField(Country)

    def __unicode__(self):
        return self.user.username


def user_country_access(user):
    """Return the countries the User has access to."""
    return UserProfile.objects.get(user=user).country_access.all()


def has_access(user, country):
    """Does the user have access to this country?"""
    return country in user_country_access(user)


class Category(models.Model):
    """Every Item is assigned a category by the categorizer. A category only has a
`name`.

    """
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


# Core models


class Site(models.Model):
    """A site sells Items through Merchants, and is the target of the scrapers.

    """
    name = models.CharField(unique=True, max_length=255)
    image_path = models.CharField(max_length=200)
    url = models.URLField()
    spider_name = models.CharField(max_length=128)
    spider_enabled = models.BooleanField()
    host_name = models.CharField(max_length=128, choices=HOST_NAME_CHOICES)
    country = models.ForeignKey(Country)
    shows_sold_count = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def get_runs(self):
        """Return a list of dictionaries representing Run information."""

        runs = Run.objects.filter(site=self.id)
        return [{'start': run.start,
                 'end': run.end,
                 'offers': run.scraped,
                 'errors': self.get_errors(run.start, run.end)}
                for run in runs]

    def get_errors(self, start, end):
        """Return a list of dictionaries with ErrorLog information."""

        errors = ErrorLog.objects.filter(site=self.id,
                                         date_time__gte=start,
                                         date_time__lte=end)
        return [{'type': error.exception_name,
                 'message': error.exception_message}
                for error in errors]

SITE_MODEL = Site


class Merchant(models.Model):
    """A merchant sells Items through a Site."""
    name = models.CharField(max_length=200)
    lat = models.DecimalField(blank=True, null=True, max_digits=10,
                              decimal_places=7)
    lon = models.DecimalField(blank=True, null=True, max_digits=10,
                              decimal_places=7)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(max_length=500, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def items_associated(self):
        """A list of the items sold by this merchant."""
        return ITEM_MODEL.objects.filter(merchant=self)

    def items_offered(self):
        """The number of items sold by this merchant."""
        return self.items_associated().count()

    def items_sold(self):
        """The number of items sold by this merchant."""
        items = self.items_associated()
        return items.aggregate(total=Sum('sold_count'))['total']

    def sales_volume(self):
        """The sum of the product of price and items sold for all items sold by this
        merchant."""
        items = self.items_associated()
        return items.aggregate(total=Sum('sold_count',
                                         field='sold_count*price'))['total']

MERCHANT_MODEL = Merchant


class Item(models.Model):
    """The Item is the central object in DayWatch's architecture. It represents a
    piece of information scraped from a Site and is aggregated by the different
    panels.

    """
    offer = models.TextField(max_length=255, null=True)
    url = models.URLField(max_length=500, null=True)
    hash_id = models.CharField(max_length=500, db_index=True, null=True)
    description = models.TextField(max_length=5000, null=True)
    raw_html = models.TextField(null=True)
    image_url = models.URLField(null=True)
    date_time = models.DateTimeField(db_index=True)
    category = models.ForeignKey(Category, blank=True, null=True)

    # Custom fields
    currency = models.ForeignKey(Currency, null=True, unique=False)
    price = models.FloatField(null=True)
    discount = models.FloatField(null=True)
    sold_count = models.IntegerField(null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    end_date_time = models.DateTimeField(null=True)
    active = models.NullBooleanField()

    site = models.ForeignKey(SITE_MODEL)
    merchant = models.ForeignKey(MERCHANT_MODEL)

    def __unicode__(self):
        return self.offer

    def total_sales(self):
        """The product of price and sold count."""
        if self.sold_count == MISSING_VALUE or self.price == MISSING_VALUE:
            return 0
        else:
            return self.price * self.sold_count

    def category_name(self):
        """The name of the item's category."""
        return self.category.name

    def currency_code(self):
        """The code of the item's price currency."""
        return self.currency.iso_code

    def get_sold_count_log(self):
        logs = SoldCount.objects.filter(deal=self.id)
        return [{'date': log.date,
                 'sold': log.value}
                for log in logs]

    @classmethod
    def remove_duplicates(cls, filters=None):
        """Search the database for duplicate items, removing them."""
        if filters:
            deals = cls.objects.filter(**filters)
        else:
            deals = cls.objects.all()
        for deal in deals:
            # Find duplicates to this deal
            others = cls.objects.filter(offer=deal.offer,
                                        company=deal.company,
                                        price=deal.price,
                                        discount=deal.discount,
                                        sold_count=deal.sold_count,
                                        city=deal.city)
            if others:
                others.delete()

ITEM_MODEL = Item


# Configure items


def __delete_merchants(sender, **kwargs):
    """This is necessary to ensure associated objects are properly deleted."""
    deleted_site = kwargs['instance']
    deals = ITEM_MODEL.objects.filter(site=deleted_site)
    for deal in deals:
        try:
            deal.merchant.delete()
        except:
            pass

pre_delete.connect(__delete_merchants, sender=SITE_MODEL)


# Temporal Items


class BufferedItem(ITEM_MODEL):
    pass


class TestItem(ITEM_MODEL):
    pass


class ActivityLog(models.Model):
    user = models.ForeignKey(User)
    user_agent = models.CharField(max_length=200)
    referer = models.TextField(max_length=700, null=True)
    query_path = models.CharField(max_length=300, null=True)
    absolute_uri = models.TextField(max_length=800, null=True)
    date_time = models.DateTimeField()

    def __unicode__(self):
        return self.user.username + ' ' + self.date_time.strftime('%D %T')

STATUS_UNKNOWN = 0
STATUS_WARNING = 1
STATUS_ERROR = 2
STATUS_CRITICAL = 3

ERROR_CHOICES = (
    (STATUS_UNKNOWN,  'Unknown'),
    (STATUS_WARNING,  'Warning'),
    (STATUS_ERROR,    'Error'),
    (STATUS_CRITICAL, 'Critical'),
)


class ErrorLog(models.Model):
    """An error raised by a spider during scraping."""
    site = models.ForeignKey(SITE_MODEL)
    date_time = models.DateTimeField()
    exception_name = models.CharField(max_length=30, null=True)
    exception_message = models.TextField(max_length=200, null=True)
    category = models.TextField(max_length=50, null=True)
    exception_trace = models.TextField(max_length=200, null=True)
    error_level = models.IntegerField(choices=ERROR_CHOICES)

    def __unicode__(self):
        if self.exception_name and self.exception_message:
            return self.exception_name + ' - ' + self.exception_message
        else:
            return "<No name or message>"


class SoldCount(models.Model):
    """Represents that, at `date`, `value` offers for the item `item` had been
    sold.

    """
    deal = models.ForeignKey(ITEM_MODEL)
    date = models.DateTimeField()
    value = models.IntegerField()

    def __unicode__(self):
        return self.date.strftime(DW_DATE_FORMAT) + ' -> ' + \
            str(self.value)


class Run(models.Model):
    """A run represents an instance of a spider being run. `site` is the site the
    spider belongs to, `start` and `end` are the start/end times, and `scraped`
    is the number of items scraped.

    """
    site = models.ForeignKey(SITE_MODEL)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
    scraped = models.IntegerField()

    def __unicode__(self):
        return self.start.strftime(DW_DATE_FORMAT) + ' - ' + \
            self.end.strftime(DW_DATE_FORMAT) + ' (' + str(self.scraped) \
            + ')'
