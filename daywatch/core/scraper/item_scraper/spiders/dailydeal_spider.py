# -*- coding: utf-8 -*-

from core.general import FIELD_TOTAL_SALES_LOCAL, FIELD_TOTAL_SALES_USD

from base import DayWatchSpider
from fields import *


class DailyDealSpider(DayWatchSpider):
    fields_to_categorize = [F_DESC, F_OFFER]

    calculcated_fields = [F_CATEGORY, FIELD_TOTAL_SALES_LOCAL, \
                          FIELD_TOTAL_SALES_USD]
