******
Panels
******

DayWatch includes a set of panels, which are pages with some form for querying
the database and generating reports, usually in the form of plots.

Panels
======

.. _items-panel:

Items Panel
-----------

.. image:: img/items-panel.png

The Items Panel allows the user to query the item database and displays selected
fields in a table.

.. _analytics-panel:

Analytics Panel
---------------

.. image:: img/analytics-panel.png

Trends Panel
------------

The Trends Panel shows the change over time of various variables in items.

Spiders Panel
-------------

.. image:: img/spiders-panel.png

The Spiders Panel is used to monitor the state of the Scrapy web spiders. It
reports the number of items they scraped as well as their current state.

Producing Reports
=================

Plots
-----

`D3`_ is a powerful, declarative data visualization library. For our purposes,
however, the full power of D3 is not required, so we limit ourselves to `NVD3`_,
an abstraction layer that provides reusable functions for creating the most
common types of charts.

DayWatch uses a small Javascript library, `nvd3-tags`_, originally developed for
internal use, that generates NVD3 charts from data embedded in the markup of a
page.

:code:`nvd3-tags` uses two non-standard tags, :code:`<chart>` and
:code:`<data>`. An example is:

::

  <chart type="line"
         title="Sales"
         x-date-format="%x"
         y-format=",.2f">
    <data>
      Date,Widgets Sold
      1396530554328,145.2
      1396530556789,120.0
      1396530578473,333.1
    </data>
  </chart>

.. _D3: http://d3js.org/
.. _NVD3: http://nvd3.org/
.. _nvd3-tags: http://tryolabs.github.io/nvd3-tags/
