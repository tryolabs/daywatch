************
Introduction
************

DayWatch is a Django application for scraping, tracking and analysis of daily
deals or other e-commerce items. The application is subdivided into three
sub-applications:

- :code:`core` implements the general database models and includes a subapp
  :code:`scraper`, which contains web scrapers defined using the Scrapy
  framework.
- :code:`api` defines DayWatch's API interface.
- :code:`gui` implements DayWatch's web-based user interface.
