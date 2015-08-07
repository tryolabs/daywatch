from core.models import ITEM_MODEL, MERCHANT_MODEL, SoldCount, \
    SITE_MODEL, Run

from rest_framework import serializers
import json


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.Field(source='category_name')
    currency = serializers.Field(source='currency_code')
    start = serializers.Field(source='date_time')
    end = serializers.Field(source='end_date_time')
    sales_log = serializers.Field(source='get_sold_count_log')

    class Meta:
        model = ITEM_MODEL
        fields = (
            # Model fields
            'hash_id', 'offer', 'url', 'category', 'description', 'site',
            'currency', 'price', 'discount', 'sold_count', 'city',
            'merchant', 'image_url', 'start', 'end', 'active',
            'sold_count',
            # Computed fields
            'sales_log',
        )


class MerchantSerializer(serializers.ModelSerializer):
    items_sold = serializers.Field(source='items_sold')
    sales_volume = serializers.Field(source='sales_volume')
    items_offered = serializers.Field(source='items_offered')

    class Meta:
        model = MERCHANT_MODEL
        fields = (
            # Model fields
            'id', 'name', 'lat', 'lon', 'address', 'phone', 'website', 'email',
            # Computed fields
            'items_sold', 'sales_volume', 'items_offered'
        )


class SiteSerializer(serializers.ModelSerializer):
    runs = serializers.Field(source='get_runs')

    class Meta:
        model = SITE_MODEL
        fields = (
            # Model fields
            'id', 'name', 'url', 'spider_name', 'spider_enabled', 'country',
            # Computed fields
            'runs',
        )
