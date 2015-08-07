# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from core.general import catch_error, get_status


@login_required
def index(request):
    context = get_status(request)
    return render_to_response('main/index.html',
                              dictionary=context,
                              context_instance=RequestContext(request))


@catch_error
def set_language(request, *args, **kwargs):
    request.session['django_language'] = request.GET.get('language', 'en')
    next_url = request.GET.get('next', '/')
    return HttpResponseRedirect(next_url)
