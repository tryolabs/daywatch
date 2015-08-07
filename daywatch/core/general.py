# -*- coding: utf-8 -*-

import traceback
import json

from django.conf import settings
from django.http import HttpResponse
from django.core.mail import mail_admins
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy


FIELD_OFFER = 'offer'
FIELD_PRICE = 'price'
FIELD_TOTAL_SALES_LOCAL = 'total_sales_local'
FIELD_TOTAL_SALES_USD = 'total_sales_usd'
FIELD_CURRENCY = 'currency'
FIELD_DISCOUNT = 'discount'
FIELD_SOLD_COUNT = 'sold_count'
FIELD_DESCRIPTION = 'description'
FIELD_DATE_TIME = 'date_time'
FIELD_CATEGORY = 'category'
FIELD_IS_MAIN_DEAL = 'is_main_deal'
FIELD_RAW_HTML = 'raw_html'
FIELD_URL = 'url'
FIELD_OFFER_ID = 'hash_id'
FIELD_MISS_CHECK = 'miss_check'
FIELD_FINISHED = 'finished'

FIELD_CITY = 'city'
FIELD_MERCHANT_NAME = 'merchant_name'
FIELD_MERCHANT_LAT = 'merchant_lat'
FIELD_MERCHANT_LON = 'merchant_lon'
FIELD_MERCHANT_ADDRESS = 'merchant_address'
FIELD_MERCHANT_POSTCODE = 'merchant_postcode'
FIELD_MERCHANT_PHONE = 'merchant_phone'
FIELD_MERCHANT_WEBSITE = 'merchant_website'
FIELD_MERCHANT_EMAIL = 'merchant_email'

# Countries that show numbers in their local currency, not in USD
# Mostly Asia countries
LOCAL_CURRENCY_COUNTRIES = [
    'sg',
    'my',
    'ph',
    'id',
    'th',
]


class Status:
    OK = 0
    ERROR = 1
    ERROR_COMMIT = 2
    message = ["ok", "Error, could not commit to db"]


def get_status(request):
    return {
        'request': request,
        'status': get_user_status(request.user),
        'user': request.user
    }


def get_user_status(user):
    if user.is_authenticated():
        logged_in = True
    else:
        logged_in = False
    return {"logged_in": logged_in}


def result(status_code, status_message=None, data=None):
    if status_code == Status.ERROR:
        res = {"status_code": status_code, "status_message": status_message}
    else:
        res = {"status_code": status_code,
               "status_message": Status.message[status_code]}
    if data:
        res = dict(res, **data)
    return res


class JsonResponse(HttpResponse):
    def __init__(self, obj):
        self.original_obj = obj
        HttpResponse.__init__(self, self.serialize())
        self["Content-Type"] = "text/javascript"

    def serialize(self):
        return(json.dumps(self.original_obj))


def error_response(request, exception):
    exceptionName = 'Exception: ' + exception.__class__.__name__
    exceptionMessage = 'Message: ' + str(exception)
    trace = 'Trace: ' + traceback.format_exc()
    if not settings.DEBUG:
        mail_admins('Error Detected',
                    (exceptionName + '\n' +
                     exceptionMessage + '\n' + trace + '\n'),
                    fail_silently=False)
    return render_to_response(
        'main/error.html',
        {
            'exceptionName': exceptionName,
            'exceptionMessage': exceptionMessage,
            'trace': trace
        },
        context_instance=RequestContext(request)
    )


def warning_response(request, message):
    context = get_status(request)
    context['message'] = message
    return render_to_response(
        'main/warning.html',
        context,
        context_instance=RequestContext(request)
    )


# Decorators


ANALYTICS_PERM = 'ANALYTICS'
SPIDERS_PERM = 'SPIDERS'
ITEMS_PERM = 'ITEMS'
TRENDS_PERM = 'TRENDS'

PANEL_CHOICES = (
    (ANALYTICS_PERM, 'Analytics Panel'),
    (SPIDERS_PERM, 'Spiders Panel'),
    (ITEMS_PERM, 'Items Panel'),
    (TRENDS_PERM, 'Trends Panel'),
)

VIEW_PERMISSIONS = {
    'analytics_panel': [ANALYTICS_PERM],
    'analytics_div': [ANALYTICS_PERM],
    'spider_listings': [SPIDERS_PERM],
    'spider_listings_div': [SPIDERS_PERM],
    'item_listings': [ITEMS_PERM],
    'item_div': [ITEMS_PERM],
    'trends_listings': [TRENDS_PERM],
    'trends_div': [TRENDS_PERM],
}


def permission_required(f):
    def call(request, *args, **kwargs):
        for credential in VIEW_PERMISSIONS[f.func_name]:
            try:
                profile = request.user.get_profile()
                if credential not in profile.panel_access:
                    return warning_response(request, ugettext_lazy(
                        (" Sorry, you don't have access to this panel." +
                         " Please request access to our team.")))
            except:
                return warning_response(request, ugettext_lazy(
                    (" Sorry, you don't have access to this panel." +
                     " Please request access to our team.")))
        return f(request)

    call.__doc__ = f.__doc__
    call.__name__ = f.__name__
    call.__dict__.update(f.__dict__)
    return call


def catch_error(f):
    def call(request, *args, **kwargs):
        if settings.DEBUG:
            return f(request)
        else:
            try:
                return f(request)
            except Exception as e:
                return error_response(request, e)
    call.__doc__ = f.__doc__
    call.__name__ = f.__name__
    call.__dict__.update(f.__dict__)
    return call
