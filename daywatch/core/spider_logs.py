# -*- coding: utf-8 -*-
# Analyze spider logs

from utils import percentage, datetime_to_unix
from models import Run, ErrorLog

from scraper.item_scraper.errors import ERROR_CATEGORIES


class SpiderLogAnalysis(object):
    """Encapsulates the results of extracting important information from a set of
    spider logs from a particular site.

    ================= =============== ================================================
    Attribute         Type            Description
    ================= =============== ================================================
    `working`         ``bool``        Whether or not the spider is working.
    `times_run`       ``int``         The number of times the spider ran in the period.
    `offers_log`      ``dict``        A map from Unix timestamps to the number of offers scraped in that date.
    `errors`          ``list[tuple]`` Percentage of different error categories.
    `error_evolution` ``list[dict]``  How error percentages have evolved over the period.
    ================== ============== ================================================

    The `errors` field is a list of tuples, where the first element of the tuple
    is the name of the error category and the second is the percentage in the
    set of errors.

    `error_evolution` is a list of dictionaries, where each dictionary has two keys:

    * `date`: The date the spider was run.
    * `errors`: The percentage of errors in that run.

    """

    def __init__(self, working, times_run, offers_log, errors,
                 error_evolution):
        self.working = working
        self.times_run = times_run
        self.offers_log = offers_log
        self.errors = errors
        self.error_evolution = error_evolution


def process_errors(error_logs):
    '''Take a list of error logs, and return its characteristics, ie percentage
    of errors related to merchant data, database failures etc.'''
    total = len(error_logs)
    if total == 0:
        # No errors, however, we still return a dictionary with every key, just
        # for consistency
        errors = [(category, 0) for category in ERROR_CATEGORIES]
        return errors

    def count_category(cat):
        """Return the number of logs that have category 'cat'."""
        return sum([(1 if log.category == cat else 0) for log in error_logs])

    errors = [(category, percentage(count_category(category), total))
              for category in ERROR_CATEGORIES]
    return errors


def analyze(sites, start_date, end_date):
    data = {}

    for site in sites:
        # For each site, we extract the runs for the specified period, and from
        # them, offer counts and error logs
        runs = Run.objects.filter(site=site,
                                  start__gte=start_date,
                                  end__lte=end_date)

        # Error Logs

        # Iterate over each run, find every error log between its start and
        # end, and get the percentage of each kind.

        all_errors = ErrorLog.objects.filter(site=site,
                                             date_time__gte=start_date,
                                             date_time__lte=end_date)
        period_error_distribution = process_errors(all_errors)

        error_evolution = []

        for run in runs:
            errors = ErrorLog.objects.filter(site=site,
                                             date_time__gte=run.start,
                                             date_time__lte=run.end)

            run_time = datetime_to_unix(run.start)
            processed_errors = process_errors(errors)

            error_evolution += [{
                'date': run_time,
                'errors': processed_errors
            }]

        working = False
        if runs:
            last_run = runs.order_by('-start')[0]
            if last_run.scraped > 0:
                working = True

        offers_log = [[datetime_to_unix(run.start), run.scraped]
                      for run in runs]
        analysis = SpiderLogAnalysis(working=working,
                                     times_run=len(runs),
                                     offers_log=offers_log,
                                     errors=period_error_distribution,
                                     error_evolution=error_evolution)
        data[site.name] = analysis

    return data
