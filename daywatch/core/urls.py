# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # admin
    url(r'^admin/', include(admin.site.urls)),

    # gui
    (r'', include('gui.urls')),

    # Daywatch API
    (r'^api/', include('api.urls')),
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

urlpatterns += patterns('',
    (r'^i18n/', include('django.conf.urls.i18n')),
)
