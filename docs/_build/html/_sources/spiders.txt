*******
Spiders
*******

Overview
========

The basic structure of a spider is as follows:

::

  # -*- coding: utf-8 -*-
  import PythonLib

  from scrapy.http import Request
  from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
  from scrapy.contrib.spiders.crawl import Rule
  from scrapy.selector import HtmlXPathSelector

  from dailyitem.spiders.general import *
  from dailyitem.parsers import *

  from fields import *


  class SiteNameSpider(DailyItemSpider):
      name = "sitename.com"

      rules = (
          #cities
          Rule(SgmlLinkExtractor(restrict_xpaths='...',
                                 allow=('...',)),
               follow=True),

          #navigation
          Rule(SgmlLinkExtractor(restrict_xpaths='...',
                                 deny=('...',)),
               follow=True),

          #offers
          Rule(SgmlLinkExtractor(restrict_xpaths='...',),
               follow=False,
               callback='get_offer'),
      )

      extractors = {
          ...
      }

Extractors
----------

Extractors are a simple, short way of applying XPath selectors, regular
expressions, and simple functions when extracting data.

Built-in Extractors
^^^^^^^^^^^^^^^^^^^

:code:`lat`
  Extract Latitude information from an XPath to a Google Map.

:code:`lon`
  Like :code:`lat`, but returns Longitude information.

Loader Functions
----------------

When neither an XPath selector or an extractor will cut it, you can override it
with a function that does whatever processing you need to extract the
values. For example, if you have to do something more complicated than what
XPath can handle to extract the :code:`merchant_phone`, you can can use
something like this:

::

  def load_merchant_phone(self, item_loader, response):
      hxs = HtmlXPathSelector(response)
      try:
          phone = ...some processing...
          item_loader.add_value(F_M_PHONE, phone)
      except:
          item_loader.add_value(F_M_PHONE, MISSING_VALUE)

Functions take precedence over XPath selectors. If the international-level
spider has, say, a function to load the offer ID, and the country-level spider
has an XPath selector, the function from the parent will be executed. You have
to override the method.

When a country-specific spider can run entirely on xpaths and functions
inherited from its parent (ie, when the site's structure is the same for every
country), that spider only needs the following code:

::

  # -*- coding: utf-8 -*-
  from dailyitem.spiders.groupon_spider import GrouponSpider
  from dailyitem.items import *
  from dailyitem.parsers import *


  class SiteNameCountrySpider(SiteNameSpiderr):
      name = "sitename.com.countrycode"
      country = "countrycode"
      main_domain = "..."
      allowed_domains = [main_domain]

      main_url = "..."

      decimal_mark = [DECIMAL_MARK_PERIOD|DECIMAL_MARK_COMMA]

Starting from this skeleton, you can change the XPaths or the functions if there
is anything that changes at the country level, but first you have to add the
necessary :code:`import` statements.

Variables
=========

:code:`name`
    The spider's name, in the :code:`sitename.com.countrycode` format. Example:
    :code:`livingsocial.com.ph`.

:code:`main_domain`
    The domain and subdomains the spider is allowed to crawl. Essentially the
    site's FQDN, without all the slashes and the protocol (:code:`http`)
    information.

:code:`main_url`
    The starting URL. When testing a spider, this must be provided through the
    command line (See below).

:code:`has_main_offer`
    In some sites, not all the items are linked to: Instead the landing page
    displays a full item (Generally "today's item"),and links to other items are
    in a sidebar or at the bottom of the page. In these cases,
    :code:`has_main_offer` should be set to :code:`True` so Scrapy knows it has
    to crawl that landing page as well as the others.

:code:`decimal_mark`
    Either :code:`DECIMAL_MARK_COMMA` or :code:`DECIMAL_MARK_PERIOD`. This
    informs the parsers which symbol is used to mark the decimals in the
    price. If the site suddenlly decides to change from one representation to
    the other, you (Or your clients) will notice a change in the sold count.

Running Spiders
===============

From the Command Line
---------------------

When testing the spider, you use use the :code:`run_spider` command to run it.

For example:

