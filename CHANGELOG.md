# Changes

## 0.15 (15/06/2021)
* Set aiohttp to a release 3.7.4 or later (thanks @fabaff).
* Add license tag (thanks @fabaff).
* Migrated to github actions.

## 0.14 (25/04/2021)
* Allow overriding filters on update (with backwards compatibility).
* Exclude tests subpackages from distribution (thanks @scop).
* Code housekeeping (black formatting, isort, flake8).
* Python 3.9 support.

## 0.13 (18/02/2020)
* Fixes extraction of polygons from a feed (polygon without hole only).

## 0.12 (14/02/2020)
* Added type hints.
* Improved internal handling of GeoJSON geometry data.
* Retain backwards compatibility with v0.11 for downstream libraries.

## 0.11 (05/11/2019)
* Python 3.8 compatibility.

## 0.10 (24/09/2019)
* Handle timeout error when fetching data from feed.
* Improve log message when error occurs while fetching data.

## 0.9 (19/09/2019)
* Fix feed manager external ID handling.

## 0.8 (18/09/2019)
* Makes feed manager base class more modular for overriding classes.

## 0.7 (14/08/2019)
* Add ability to override client session timeout in sub-classes of feed.

## 0.6 (13/08/2019)
* Reset last timestamp when update fails.
* Improves code and test coverage.
* Add request timeout of 10 seconds.

## 0.5 (12/08/2019)
* Added total number of managed entries to status callback info.

## 0.4 (10/08/2019)
* Added time of last successful update from feed and last update in general.
* Added status callback to let subscriber know about feed update details.

## 0.3 (29/07/2019)
* Improved handling errors while establishing client connection.

## 0.2 (26/07/2019)
* Changed feed manager callbacks to async.
* Removed unused dependency `pytz`.

## 0.1 (21/07/2019)
* Initial release as base for GeoJSON feeds.
* Calculating distance to home coordinates.
* Support for filtering by distance.
* Filter out entries without any geo location data.
* Simple Feed Manager.
