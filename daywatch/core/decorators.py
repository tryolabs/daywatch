# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from models import ActivityLog


def log_activity(f):
    '''
    Decorator function for views where we want to register user activity.
    '''
    def call(request, *args, **kwargs):
        user = request.user
        if isinstance(user, User):
            try:
                referer = request.META['HTTP_REFERER']
            except:
                referer = None
            agent = request.META['HTTP_USER_AGENT']
            path = request.path
            qs = request.build_absolute_uri()
            ActivityLog(user=user, referer=referer,
                        query_path=path, user_agent=agent,
                        absolute_uri=qs, date_time=datetime.now()).save()

        return f(request)

    call.__doc__ = f.__doc__
    call.__name__ = f.__name__
    call.__dict__.update(f.__dict__)
    return call
