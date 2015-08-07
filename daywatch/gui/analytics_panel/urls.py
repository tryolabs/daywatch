# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^$', 'gui.analytics_panel.views.analytics_panel',
        name='analytics_panel_home'),
    url(r'^analytics_div', 'gui.analytics_panel.views.analytics_div',
        name='analytics_div'),
)
