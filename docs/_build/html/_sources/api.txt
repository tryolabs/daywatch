***
API
***

Items
=====

The Items API allows you to access the data of the :ref:`Items Panel <items-panel>`.

Query Parameters
----------------

:code:`min_price` and :code:`max_price`
    Specify a price range.

:code:`min_discount` and :code:`max_discount`
    Specify a discount range.

:code:`start` and :code:`end`
    Specify a date range.

:code:`category`
    Only items with this category.

:code:`site`
    Only items offered on this site.

:code:`merchant`
    Only items sold by this merchant.

:code:`active`
    Whether the item is actively tracked or historical.

Output
------

:code:`hash_id`
    Usually a SHA-256 of the slug in the :code:`url`, sans query parameters.

:code:`offer`
    Offer's title.

:code:`url`
    Offer URL

:code:`category`
    Name of the category.

:code:`description`
    (Optional) description of the offer.

:code:`site`
    ID of the site the offer was extracted from. See Sites.

:code:`currency`
    ISO code of the price's currency.

:code:`price`
    Numerical value of the price.

:code:`discount`
    Discount percentage (as a number).

:code:`sold_count`
    Number of coupons sold.

:code:`city`
    City where the item was offered.

:code:`merchant`
    ID of the merchant offering the item. See Merchants.

:code:`image_url`
    URL of the main image.

:code:`start`
    Time the item was first found.

:code:`end`
    Time the item ended.

:code:`active`
    Whether the item is still being tracked (True) or is historical (False).

:code:`sales_log`
    A list of dictionaries, each with two key/value pairs: :code:`sold`, the
    sold count at that particular time, and :code:`date`, the time it was
    recorded.

Sites
=====

The Sites API allows you to query the database of sites.

Query Parameters
----------------

:code:`name`, :code:`spider_name`
    Site and spider name.

:code:`spider_enabled`
    Whether the spider will be run.

:code:`country`
    The country the site does business in.

Output
------

:code:`id`
    Merchant ID.

:code:`name`
    Site name.

:code:`url`
    URL where the spider starts scraping.

:code:`spider_name`
    Scrapy name of the spider.

:code:`spider_enabled`
    Whether the spider will be run.

:code:`country`
    Country this site is selling in.

:code:`runs`
    A list of data about every time the spider was run. :code:`start` and
    :code:`end` are the times the run began and ended, respectively,
    :code:`offers` is the number of offers found by the spider, and
    :code:`errors` is a list of error logs found in the run.

Examples
--------

::

  [
      {
          "name": "Test",
          "url": "http://groupon.com",
          "spider_name": "test-spider",
          "spider_enabled": true,
          "country": 2,
          "runs": [
              {
                  "start": "2013-12-10T14:07:08.963Z",
                  "offers": 346,
                  "end": "2013-12-10T14:14:56.812Z",
                  "errors": [
                      {
                          "message": "...",
                          "type": "SpiderMissingValueException"
                      },
                      {
                          "message": "...",
                          "type": "SpiderMissingValueException"
                      }
                  ]
              }
          ]
      }
  ]

Merchants
=========

The Merchants API allows you to query the merchants database.

Query Parameters
----------------

:code:`min_lat`, code:`max_lon`, code:`min_lat` and code:`max_lat`
    Specify a rectangle that includes that merchant location.

Output
------

:code:`id`
    Merchant ID.

:code:`name`
    Merchant name.

:code:`lat` and :code:`lon`
    Merchant latitude and longitude, respectively.

:code:`address`, :code:`phone`, :code:`website`, :code:`email`
    Exactly what it says on the tin.

:code:`items_sold`
    Number of items sold in the specified date range.

:code:`sales_volume`
    The sales volume in the date range. This is the sum over every item of its
    price times the number sold.

:code:`items_offered`
    The number of items offered in the date range.

:code:`radius`
    These allow you to find merchants in a radius of :code:`radius` from the
    point determined by :code:`lat` and :code:`lon`.

Examples
--------

::

  [
      {
          "id": 5460,
          "name": "Peeled",
          "lat": 42.0483238,
          "lon": -87.6843991,
          "address": "940 Church St.EvanstonIllinois",
          "phone": null,
          "website": "http://www.peeledchicago.com",
          "email": null,
          "items_sold": 1838,
          "sales_volume": 785075.0,
          "items_offered": 86
      },
  ]

Analytics
=========

The analytics endpoint provides the functionality of the :ref:`Analytics Panel
<analytics-panel>` from the API.

Query Parameters
----------------

:code:`sites`
  JSON-formatted array of site IDs.

:code:`result_type`
  Either `sales`, `offered` or `sold`.

:code:`start_date`, :code:`end_date`
  Optional analytics date range.

Output
------

:code:`result_type`
  The value of the :code:`result_type` request parameter.