::

   $ ./manage.py run_spider test_spider
   Running spider test_spider
   59815 Apple iPhone 5 16GB Unlocked | Daily Steals Apple iPhone 5 16GB Unlocked (U$S 249.0, ?)
   59811 AnyCommand AC Remote Control | Daily Steals AnyCommand AC Remote Control (U$S 8.0, ?)
   Could not classify item '59803', assigning category 'Retail'.
   59803 Incipio Wireless Phone Charger | Daily Steals Incipio Wireless Phone Charger (U$S 10.0, ?)
   59806 BlueAnt Pump BT Sportbuds | Daily Steals BlueAnt Pump BT Sportbuds (U$S 25.0, ?)
   59792 Solarpod Buddy 2800mAh Battery | Daily Steals Solarpod Buddy 2800mAh Battery (U$S 10.0, ?)
   59796 Sphamm 7ft Nylon Hammock | Daily Steals Sphamm 7ft Nylon Hammock (U$S 9.0, ?)


From Celery
-----------

Spiders can be scheduled to run periodically through Celery from the Django
Admin (Or programatically).

Two objects are required to schedule a spider: **Intervals**, which represent
some periodic time delta (ie, "Every 30 seconds", "Every six hours"); and
**Periodic Tasks**. To schedule a new spider-running task, just create a new
Periodic Task with an appropriate interval, choose the
:code:`core.tasks.runspiders` as the task, and pass the appropriate parameters.

Spider Logs
===========

When a spider fails, it's generally either because the site has been changed in
some way and the old XPath selectors no longer work, or the Site has blocked
us because the Spider's crawling looks like a DOS attack.

Daily Deal Sites
================

Navigation
----------

Essentially, there is a main page that usually lists some deals, a navigation
bar with links to different sections, and a selector to jump to a different city
or country. The selector is sometimes AJAX, which some times requires one to
collect a list of supported locations and add them to Scrapy's
:code:`start_urls` list for that spiders so they will be scraped. The navigation
bar sometimes includes an item labeled 'All deals' or similar, which shows a
page listing all the deals. Just to make sure all deals are being scraped, all
sections should be scraped unless it is very clear that there exists an 'All
deals' section and that it does in fact show all the deals.

Many sites that handle a large volume of deals include pagination in their deal
listings. When the pagination is HTTP, it is sufficient to add a rule with the
XPath of the 'Next' button. When the pagination is AJAX, the methods described
in the JavaScript section should be used.

In rare cases, a link to a deal actually links to a list of deals, or some deals
can only be accessed in a listing (Usually in a sidebar or below) inside a
deal's page. In those cases, the rule for scraping a deal should include a
:code:`follow=True` parameter to ensure the 'sub-deals' are scraped.

JavaScript
----------

Many sites use JavaScript to dynamically load content. Scrapy doesn't have a
JavaScript interpreter built it, but this is generally not necessary. Usually,
the JavaScript sends a request to some file somewhere on the server. You can
view the request and its results in the Web Inspector's network tab, just open
it and press F5 and or scroll down (If the page uses infinite scroll) until a
request is sent.

Usually the response is JSON data that is then concatenated with prewritten HTML
and written onto the page. In other cases, it's a complete snippet of HTML that
is simply written directly into the page. In the latter case, you can just use
`Requests`_ to whatever URL holds that file; and in the former, you can simply
use the methods described in the :ref:`JSON section <spiders-json>` to extract
the data.

.. _spiders-json:

JSON
----

Sometimes, when Javascript is used to dynamically load the deals, the script
doesn't request a page with raw HTML and insert it, but rather requests a JSON
file, and produces the links to the requests using the data in it.

You can find this out by going to the Web Inspector, and in the Network tab
clearing whatever is there and refreshing the page, then scroll until you find a
response with the MIME type :code:`application/json` (:code:`text/x-json` is
sometimes used, but is not the Standard. Sometimes, the file is sent as a
:code:`text/plain`, and if the file doesn't have the :code:`.json` extension
then you have no choice but to look manually).

The link to the JSON file might be the same even as its content changes, or it
might change every day. For example, in one of our spiders the file was called
:code:`20130219.json` on the ninteenth of February, 2013, so the query string
had to be created dynamically.

Once you have the link, you can use Scrapy's `Requests`_ to download it Python's
:code:`json` module to parse it. Python and JSON get along very well. You can
access JSON maps and array as if they were native Python dictionaries and lists,
respectively. To build an item 'by hand', you should do it like this:

::

  deal = DayWatchItem()

  deal[F_ID] = item['id']
  deal[F_OFFER] = item['name']

  ...

  yield deal

.. _Requests: http://doc.scrapy.org/en/latest/topics/request-response.html
