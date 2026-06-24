# Mars Weather: Curiosity Rover (MSL / REMS)

> **In plain terms:** Daily weather readings (temperature, pressure, atmospheric opacity, UV) from NASA's Curiosity rover at Gale Crater on Mars, returned as JSON. Unlike the retired InSight lander, Curiosity is still operating, so this feed is current — typically updated within a few days.

**Tool:** `mars_weather`

## Why this replaced InSight

The original tool read NASA's InSight Mars Weather Service (`api.nasa.gov/insight_weather`). InSight was retired in December 2022 and that endpoint now only returns sparse historical data ending around October 2020. This tool instead reads the **Curiosity (MSL) REMS** weather feed published by mars.nasa.gov, which is kept current.

The Curiosity feed is maintained by the Centro de Astrobiología (CAB) in Spain, which operates the REMS (Rover Environmental Monitoring Station) instrument. It is provided for outreach purposes (see the `disclaimer` field in every response).

## HTTP Request

No API key is required — this endpoint is on `mars.nasa.gov`, not `api.nasa.gov`. Note the trailing slash on `/api/`; without it the server issues a 301 redirect.

```
GET https://mars.nasa.gov/rss/api/?feed=weather&category=msl&feedtype=json&ver=1.0
```

## Tool parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit`   | int  | 10      | Max sols to return, newest first. Use `0` for the full mission (~4,700 sols, ~1.7 MB). |
| `sol`     | int  | —       | Return only this Martian day number. |
| `date`    | str  | —       | Return only this Earth date (`YYYY-MM-DD`). |

The upstream feed returns the **entire mission** (every sol since landing in 2012, newest-first) in a single response, so the tool filters and slices locally rather than paging the API.

## Response shape

```jsonc
{
  "source": "NASA/JPL-Caltech & Centro de Astrobiología (CAB) — Curiosity rover REMS, via mars.nasa.gov",
  "disclaimer": "The information contained into this file is provided by Centro de Astrobiologia (CAB) ...",
  "sol_count": 10,
  "soles": [
    {
      "sol": 4931,
      "terrestrial_date": "2026-06-20",
      "ls": 304,                 // solar longitude (deg)
      "season": "Month 11",
      "min_air_temp_c": -68,
      "max_air_temp_c": -3,
      "min_ground_temp_c": -78,
      "max_ground_temp_c": 5,
      "pressure_pa": 806,
      "pressure_trend": "Higher",
      "abs_humidity": null,      // REMS humidity sensor degraded -> usually null
      "wind_speed": null,        // REMS wind sensor degraded -> usually null
      "wind_direction": "--",
      "atmo_opacity": "Sunny",
      "uv_index": "Moderate",
      "sunrise": "06:36",
      "sunset": "18:50"
    }
  ]
}
```

### Field notes

- **Temperatures** are in °C. `*_air_temp_c` are atmospheric (air) readings; `*_ground_temp_c` are ground/surface readings (the raw feed's `gts` = ground temperature sensor).
- **Pressure** is in pascals (Pa).
- **Degraded sensors:** Curiosity's wind and humidity sensors no longer return reliable data, so `wind_speed`/`abs_humidity` are usually `null` and `wind_direction` is usually `"--"`. The tool maps the raw `"--"` placeholder to `null` for numeric fields rather than coercing it.
- **`ls`** is the solar longitude in degrees (Mars' position in its orbit; 0/90/180/270 mark the seasons).

## Credit & rate limits

Data courtesy of NASA/JPL-Caltech and the Centro de Astrobiología (CAB). The feed is intended for outreach purposes only; see the `disclaimer` field returned with every response.
