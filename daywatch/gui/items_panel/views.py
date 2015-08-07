# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.models import SITE_MODEL, ITEM_MODEL, user_country_access
from core.decorators import log_activity
from core.general import catch_error, get_status, permission_required

from gui.utils import parse_date_range, country_sites
from gui.forms import ItemsPanelForm


@catch_error
@log_activity
@login_required
@permission_required
def item_listings(request):
    context = get_status(request)

    context['app'] = 'items_panel'
    context['country_sites'] = country_sites(user_country_access(request.user))
    context['form'] = ItemsPanelForm(
        user=request.user,
        initial=request.session.get('form_session'))

    return render_to_response('items_panel.html', context,
                              context_instance=RequestContext(request))


@catch_error
@login_required
@permission_required
def item_div(request):
    context = get_status(request)
    form = ItemsPanelForm(user=request.user, data=request.GET)

    if not form.is_valid():
        return render_to_response('main/form_error.html', context)

    start_date, end_date = parse_date_range(form)
    fields = form.cleaned_data['fields']

    sites = [SITE_MODEL.objects.get(id=site_id) for site_id in
             [int(site_id) for site_id in form.cleaned_data['players']]]
    items = ITEM_MODEL.objects.filter(site__in=sites,
                                      date_time__gte=start_date,
                                      date_time__lte=end_date)

    paginator = Paginator(items, 25)

    page = request.GET.get('page')
    try:
        display_page = paginator.page(page)
    except PageNotAnInteger:
        # Wrong input
        display_page = paginator.page(1)
    except EmptyPage:
        # Out of range
        display_page = paginator.page(paginator.num_pages)

    context['items'] = display_page
    context['fields'] = fields
    return render_to_response('item_div.html', context,
                              context_instance=RequestContext(request))
