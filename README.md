# python-aio-geojson-client

[![Build Status](https://github.com/exxamalte/python-aio-geojson-client/workflows/CI/badge.svg?branch=master)](https://github.com/exxamalte/python-aio-geojson-client/actions?workflow=CI)
[![codecov](https://codecov.io/gh/exxamalte/python-aio-geojson-client/branch/master/graph/badge.svg?token=FHM8U3HT33)](https://codecov.io/gh/exxamalte/python-aio-geojson-client)
[![PyPi](https://img.shields.io/pypi/v/aio-geojson-client.svg)](https://pypi.python.org/pypi/aio-geojson-client)
[![Version](https://img.shields.io/pypi/pyversions/aio-geojson-client.svg)](https://pypi.python.org/pypi/aio-geojson-client)
[![Maintainability](https://api.codeclimate.com/v1/badges/4f7b12fe27fc845b5712/maintainability)](https://codeclimate.com/github/exxamalte/python-aio-geojson-client/maintainability)

This library provides convenient async access to 
[GeoJSON](https://tools.ietf.org/html/rfc7946) Feeds.

## Installation
`pip install aio-geojson-client`

## Known Implementations

| Library  | Source  | Topic  |
|----------|---------|--------|
| [aio_geojson_geonetnz_quakes](https://github.com/exxamalte/python-aio-geojson-geonetnz-quakes)     | GeoNet New Zealand Quakes  | Earthquakes |
| [aio_geojson_geonetnz_volcano](https://github.com/exxamalte/python-aio-geojson-geonetnz-volcano)   | GeoNet New Zealand Volcano | Volcanoes   |
| [aio_geojson_nsw_rfs_incidents](https://github.com/exxamalte/python-aio-geojson-nsw-rfs-incidents) | NSW Rural Fire Service     | Fires       |


## Usage
Each implementation extracts relevant information from the GeoJSON feed. Not 
all feeds contain the same level of information, or present their information 
in different ways.

After instantiating a particular class and supply the required parameters, you 
can call `update` to retrieve the feed data. The return value will be a tuple 
of a status code and the actual data in the form of a list of feed entries 
specific to the selected feed.
Alternatively, calling method `update_override` allows passing in ad-hoc filters
that override the globally defined filters.

Status Codes
* _OK_: Update went fine and data was retrieved. The library may still 
  return empty data, for example because no entries fulfilled the filter 
  criteria.
* _OK_NO_DATA_: Update went fine but no data was retrieved, for example 
  because the server indicated that there was not update since the last request.
* _ERROR_: Something went wrong during the update

## Feed Manager

The Feed Manager helps managing feed updates over time, by notifying the 
consumer of the feed about new feed entries, updates and removed entries 
compared to the last feed update.

* If the current feed update is the first one, then all feed entries will be 
  reported as new. The feed manager will keep track of all feed entries' 
  external IDs that it has successfully processed.
* If the current feed update is not the first one, then the feed manager will 
  produce three sets:
  * Feed entries that were not in the previous feed update but are in the 
    current feed update will be reported as new.
  * Feed entries that were in the previous feed update and are still in the 
    current feed update will be reported as to be updated.
  * Feed entries that were in the previous feed update but are not in the 
    current feed update will be reported to be removed.
* If the current update fails, then all feed entries processed in the previous
  feed update will be reported to be removed.

After a successful update from the feed, the feed manager provides two
different dates:

* `last_update` will be the timestamp of the last update from the feed 
  irrespective of whether it was successful or not.
* `last_update_successful` will be the timestamp of the last successful update 
  from the feed. This date may be useful if the consumer of this library wants 
  to treat intermittent errors from feed updates differently.
* `last_timestamp` (optional, depends on the feed data) will be the latest 
  timestamp extracted from the feed data. 
  This requires that the underlying feed data actually contains a suitable 
  date. This date may be useful if the consumer of this library wants to 
  process feed entries differently if they haven't actually been updated.
