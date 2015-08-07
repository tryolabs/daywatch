# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'gui.spiders_panel.views.spider_listings',
        name='spiders_panel_home'),
    url(r'^spider_div', 'gui.spiders_panel.views.spider_listings_div',
        name='spider_div'),
)
