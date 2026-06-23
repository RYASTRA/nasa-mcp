# SSD/CNEOS

> **In plain terms:** JPL's hub for solar system dynamics and near-Earth object data, bundling several services: close approaches (CAD), fireball impacts, mission design, human-accessible asteroids (NHATS), new-object tracking (Scout), and impact-risk assessment (Sentry).

Welcome to JPL's SSD (Solar System Dynamics) and CNEOS (Center for Near-Earth Object Studies) API (Application Program Interface) service. This service provides an interface to machine-readable data (JSON-format) related to SSD and CNEOS. If you are looking for human-readable data, please go to the main websites for SSD and/or CNEOS. For further information on this API and its component services, please visit the JPL SSD/CNEOS API main website or contact contact-ssd-api@jpl.nasa.gov.

This API consists of the following component services:

| API | Description |
|-----|-------------|
| [CAD](http://ssd-api.jpl.nasa.gov/doc/cad.html) | Asteroid and comet close approaches to the planets in the past and future |
| [Fireball](http://ssd-api.jpl.nasa.gov/doc/fireball.html) | Fireball atmospheric impact data reported by US Government sensors |
| [Mission Design](https://ssd-api.jpl.nasa.gov/doc/mdesign.html) | Mission Design - Small-body mission design suite |
| [NHATS](http://ssd-api.jpl.nasa.gov/doc/nhats.html) | Human-accessible NEOs data |
| [Scout](https://ssd-api.jpl.nasa.gov/doc/scout.html) | NEOCP orbits, ephemerides, and impact risk data |
| [Sentry](http://ssd-api.jpl.nasa.gov/doc/sentry.html) | NEO Earth impact risk assessment data |

## CAD

This API provides access to current close-approach data for all asteroids and comets in JPL's SBDB (Small-Body DataBase). Defaults for query parameters are setup for a typical CNEOS web-site search: NEO Earth close-approaches less than 0.05 au in the next 60 days sorted by date.

For complete API documentation please visit the [JPL SBDB Close-Approach Data API](http://ssd-api.jpl.nasa.gov/doc/cad.html) website.

## Fireball

The fireball data API provides a method of requesting specific records from the available data-set. Every successful query will return content representing one or more fireball data records. See the CNEOS page on fireballs for details on this data-set.

For complete API documentation please visit the [JPL Fireball Data API](http://ssd-api.jpl.nasa.gov/doc/fireball.html) website.

## Mission Design

This API provides access to the JPL/SSD small-body mission design suite. Please see the Mission Design web-page for details about Mission Design.

For complete API documentation please visit the [JPL Mission Design API](https://ssd-api.jpl.nasa.gov/doc/mdesign.html) website.

## NHATS

The NHATS API provides a method of requesting data from the NHATS-related tables in the SBDB. These data will primarily support the CNEOS "Accessible NEAs" web-page. Please see the NHATS web-page for details about NHATS.

For complete API documentation please visit the [JPL NHATS API](http://ssd-api.jpl.nasa.gov/doc/nhats.html) website.

## Scout

This API provides access to near-realtime results from the CNEOS Scout system. Various query modes provide access to available subsets of data. Please see the Scout web-page for details about Scout.

For complete API documentation please visit the [JPL Scout API](https://ssd-api.jpl.nasa.gov/doc/scout.html) website.

## Sentry

This API provides access to results from the CNEOS Sentry system. There are various "modes" used to obtain desired data.

- O - object-specific details table
- S - summary table
- V - VI (virtual impactor) table
- R - removed-objects table

For complete API documentation please visit the [JPL Sentry API](http://ssd-api.jpl.nasa.gov/doc/sentry.html) website.
