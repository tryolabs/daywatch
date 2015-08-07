from django.conf.urls import patterns, include, url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from api import views

router = routers.DefaultRouter()
router.register(r'items', views.ItemView)
router.register(r'merchants', views.MerchantView)
router.register(r'sites', views.SiteView)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       url(r'^analytics/$', views.AnalyticsView.as_view()))
