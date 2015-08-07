# -*- coding: utf-8 -*-

import copy

from django.contrib import admin

from core.models import *

admin.site.register(SITE_MODEL)
admin.site.register(MERCHANT_MODEL)
admin.site.register(ITEM_MODEL)

admin.site.register(BufferedItem)
admin.site.register(TestItem)

admin.site.register(Category)
admin.site.register(Currency)
admin.site.register(Language)
admin.site.register(Country)

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]

    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_staff', 'last_login')

    class Media:
        # We use this script to manage some account type details in the admin
        js = ("js/userprofile-validator.js",)

# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)


class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'date_time',
                    'referer', 'query_path', 'target_resource')
    list_filter = ('user',)

    def user_link(self, instance):
        return u'<a href="../../auth/user/%d">%s</a>' % \
            (instance.user.id, instance.user.username)
    user_link.allow_tags = True
    user_link.short_description = 'User'

    def target_resource(self, instance):
        return u'<a href="%s">%s</a>' % (instance.absolute_uri, "Go")
    target_resource.allow_tags = True

admin.site.register(ActivityLog, ActivityLogAdmin)

admin.site.register(Run)
admin.site.register(SoldCount)
admin.site.register(ErrorLog)
