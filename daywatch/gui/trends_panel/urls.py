# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'gui.trends_panel.views.trends_listings',
        name='trends_listings'),
    url(r'^trends_div', 'gui.trends_panel.views.trends_div',
        name='trends_div'),
)
