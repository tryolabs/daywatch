# -*- coding: utf-8 -*-

from datetime import timedelta

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from gui.utils import parse_date_range, country_sites
from gui.forms import TrendsPanelForm, SUM, AVERAGE

from core.decorators import log_activity
from core.general import catch_error, get_status, permission_required
from core.models import SITE_MODEL, ITEM_MODEL, user_country_access
from core.analytics import items_sum, items_average


@catch_error
@log_activity
@login_required
@permission_required
def trends_listings(request):
    context = get_status(request)

    context['app'] = 'items_panel'
    context['country_sites'] = country_sites(user_country_access(request.user))
    context['form'] = TrendsPanelForm(
        user=request.user,
        initial=request.session.get('form_session'))

    return render_to_response('trends_panel.html', context,
                              context_instance=RequestContext(request))


@catch_error
@login_required
@permission_required
def trends_div(request):
    context = get_status(request)
    form = TrendsPanelForm(user=request.user, data=request.GET)

    if not form.is_valid():
        return render_to_response('main/form_error.html', context)

    start_date, end_date = parse_date_range(form)
    sites = [SITE_MODEL.objects.get(id=site_id) for site_id in
             [int(site_id) for site_id in form.cleaned_data['players']]]
    fields = form.cleaned_data['fields']
    metric = form.cleaned_data['metric']

    def get_items(start_date, end_date):
        return ITEM_MODEL.objects.filter(site__in=sites,
                                         date_time__gte=start_date,
                                         date_time__lte=end_date)

    def analyze_items(items, field):
        if metric == SUM:
            return items_sum(items, field)
        elif metric == AVERAGE:
            return items_average(items, field)

    evolution = {}
    for field in fields:
        # Find how the field has evolved over time
        # Step over every day between the start and end date
        delta = (end_date - start_date)
        metric_evolution = []
        for i in range(delta.days + 1):
            start_day = (start_date + timedelta(days=i))
            end_day = start_day + timedelta(days=1)
            items = get_items(start_day, end_day)
            analysis = analyze_items(items, field)
            if analysis:
                metric_evolution += [(start_day.strftime('%s'), analysis)]
        evolution[field] = metric_evolution

    context['evolution'] = evolution
    return render_to_response('trends_div.html', context,
                              context_instance=RequestContext(request))
