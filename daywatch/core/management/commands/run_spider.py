from django.core.management.base import BaseCommand

from core.models import SITE_MODEL
from core.spiders import run_site_spider


class Command(BaseCommand):
    args = '<spider_name>'
    help = 'Run a spider given its name.'

    def handle(self, *args, **options):
        spider_name = args[0]

        site = SITE_MODEL.objects.get(spider_name=spider_name)

        run_site_spider(site)
