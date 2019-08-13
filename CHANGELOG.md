# Changes

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
