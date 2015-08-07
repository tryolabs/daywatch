from datetime import datetime, timedelta
from django.utils import timezone

from core.models import Country, SITE_MODEL



class DateRangeError(Exception):
    pass


def parse_date_range(form):
    """Extract a date range from a form. Forms in DayWatch allow you to select a
    pre-set period, like "Past 30 days" or "Past Week", or set a custom date
    range. This function takes a form and returns a `(start_date, end_date`)
    pair.

    """
    period = form.cleaned_data['period']

    end_date = timezone.now()
    if period == 'last_30_d':
        start_date = timezone.now() - timedelta(days=30)
    elif period == 'last_15_d':
        start_date = timezone.now() - timedelta(days=15)
    elif period == 'last_7_d':
        start_date = timezone.now() - timedelta(days=7)
    elif period == 'custom':
        d = form.cleaned_data['start_date']
        start_date = datetime(d.year, d.month, d.day)
        d = form.cleaned_data['end_date']
        end_date = datetime(d.year, d.month, d.day, 23, 59)

    if start_date > end_date:
        raise DateRangeError
    else:
        return (start_date, end_date)


def country_sites(countries):

    """Take a list of Country objects, and return a JSON that maps their names to
    the IDs of the sites of those countries. Used to filter sites by country in
    the panels.
    """
    def country_sites(country):
        return [site.id for site in SITE_MODEL.objects.filter(country=country)]

    return {str(country.code): country_sites(country)
            for country in countries}
