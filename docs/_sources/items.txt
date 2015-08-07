*****
Items
*****

Item's are the central object of DayWatch: They store the information about the
target object -- a daily deal, a Groupon, etc.

Item Data
=========

:code:`hash_id`
    A unique alphanumerical identifier, generally found in the URL (Example:
    :code:`/item.php?id=1234`). When there is no ID, just hash the concatention
    of the offer title and (optionally) the city.

:code:`offer`
    The title of the offer. You can save unobservable milliseconds by setting
    this to :code:`/html/head/title`, if indeed the title contains the offer's
    title.

:code:`price_currency`
    This should return the price with its currency symbol. It's important that
    it matches the ones DayWatch understands belong to the currency for that
    spider's country.

:code:`discount`
    This should return the discount *with the percentage sign*.

:code:`sold_count`
    Many sites inform how many people have bought the item. This is important
    for deriving, for example, the total sales revenue and the site's total
    profits.

:code:`description`
    Most Daily Item sites offer a variable-length description of this item. This
    is important for categorizing the item.

:code:`city`
    The city where the item is being offered. In many Daily Item sites, the same
    items are repeatedly offered in different sities.

Merchant Data
-------------

The merchant is the site that is offering the item through the Site. Sometimes
the merchant is completely hidden, but most of the time the Site will give you
some information on the merchant in the same page as the item: Generally the
merchant's name, next to an image of the merchant's logo; and usually also the
website. Sometimes, but not always, the Site gives the address, email, phone
number, latidude/longitude, et cetera.

Latitude and Longitude
^^^^^^^^^^^^^^^^^^^^^^

Many Daily Item companies also provide, in addition to the address, an inlined
Google Map marking the merchant's location, which can be used to extract the
merchant's Latitude and Longitude. Usually this information is stored in the
Map's URL, which will either be an :code:`iframe` (An embedded map) or a static
image. For example, a static image map whose :code:`src` contains
latitude/longitude data like:

::

  <img src="http://maps.google.com/maps/...ll=-34.9119757494017,-56.1525905296387">

A function, :code:`parse_google_map` is provided in :code:`parsers.py`,
facilitates the process. It takes the raw URL text and returns a pair of floats
with the Longitude and Latitude, or :code:`None`.

Merchant Phone
^^^^^^^^^^^^^^

The merchant's phone is usually in the same tag as the address. Consider two
real world examples:

::

  <div class="location-details f-left" style="width:330px;">
    <h4>Location</h4>
    <p><strong>Greenbelt 3</strong></p>
    <p>Address: 3/F Greenbelt 3, Makati City</p>
    <p>Reservation No.:<strong> </strong>(02) 475-5153, (02) 475-5154</p>
    <p>&nbsp;</p>
    ...
  </div>

::

  <div class="parceiro">
    <img src="/img/logoParceiro/parceiro1941.jpg" alt="KM Tudo" class="parceiroLogo">
    KM Tudo
    <a href="http://www.kmtudo.com.br" target="_blank">www.kmtudo.com.br</a>
    RUA AMADOR BUENO, 116 , CAJURU . PR / CURITIBA-PR- Brasil- CEP: 82960-020
    (41)3093-0202
  </div>

For the above two cases, using :code:`r'\((\d+)\)( )*(\d+)-(\d+)'` as the
regular expression of :code:`phone_re` would fit both cases.

Scraping Items
==============

DayWatch's Scrapy spiders extract some data which they use to build Items
automatically.

Extractors
----------

Extractors are a way of merging many common operations that usually require
overloading a field's :code:`load` method.

The :code:`Extractor` constructor takes three (all optional) keyword arguments:

:code:`xpath`
    An XPath query.

:code:`regexp`
    A regular expression to be run on the XPath matches or on the raw text if no
    XPath is given.

:code:`fn`
    A function to manipulate the matches returned by the XPath and/or regular
    expression. If no matches are present/necessary, it can also be used to
    extract data from the reponse object. It's prototype is
    :code:`(matches,response,self) -> value`.

Extractors don't automatically set anything, they return values that the spider
will then assign to fields. To use extractors in a spider, you map field names
to their corresponding extractors in the :code:`extractors` map:

::

  extractors = {
      'hash_id': Extractor(fn=lambda match,resp,self: response.url().split('/')[-1]),
      ...
      'merchant_phone': Extractor(xpath='//div[@class="merchant"]/p/text()'
                                  regexp=tel_regexp),
  }
