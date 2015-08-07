# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from gui.utils import parse_date_range, country_sites
from gui.forms import SpidersPanelForm

from core.spider_logs import analyze
from core.models import SITE_MODEL, user_country_access
from core.decorators import log_activity
from core.general import catch_error, get_status, permission_required

from core.scraper.item_scraper.errors import ERROR_CATEGORIES

@catch_error
@log_activity
@login_required
@permission_required
def spider_listings(request):
    context = get_status(request)

    context['app'] = 'spiders_panel'
    context['country_sites'] = country_sites(user_country_access(request.user))
    context['form'] = SpidersPanelForm(
        user=request.user,
        initial=request.session.get('form_session'))

    return render_to_response('spiders_panel.html', context,
                              context_instance=RequestContext(request))


@catch_error
@login_required
@permission_required
def spider_listings_div(request):
    context = get_status(request)
    form = SpidersPanelForm(user=request.user, data=request.GET)

    if not form.is_valid():
        return HttpResponse(json.dumps({'error': 'Invalid form'}),
                            content_type='application/json')

    request.session['form_session'] = form.cleaned_data

    # Convert date parameters
    start_date, end_date = parse_date_range(form)

    country = form.cleaned_data['country']
    site_ids = [int(site) for site in form.cleaned_data['players']]
    sites = [SITE_MODEL.objects.get(id=site_id) for site_id in site_ids]

    data = analyze(sites, start_date, end_date)
    context['sites'] = data
    context['error_categories'] = ERROR_CATEGORIES

    if data:
        return render_to_response('spider_div.html', context)
    else:
        return render_to_response('main/no_results.html', context)
