# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'gui.items_panel.views.item_listings',
        name='item_listings'),
    url(r'^items_div', 'gui.items_panel.views.item_div',
        name='item_div'),
)
