# -*- coding: utf-8 -*-

from __future__ import absolute_import
from core.settings import BROKER_URL
from celery import Celery

celery = Celery('core.tasks', broker=BROKER_URL)

from django.conf import settings
from core.models import SITE_MODEL, Currency

from core.spiders import run_site_spider



@celery.task
def run_spiders(site_ids):
    '''Run all the spiders belonging to the sites in `site_ids`.

    '''
    sites = [SITE_MODEL.objects.get(id=id)
             for id in site_ids]
    for site in sites:
        run_site_spider(site)


@celery.task
def update_currencies():
    Currency.update_currencies()
