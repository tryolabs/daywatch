from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, RedirectView

from gui.forms import PasswordResetReCaptchaForm

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # general
    url(r'^$', 'gui.views.index', name='index'),

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt')),
    (r'^favicon\.ico$',
     RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),

    # panels
    (r'^analytics_panel/', include('gui.analytics_panel.urls')),
    (r'^spiders_panel/', include('gui.spiders_panel.urls')),
    (r'^items_panel/', include('gui.items_panel.urls')),
    (r'^trends_panel/', include('gui.trends_panel.urls')),

    # accounts
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),

    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        name='logout', kwargs={'next_page': '/'}),

    url(r'^accounts/password/reset/$',
        'django.contrib.auth.views.password_reset', name='password_reset',
        kwargs={'post_reset_redirect': '/accounts/password/reset/done/',
                'password_reset_form': PasswordResetReCaptchaForm}
    ),

    (r'^accounts/password/reset/done/$',
     'django.contrib.auth.views.password_reset_done'),

    (r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
     'django.contrib.auth.views.password_reset_confirm',
     {'post_reset_redirect': '/accounts/password/done/'}),

    (r'^accounts/password/done/$',
     'django.contrib.auth.views.password_reset_complete'),

    url(r'^accounts/password/change/$',
        'django.contrib.auth.views.password_change', name='password_change'),

    (r'^accounts/password/change/done/$',
     'django.contrib.auth.views.password_change_done'),
)
