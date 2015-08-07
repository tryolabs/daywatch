import json
from datetime import datetime

from django.db import models
from django.forms.models import model_to_dict
from rest_framework.response import Response

from core.models import ITEM_MODEL, MERCHANT_MODEL, SITE_MODEL, \
    Run, has_access, user_country_access
from gui.forms import RESULT_TYPE_CHOICES
from api.serializers import ItemSerializer, MerchantSerializer, \
    SiteSerializer
from .base import DayWatchModelView, DayWatchManualView
import core.analytics as analytics


class ItemView(DayWatchModelView):
    """
    List items.
    """

    model = ITEM_MODEL
    serializer_class = ItemSerializer

    filter_fields = [
        ('min_price', 'price__gte'),
        ('max_price', 'price__lte'),
        ('min_discount', 'discount__gte'),
        ('max_discount', 'discount__lte'),
        ('start', 'date_time__gte'),
        ('end', 'date_time__lte'),
        'category', 'site', 'merchant', 'active',
    ]

    def filter_user(self, user):
        countries = user_country_access(user)
        return self.queryset.filter(site__country__in=countries)


class MerchantView(DayWatchModelView):
    """
    List merchants, optionally within a location range.
    """

    model = MERCHANT_MODEL
    serializer_class = MerchantSerializer

    filter_fields = [
        ('min_lat', 'lat__gte'), ('max_lat', 'lat__lte'),
        ('min_lon', 'lat__gte'), ('max_lon', 'lat__lte'),
    ]

    def get_queryset(self):
        self.queryset = super(MerchantView, self).get_queryset()
        radius = self.ex('radius')
        lat = self.ex('lat')
        lon = self.ex('lon')
        if radius and lat and lon:
            radius = float(radius)
            lat = float(lat)
            lon = float(lon)
            lat_range = (lat-radius, lat+radius)
            lon_range = (lon-radius, lon+radius)
            self.queryset = self.queryset.filter(lat__range=lat_range,
                                                 lon__range=on_range)
            self.queryset = self.queryset.exclude(lat__isnull=True,
                                                  lon__isnull=True)
        return self.queryset


class SiteView(DayWatchModelView):
    """
    List sites in countries the user has access to.
    """

    model = SITE_MODEL
    serializer_class = SiteSerializer

    filter_fields = [
        'name', 'spider_name', 'spider_enabled', 'country',
    ]

    def filter_user(self, user):
        return self.queryset.filter(country__in=user_country_access(user))

DATE_FORMAT = '%Y-%m-%d'


def parse_date(date_string):
    try:
        return datetime.strptime(date_string, DATE_FORMAT)
    except:
        # Wrong date format or date_string is None
        return None


class DjangoJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, models.Model):
            return model_to_dict(obj)
        return JSONEncoder.default(self, obj)


class AnalyticsView(DayWatchManualView):
    """
    Access the functionality of the analytics panel from the API.
    """

    def get(self, request, format=None):
        site_ids = json.loads(self.ex('sites'))
        result_type = self.ex('result_type')
        start_date = parse_date(self.ex('start_date'))
        end_date = parse_date(self.ex('end_date'))

        sites = [SITE_MODEL.objects.get(id=site_id)
                 for site_id in site_ids]
        if start_date and end_date:
            items = ITEM_MODEL.objects.filter(site__in=sites,
                                              date_time__gte=start_date,
                                              date_time__lte=end_date)
        else:
            items = ITEM_MODEL.objects.filter(site__in=sites)

        if result_type == 'sales':
            result = analytics.sales_analysis(items)
        elif result_type == 'offered':
            result = analytics.offered_analysis(items)
        elif result_type == 'sold':
            result = analytics.sold_analysis(items)

        json_result = json.loads(json.dumps(result, cls=DjangoJSONEncoder))
        json_result.update({'result_type': result_type})
        return Response(json_result)
