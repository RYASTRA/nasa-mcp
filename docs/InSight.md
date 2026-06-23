# InSight: Mars Weather Service API

> **In plain terms:** Daily weather readings (temperature, wind, pressure) from NASA's InSight lander on Mars for the last seven Martian days, returned as JSON. Note the mission has ended, so the data is historical and often has gaps.

(Last Updated: 3/30/2021)

**THIS SERVICE HAS SIGNIFICANT MISSING DATA DUE TO INSIGHT NEEDING TO MANAGE POWER USE:** Please check out the seasonal weather report plot for an illustration of missing data and read this article about how dust and distance from the sun affect Insight's power situation.

NASA's InSight Mars lander takes continuous weather measurements (temperature, wind, pressure) on the surface of Mars at Elysium Planitia, a flat, smooth plain near Mars' equator. Please note that there are sometimes problems with the sensors on Mars that result in missing data! If you see a long gap, a search result may bring up more information on whether it is a long-lasting problem. Summaries of these data are available at [https://mars.nasa.gov/insight/weather/](https://mars.nasa.gov/insight/weather/).

This API provides per-Sol summary data for each of the last seven available Sols (Martian Days). As more data from a particular Sol are downlinked from the spacecraft (sometimes several days later), these values are recalculated, and consequently may change as more data are received on Earth. Additionally, please note that wind and other sensor data may not exist for certain date ranges. You can check out [https://mars.nasa.gov/insight/weather/](https://mars.nasa.gov/insight/weather/) and scroll down to the 'seasonal weather report' you'll see the gaps where no data exists for some sensors.

This API is maintained and provided by NASA Jet Propulsion Laboratory and Cornell University. If you find bugs in this API, please use the contact form found at [https://mars.nasa.gov/feedback/](https://mars.nasa.gov/feedback/). The rate limit for this API is every hour no more than 2000 hits for each individual IP.

## Defining the Data

The summary data are provided as an object in a JSON stream, a formal definition of JSON is RFC 7159. Appendix A contains an abridged, typical JSON stream for this API as an example.

## HTTP Request

`GET https://api.nasa.gov/insight_weather/?api_key=DEMO_KEY&feedtype=json&ver=1.0`

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|--------|---------|-------------|
| version | float | 1.0 | The version of this API |
| feedtype | string | json | The format of what is returned. Currently the default is JSON and only JSON works. |
| api_key | string | DEMO_KEY | api.data.gov key for expanded usage |

## Example query

```
https://api.nasa.gov/insight_weather/?api_key=DEMO_KEY&feedtype=json&ver=1.0
```
