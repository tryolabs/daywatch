# -*- coding: utf-8 -*-

from django.template.defaulttags import register

@register.filter
def lookup(model, field_name):
    """Extract a value from a model instance using a key. If the key is not present,
    return None.

    """
    return getattr(model, field_name)
