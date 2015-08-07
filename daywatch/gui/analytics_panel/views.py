# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from gui.utils import parse_date_range, country_sites

from core.models import Country, SITE_MODEL, ITEM_MODEL, user_country_access
from core.general import catch_error, get_status, Status, result, \
    permission_required
from gui.forms import PanelForm, RESULT_TYPE_CHOICES
from core.decorators import log_activity

import core.analytics as analytics


OTHER_LABEL = 'Other'


@login_required
@catch_error
@permission_required
@log_activity
def analytics_panel(request):
    context = get_status(request)

    context['app'] = 'analytics_panel'

    context['country_sites'] = country_sites(user_country_access(request.user))
    context['form'] = PanelForm(user=request.user,
                                initial=request.session.get('form_session'))

    return render_to_response('analytics_panel.html', context,
                              context_instance=RequestContext(request))


@login_required
@catch_error
def analytics_div(request):
    # Things the analytics panel provides:
    # Sales:
    # - Sales volume over time
    # - Percentage of companies that sell each category (Pie)
    # - Percentage of categories sold by each company (Pie)
    # - Total sales in the period
    # - Total sales volume
    # - Sales volume share by company
    # - Sales volume share by category
    # - Evolution of the above two over the time period (Stacked area chart)
    # Deals Offered and Coupons sold:
    # - By company, over time
    # - Number of deals sold by a company, per category (Pie)
    # - Number of deals sold of each category, per company (Pie)
    # - Total number of deals sold
    # - Total number of deals sold, by company
    # - Percentage of deals sold by each company
    # - Percentage of deals sold in each category

    context = get_status(request)
    form = PanelForm(user=request.user, data=request.GET)

    if not form.is_valid():
        return render_to_response('main/form_error.html', context)

    request.session['form_session'] = form.cleaned_data
    result_type = form.cleaned_data['result_type']
    country = Country.objects.get(code=form.cleaned_data['country'])
    start_date, end_date = parse_date_range(form)
    sites = [SITE_MODEL.objects.get(id=site_id) for site_id in
             [int(site_id) for site_id in form.cleaned_data['players']]]
    items = ITEM_MODEL.objects.filter(site__in=sites,
                                      date_time__gte=start_date,
                                      date_time__lte=end_date)

    context['result_type'] = result_type
    context['result_type_name'] = [choice[1] for choice in
                                   RESULT_TYPE_CHOICES
                                   if choice[0] == result_type][0]

    if result_type == 'sales':
        context['analysis'] = analytics.SalesAnalysis(items)
    elif result_type == 'offered':
        context['analysis'] = analytics.OfferedAnalysis(items)
    elif result_type == 'sold':
        context['analysis'] = analytics.SoldAnalysis(items)

    return render_to_response('analytics_div.html', context)
