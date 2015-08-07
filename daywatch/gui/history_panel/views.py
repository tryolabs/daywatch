# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2011

@author: raul
'''

import calendar
from collections import defaultdict
from datetime import datetime, timedelta, date

from django.http import HttpResponse
from django.db.models import Sum, Count
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from gui.forms import PanelForm
from gui.history_panel.forms import HistoryComparisonForm, \
    HistoryPanelExportForm
from gui.defs import log_activity, get_style, get_style_ref, get_interval, \
    get_datatables_records

from core.services import deal_sold_count_log
from core.general import catch_error, get_status, \
    Status, result, JsonResponse, permission_required, warningResponse, \
    LOCAL_CURRENCY_COUNTRIES
from core.models import COMPANY_CHOICES, CATEGORY_CHOICES, \
    Category, CURRENCY_DICT, DayWatchSite, DayWatchItem


@catch_error
@log_activity
@login_required
def deal_list_date(request):
    context = get_status(request)
    style = get_style()
    style_ref = get_style_ref(style)

    company_name = request.GET.get('company_name')
    datetime_str = request.GET.get('start_date')
    country = request.GET.get('country')
    start_date_time = datetime.strptime(datetime_str, '%d %m %Y %H:%M:%S')
    categories = request.GET.get('categories')

    if categories:
        category_ids = [int(c_id) for c_id in categories.split(",")]
    else:
        categories = Category.objects.all()
        category_ids = []
        for category in categories:
            if category.name != 'root':
                category_ids.append(category.id)

    if company_name:
        items = DayWatchItem.objects.filter(
            company__name=company_name,
            start_date_time__year=start_date_time.year,
            start_date_time__month=start_date_time.month,
            start_date_time__day=start_date_time.day,
            category__id__in=category_ids
        )
    else:
        items = DayWatchItem.objects.filter(
            start_date_time__year=start_date_time.year,
            start_date_time__month=start_date_time.month,
            start_date_time__day=start_date_time.day,
            category__id__in=category_ids
        )

    context['items'] = items
    context['country'] = country
    context['style_ref'] = style_ref

    return render_to_response(
        'deal_list_date.html',
        context,
        context_instance=RequestContext(request)
    )


@catch_error
@log_activity
@login_required
def deal(request):
    context = get_status(request)
    item_id = request.GET.get('deal_id')
    is_active_deal = request.GET.get('last')
    country = request.GET.get('country')

    item = DayWatchItem.objects.get(hash_id=item_id)
    graph = deal_sold_count_log(item)
    try:
        dt = item.end_date_time - item.start_date_time
    except AttributeError:
        dt = datetime.now() - item.start_date_time

    if dt.days < 2:
        context['interval'] = '4 hours'
    else:
        context['interval'] = '1 day'

    context['item'] = item
    context['graph'] = graph

    return render_to_response(
        'deal.html',
        context,
        context_instance=RequestContext(request)
    )


@catch_error
@log_activity
@login_required
@permission_required
def history_listings(request):
    context = get_status(request)
    sites_countries = {}
    companies_show_sold = {}

    countries = DayWatchSite.objects.values_list('country',
                                                 flat=True).distinct()
    for country in countries:
        sites_countries[country] = {}
        sites = DayWatchSite.objects.filter(country=country)
        for site in sites:
            sites_countries[country][str(site.id)] = 1

    for site in DayWatchSite.objects.all():
        # We wont filter in this panel
        companies_show_sold[str(site.id)] = 1

    context['companies_countries'] = sites_countries
    context['companies_show_sold'] = companies_show_sold
    context['app'] = 'history_listings'

    if request.user.premium_access:
        context['form'] = HistoryPanelExportForm(
                               user=request.user,
                               initial=request.session.get('form_session'),
                        )
    else:
        context['form'] = PanelForm(
                                user=request.user,
                                initial=request.session.get('form_session')
                        )

    return render_to_response(
        'history_panel.html',
        context,
        context_instance=RequestContext(request)
    )


@catch_error
@log_activity
@login_required
@permission_required
def history_listings_div(request):
    #prepare the params
    context = get_status(request)
    form = HistoryPanelExportForm(user=request.user, data=request.GET)

    if form.is_valid():
        request.session['form_session'] = form.cleaned_data
        period = form.cleaned_data['period']
        style = get_style()
        style_ref = get_style_ref(style)
        user = request.user

        # Convert date parameters
        end_date = datetime.now()
        if period == 'last_30_d':
            start_date = datetime.now() - timedelta(days=30)
        elif period == 'last_15_d':
            start_date = datetime.now() - timedelta(days=15)
        elif period == 'last_7_d':
            start_date = datetime.now() - timedelta(days=7)
        elif period == 'custom':
            d = form.cleaned_data['start_date']
            start_date = datetime(d.year, d.month, d.day)
            d = form.cleaned_data['end_date']
            end_date = datetime(d.year, d.month, d.day, 23, 59)

        country = form.cleaned_data['country']
        context['use_local_currency'] = country in LOCAL_CURRENCY_COUNTRIES
        context['local_currency'] = CURRENCY_DICT[country]

        history_limit = 0
        out_of_range_error = False
        out_of_range_warning = False
        if not user.has_full_access_for_country(country):
            if user.week_history_limit > 0:
                #user is history limited, limit start and end dates
                week_limit = user.week_history_limit
                history_limit = datetime.now() - timedelta(weeks=week_limit)
                if end_date < history_limit:
                    out_of_range_error = True
                elif start_date < history_limit:
                    start_date = history_limit
                    out_of_range_warning = True
                history_limit = history_limit.date()

        # Get deals for this query
        if not out_of_range_error:
            player_ids = form.cleaned_data['players']
            player_ids = [int(p_id) for p_id in player_ids]

            if form.cleaned_data['all_categories']:
                items = DayWatchItem.objects.filter(
                    site__id__in=player_ids,
                    date_time__gte=start_date,
                    date_time__lte=end_date
                )
                categories = Category.objects.all()
                category_ids = []
                for category in categories:
                    if category.name != 'root':
                        category_ids.append(category.id)
            else:
                category_ids = form.cleaned_data['categories']
                category_ids = [int(c_id) for c_id in category_ids]
                items = DayWatchItem.objects.filter(
                    site__id__in=player_ids,
                    category__id__in=category_ids,
                    date_time__gte=start_date,
                    date_time__lte=end_date
                )
        else:
            items = DayWatchItem.objects.none()

        # Prepare and return results to upper layers
        context['items'] = items
        context['country'] = country
        context['style_ref'] = style_ref

        context['history_limit'] = history_limit
        context['out_of_range_error'] = out_of_range_error
        context['out_of_range_warning'] = out_of_range_warning

    # excel button clicked
    if form.data.get('excel'):
        if not request.user.premium_access:
            msg = " Sorry, Excel exports are limited to Premium Users."
            return warningResponse(request, _(msg))

        if not user.is_staff:
            # We limit exportable deals to a month and a half from today
            floor_date = datetime.now() - timedelta(weeks=7)
            context['items'] = context['items'].filter(
                                        start_date_time__gte=floor_date)

            if start_date < floor_date:
                context['floor_date_warn'] = floor_date

        filename = "DayWatch_report_%s" % (
            datetime.now().strftime("%d-%m-%Y_%H-%M"),
        )
        result = render_to_string(
            'includes/history_table_xls.html',
            context,
            context_instance=RequestContext(request)
        )
        response = HttpResponse(
            result,
            content_type='application/vnd.ms-excel;charset=utf-8'
        )
        content_disposition = 'attachment; filename="%s.xls"' % (filename,)
        response['Content-Disposition'] = content_disposition

        return response

    # Normal results rendering
    # col_index_name_map is required for correct sorting behavior
    index_name_map = {
        0: 'offer',
        1: 'company',
        2: 'start_date_time',
        3: 'end_date_time',
        4: 'price',
        5: 'price_usd',
        6: 'discount',
        7: 'category',
        8: 'is_main_deal',
        9: 'sold_count',
        10: 'total_sales_usd',
        11: 'merchant_name',
    }
    if context['use_local_currency']:
        index_name_map[10] = 'total_sales_local'

    json_template = 'includes/history_table_json.txt'

    return get_datatables_records(
        request, context['items'],
        index_name_map, context, json_template
    )


@login_required
@catch_error
@permission_required
@log_activity
def history_comparison(request):
    context = get_status(request)
    companies_countries = {}
    companies_show_sold = {}

    countries = DayWatchSite.objects.values_list('country',
                                                 flat=True).distinct()
    for country in countries:
        companies_countries[country] = {}
        sites = DayWatchSite.objects.filter(country=country)
        for site in sites:
            companies_countries[country][str(site.id)] = 1

    for site in DayWatchSite.objects.all():
        # We SHOULD filter in this panel, but not for now
        # TODO: Think about this view and how to mix it with the new DW
        companies_show_sold[str(site.id)] = 1

    context['companies_countries'] = companies_countries
    context['companies_show_sold'] = companies_show_sold
    context['app'] = 'history_comparison'
    context['form'] = HistoryComparisonForm(
        user=request.user,
        initial=request.session.get('form_session')
    )

    return render_to_response(
        'history_comparison.html',
        context,
        context_instance=RequestContext(request)
    )


### OPTIMIZED ###
@login_required
@catch_error
@permission_required
@log_activity
def history_comparison_div(request):
    context = get_status(request)
    form = HistoryComparisonForm(user=request.user, data=request.GET)

    if form.is_valid():
        request.session['form_session'] = form.cleaned_data
        style = get_style()

        period = form.cleaned_data['period']
        concept = form.cleaned_data['concept']

        today = date.today()

        if period == 'last_3_m':
            months = 3
        elif period == 'last_4_m':
            months = 4
        elif period == 'last_6_m':
            months = 6

        player_ids = form.cleaned_data['players']
        player_ids = [int(p_id) for p_id in player_ids]

        country = form.cleaned_data['country']
        context['local_currency'] = CURRENCY_DICT[country]
        context['use_local_currency'] = country in LOCAL_CURRENCY_COUNTRIES

        if form.cleaned_data['all_categories']:
            categories = Category.objects.all()
            category_ids = []
            for category in categories:
                if category.name != 'root':
                    category_ids.append(int(category.id))
        else:
            category_ids = form.cleaned_data['categories']
            category_ids = [int(c_id) for c_id in category_ids]

        histo = defaultdict()
        player_list = []
        total_sales_player = defaultdict()
        company_names = defaultdict()

        total_sales_period = {}

        for p_id in player_ids:
            company_name = DayWatchSite.objects.get(id=int(p_id)).name
            company_names[int(p_id)] = company_name
            player_list.append((int(p_id), company_name))
            total_sales_player[company_name] = 0
            histo[company_name] = defaultdict()

        category_choices = []
        category_legends = []
        for c_id, name in CATEGORY_CHOICES:
            if c_id in category_ids:
                category_choices.append((c_id, name))
                category_legends.append(name)

        company_choices = []
        for c_id, name in COMPANY_CHOICES:
            if c_id in player_ids:
                company_choices.append((c_id, name))

        if concept == 'sales':
            if context['use_local_currency']:
                context['total_title'] = _('Total Sales')
                context['trend_y_legend'] = context['local_currency'] + ' %.0f'
            else:
                context['total_title'] = _('Total Sales U$S')
                context['trend_y_legend'] = 'U$S %.0f'
        elif concept == 'deals':
            context['total_title'] = _('Total # Deals Offered')
            context['trend_y_legend'] = '%d'
        elif concept == 'coupons_sold':
            context['trend_title'] = _('# Coupons Sold')
            context['total_title'] = _('Total # Coupons Sold')
            context['trend_y_legend'] = '%d'

        for company_id, company_name in player_list:
            total_sales_period[company_name] = []
            category_values = {}

            for category_id, category_name in category_choices:
                category_values[category_name] = []

            for i in range(months - 1, -1, -1):
                start_month = today.month - i
                if start_month <= 0:
                    start_month += 12
                    start_year = today.year - 1
                else:
                    start_year = today.year
                start_date_range = datetime(start_year, start_month, 1)
                (_, last) = calendar.monthrange(start_year, start_month)
                end_date_range = datetime(start_year, start_month, last)

                items = DayWatchItem.objects.filter(country=country)
                if concept == 'sales':
                    context['trend_title'] = _('Sales U$S')
                    context['trend_y_legend'] = _('U$S %.0f')

                    items = items.filter(
                        company__id=company_id,
                        category__id__in=category_ids,
                        start_date_time__gte=start_date_range,
                        start_date_time__lte=end_date_range,
                        total_sales_usd__gt=0
                    )
                    items = items.values('category__name').annotate(
                        subtotal=Sum('total_sales_usd')
                    )

                elif concept == 'deals':
                    context['trend_title'] = _('# Deals Offered')
                    context['trend_y_legend'] = '%d'

                    items = items.filter(
                        company__id=company_id,
                        category__id__in=category_ids,
                        start_date_time__gte=start_date_range,
                        start_date_time__lte=end_date_range
                    )
                    items = items.values('category__name').annotate(
                        subtotal=Count('offer_id')
                    )

                elif concept == 'coupons_sold':
                    context['trend_title'] = _('# Coupons Sold')
                    context['trend_y_legend'] = '%d'

                    items = items.filter(
                        company__id=company_id,
                        category__id__in=category_ids,
                        start_date_time__gte=start_date_range,
                        start_date_time__lte=end_date_range,
                        sold_count__gt=0
                    )
                    items = items.values('category__name').annotate(
                        subtotal=Sum('sold_count')
                    )

                total_category = {}
                for _, category_name in category_choices:
                    total_category[category_name] = 0

                for item in items:
                    total_category[deal['category__name']] += deal['subtotal']
                for items in items:
                    total_category[deal['category__name']] += deal['subtotal']

                for _, category_name in category_choices:
                    category_values[category_name].append(
                        total_category[category_name]
                    )

            for _, category_name in category_choices:
                total_sales_period[company_name].append(
                    category_values[category_name]
                )

        interval_values = []
        graphs = []
        for company_name in total_sales_period:
            max_val = 0
            for array in total_sales_period[company_name]:
                for value in array:
                    if value > max_val:
                        max_val = value
            graphs.append({
                'company_name': company_name,
                'interval_value': get_interval(max_val),
                'arrays': total_sales_period[company_name]
            })

        month_legends = []
        for i in range(months - 1, -1, -1):
            start_month = today.month - i
            if start_month <= 0:
                start_month += 12
            month_legends.append(calendar.month_name[start_month])

        legends = [style[category]['label'] for category in category_legends]

        context['graphs'] = graphs
        context['concept'] = concept
        context['category_legends'] = legends
        context['month_legends'] = month_legends
        context['interval_values'] = interval_values

        html = render_to_string(
            'history_comparison_div.html',
            context,
            context_instance=RequestContext(request)
            )
        return JsonResponse(result(Status.OK, data={'html': html}))
    else:
        return JsonResponse(result(Status.ERROR, 'Invalid form.'))
