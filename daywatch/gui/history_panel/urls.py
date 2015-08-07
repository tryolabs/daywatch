# -*- coding: utf-8 -*-
'''
Created on Sep 24, 2013

@author: alejandro
'''

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',

    #url(r'^$', 'gui.history_panel.views.index', name='history_panel_home'),

    url(r'^deal_list_date', 'gui.history_panel.views.deal_list_date',
        name='deal_list_date'),
    url(r'^deal', 'gui.history_panel.views.deal', name='deal'),

    url(r'^$', 'gui.history_panel.views.history_listings',
        name='history_panel_home'),
    url(r'^history_div', 'gui.history_panel.views.history_listings_div',
        name='history_div'),

    url(r'^history_comparison$', 'gui.history_panel.views.history_comparison',
        name='history_comparison'),
    url(r'^history_comparison_div',
        'gui.history_panel.views.history_comparison_div',
        name='history_comparison_div'),
)
