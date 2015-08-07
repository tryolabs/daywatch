********
Fixtures
********

The file :code:`core/fixtures/initial_data.yaml` includes data to be loaded when
the database is first created. This is largely unchanging data that is
represented in an RDBMS because of its relations, but otherwise should not be
mutable.

Languages
=========

These are used to classify sites into different languages.

::

  # Example entry
  - model: core.Language
    pk: 1
    fields:
      code: 'en'
      name: 'English'

Countries
=========

This is a list of countries DayWatch can build sites in. Support for a new
country can be added either by editing this file or through the Django Admin
interface. Countries also reference languages (If a country has multiple
languages, the one that is usually used in the country's sites should be
used. For example, the official language of Malaysia is Malay, but most daily
deal sites are in English or have English versions).

::

  # Example entry
  - model: core.Country
    pk: 1
    fields:
      name: USA
      code: us
      timezone: America/New_York
      lang: 1

Currencies
==========

Currency objects are not strictly immutable, as their exchange rate relative to
US dollars is updated periodically from a web service.

The :code:`text` field determines how the currency should be displayed. The
:code:`regex` field determines how a currency is identified from a string of
text containing the currency symbol and the price of an item.

::

  # Example entry
  - model: core.Currency
    pk: 1
    fields:
      country: 1
      iso_code: USD
      us_change: 1.0
      regex: "[Uu]\\$[Ss]"
      text: U$S

Categories
==========

Items are partitioned into different categories by the classifier, and the
classifier table contains the list of different categories that can be
used. Note that categories form a tree on the MonkeyLearn side, but we don't
really need to represent this, so we just store a set of category objects with
their label (:code:`name`).

::

  # Example entry
  - model: core.Category
    pk: 2
    fields:
      name: Entertainment & Recreation
