"""
nasa-mcp: a unified MCP server for NASA's public APIs (api.nasa.gov and friends).

One server exposing tools for all 16 APIs listed in the "Browse APIs" section of
api.nasa.gov:

  APOD, Asteroids NeoWs, DONKI, EONET, EPIC, Exoplanet Archive, GIBS, InSight
  (Mars weather), NASA Image & Video Library, Open Science Data Repository,
  Satellite Situation Center, SSD/CNEOS, TechPort, TechTransfer, TLE, and the
  Vesta/Moon/Mars Trek WMTS tile services.

The NASA-hosted endpoints use an API key read from the NASA_API_KEY environment
variable (falling back to DEMO_KEY, which is heavily rate-limited). Get a free key
at https://api.nasa.gov.
"""

from __future__ import annotations

import os
from functools import cache
from typing import Any, Literal, Optional
from urllib.parse import quote

import httpx
from fastmcp import FastMCP

mcp = FastMCP(
    name="nasa-mcp",
    instructions=(
        "Tools for NASA's public APIs. Dates are YYYY-MM-DD unless noted "
        "(DONKI/CNEOS accept the same format). NASA-hosted endpoints use the "
        "NASA_API_KEY env var, defaulting to the rate-limited DEMO_KEY."
    ),
)

NASA = "https://api.nasa.gov"
NASA_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")

@cache
def _http() -> httpx.AsyncClient:
    """Return a process-wide AsyncClient, created lazily on first use."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        headers={"User-Agent": "nasa-mcp/0.1 (+https://api.nasa.gov)"},
        follow_redirects=True,
    )


def _clean(params: dict) -> dict:
    """Drop keys whose value is None (keep False/0/'')."""
    return {k: v for k, v in params.items() if v is not None}


async def _get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None) -> Any:
    try:
        r = await _http().get(url, params=params, headers=headers)
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        body = e.response.text[:300]
        raise RuntimeError(f"{url} -> HTTP {e.response.status_code}: {body}") from e
    except httpx.HTTPError as e:
        raise RuntimeError(f"Request to {url} failed: {e}") from e
    ctype = r.headers.get("content-type", "")
    if "json" in ctype:
        return r.json()
    return {"content_type": ctype, "text": r.text}


# --------------------------------------------------------------------------- #
# APOD — Astronomy Picture of the Day
# --------------------------------------------------------------------------- #
@mcp.tool
async def apod(
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    count: Optional[int] = None,
    thumbs: bool = False,
) -> Any:
    """NASA's Astronomy Picture of the Day: image/video URL, title, and explanation.

    Use `date` for one day, `start_date`+`end_date` for a range, or `count` for N
    random pictures. `thumbs` returns a thumbnail URL for video entries.
    """
    params = _clean(
        {
            "date": date,
            "start_date": start_date,
            "end_date": end_date,
            "count": count,
            "thumbs": thumbs,
            "api_key": NASA_KEY,
        }
    )
    return await _get(f"{NASA}/planetary/apod", params)


# --------------------------------------------------------------------------- #
# Asteroids NeoWs — Near Earth Object Web Service
# --------------------------------------------------------------------------- #
@mcp.tool
async def neo_feed(start_date: str, end_date: Optional[str] = None) -> Any:
    """Near-Earth asteroids by closest-approach date range (max 7 days per request).

    Dates are YYYY-MM-DD; if end_date is omitted the API uses 7 days after start_date.
    """
    return await _get(
        f"{NASA}/neo/rest/v1/feed",
        _clean({"start_date": start_date, "end_date": end_date, "api_key": NASA_KEY}),
    )


@mcp.tool
async def neo_lookup(asteroid_id: str) -> Any:
    """Look up a single asteroid by its NASA JPL small-body (SPK) ID, e.g. '3542519'."""
    return await _get(f"{NASA}/neo/rest/v1/neo/{quote(asteroid_id)}", {"api_key": NASA_KEY})


@mcp.tool
async def neo_browse(page: int = 0, size: int = 20) -> Any:
    """Browse the overall near-Earth asteroid dataset, paginated."""
    return await _get(
        f"{NASA}/neo/rest/v1/neo/browse",
        {"page": page, "size": size, "api_key": NASA_KEY},
    )


# --------------------------------------------------------------------------- #
# DONKI — Space Weather Database Of Notifications, Knowledge, Information
# --------------------------------------------------------------------------- #
@mcp.tool
async def donki(
    service: Literal[
        "CME",
        "CMEAnalysis",
        "GST",
        "IPS",
        "FLR",
        "SEP",
        "MPC",
        "RBE",
        "HSS",
        "WSAEnlilSimulations",
        "notifications",
    ],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    location: Optional[str] = None,
    catalog: Optional[str] = None,
    most_accurate_only: Optional[bool] = None,
    complete_entry_only: Optional[bool] = None,
    speed: Optional[int] = None,
    half_angle: Optional[int] = None,
    keyword: Optional[str] = None,
    notification_type: Optional[str] = None,
) -> Any:
    """Space-weather events from DONKI. Pick a `service`:

      CME, CMEAnalysis, GST (geomagnetic storm), IPS (interplanetary shock),
      FLR (solar flare), SEP, MPC, RBE, HSS, WSAEnlilSimulations, notifications.

    Dates are YYYY-MM-DD. `location`/`catalog` apply to IPS; the CME-analysis knobs
    (`most_accurate_only`, `speed`, `half_angle`, `catalog`, `keyword`) apply to
    CMEAnalysis; `notification_type` (e.g. 'all', 'FLR', 'CME') applies to notifications.
    """
    params: dict[str, Any] = {"startDate": start_date, "endDate": end_date, "api_key": NASA_KEY}
    if service == "IPS":
        params.update(location=location, catalog=catalog)
    elif service == "CMEAnalysis":
        params.update(
            mostAccurateOnly=most_accurate_only,
            completeEntryOnly=complete_entry_only,
            speed=speed,
            halfAngle=half_angle,
            catalog=catalog,
            keyword=keyword,
        )
    elif service == "notifications":
        params.update(type=notification_type)
    return await _get(f"{NASA}/DONKI/{service}", _clean(params))


# --------------------------------------------------------------------------- #
# EONET — Earth Observatory Natural Event Tracker
# --------------------------------------------------------------------------- #
@mcp.tool
async def eonet_events(
    status: Optional[Literal["open", "closed"]] = None,
    limit: Optional[int] = None,
    days: Optional[int] = None,
    source: Optional[str] = None,
    category: Optional[str] = None,
) -> Any:
    """Curated natural events (wildfires, storms, volcanoes, etc.) from EONET v3.

    `status` open/closed, `days` = look-back window, `source` e.g. 'InciWeb',
    `category` an EONET category id (see eonet_categories).
    """
    return await _get(
        "https://eonet.gsfc.nasa.gov/api/v3/events",
        _clean(
            {
                "status": status,
                "limit": limit,
                "days": days,
                "source": source,
                "category": category,
            }
        ),
    )


@mcp.tool
async def eonet_categories() -> Any:
    """List the EONET event categories (wildfires, severe storms, volcanoes, ...)."""
    return await _get("https://eonet.gsfc.nasa.gov/api/v3/categories")


# --------------------------------------------------------------------------- #
# EPIC — Earth Polychromatic Imaging Camera (DSCOVR)
# --------------------------------------------------------------------------- #
@mcp.tool
async def epic(
    collection: Literal["natural", "enhanced"] = "natural",
    date: Optional[str] = None,
    list_available_dates: bool = False,
) -> Any:
    """Full-disc Earth imagery metadata from DSCOVR's EPIC camera.

    Default returns the most recent set. Pass `date` (YYYY-MM-DD) for a specific day,
    or `list_available_dates=True` to list every available date.
    """
    if list_available_dates:
        path = f"/EPIC/api/{collection}/all"
    elif date:
        path = f"/EPIC/api/{collection}/date/{date}"
    else:
        path = f"/EPIC/api/{collection}"
    return await _get(f"{NASA}{path}", {"api_key": NASA_KEY})


# --------------------------------------------------------------------------- #
# Exoplanet Archive (TAP / ADQL)
# --------------------------------------------------------------------------- #
@mcp.tool
async def exoplanet_query(
    query: str, output_format: Literal["json", "csv", "votable"] = "json"
) -> Any:
    """Query NASA's Exoplanet Archive via its TAP service using ADQL (SQL-like).

    Example: "select pl_name, hostname, disc_year from ps where disc_year > 2020".
    Common tables: `ps` (planetary systems), `pscomppars`, `cumulative` (KOI).
    """
    return await _get(
        "https://exoplanetarchive.ipac.caltech.edu/TAP/sync",
        {"query": query, "format": output_format},
    )


# --------------------------------------------------------------------------- #
# GIBS — Global Imagery Browse Services (WMTS tile-URL builder)
# --------------------------------------------------------------------------- #
@mcp.tool
def gibs_tile_url(
    layer: str,
    z: int,
    row: int,
    col: int,
    time: Optional[str] = None,
    projection: str = "epsg4326",
    tile_matrix_set: str = "250m",
    image_format: str = "jpg",
) -> dict:
    """Build a GIBS WMTS REST tile URL (does not fetch — GIBS serves image tiles).

    `layer` is a GIBS layer id (e.g. 'MODIS_Terra_CorrectedReflectance_TrueColor').
    `time` is YYYY-MM-DD for daily layers. Inspect the returned `capabilities` URL to
    discover valid layers, tile matrix sets, and formats.
    """
    t = f"{time}/" if time else "default/"
    base = f"https://gibs.earthdata.nasa.gov/wmts/{projection}/best"
    return {
        "tile_url": f"{base}/{layer}/default/{t}{tile_matrix_set}/{z}/{row}/{col}.{image_format}",
        "capabilities": f"{base}/1.0.0/WMTSCapabilities.xml",
    }


# --------------------------------------------------------------------------- #
# InSight — Mars Weather Service
# --------------------------------------------------------------------------- #
@mcp.tool
async def insight_weather() -> Any:
    """Per-Sol Mars weather (temp, wind, pressure) from the InSight lander.

    Note: the mission has ended, so this returns sparse, historical data with gaps.
    """
    return await _get(
        f"{NASA}/insight_weather/",
        {"api_key": NASA_KEY, "feedtype": "json", "ver": "1.0"},
    )


# --------------------------------------------------------------------------- #
# NASA Image and Video Library (images.nasa.gov)
# --------------------------------------------------------------------------- #
@mcp.tool
async def nivl_search(
    q: str,
    media_type: Optional[Literal["image", "video", "audio"]] = None,
    year_start: Optional[str] = None,
    year_end: Optional[str] = None,
    page: Optional[int] = None,
) -> Any:
    """Search the NASA Image and Video Library (images.nasa.gov)."""
    return await _get(
        "https://images-api.nasa.gov/search",
        _clean(
            {
                "q": q,
                "media_type": media_type,
                "year_start": year_start,
                "year_end": year_end,
                "page": page,
            }
        ),
    )


@mcp.tool
async def nivl_asset(nasa_id: str) -> Any:
    """Get the media-file manifest (downloadable asset URLs) for a NASA media item by nasa_id."""
    return await _get(f"https://images-api.nasa.gov/asset/{quote(nasa_id)}")


# --------------------------------------------------------------------------- #
# OSDR — Open Science Data Repository
# --------------------------------------------------------------------------- #
@mcp.tool
async def osdr_search(
    term: str, from_: int = 0, size: int = 25, data_type: Optional[str] = None
) -> Any:
    """Search OSDR study datasets (space biology / life sciences).

    `data_type` can restrict the source: cgene, nih_geo_gse, ebi_pride, mg_rast.
    """
    return await _get(
        "https://osdr.nasa.gov/osdr/data/search",
        _clean({"term": term, "from": from_, "size": size, "type": data_type}),
    )


@mcp.tool
async def osdr_study_files(accession: str) -> Any:
    """List data files for OSDR study accession(s), e.g. '87' or '137,87-95,153.2'."""
    return await _get(f"https://osdr.nasa.gov/osdr/data/osd/files/{accession}")


@mcp.tool
async def osdr_study_metadata(accession: str) -> Any:
    """Get the full metadata set for an OSDR study accession number, e.g. '137'."""
    return await _get(f"https://osdr.nasa.gov/osdr/data/osd/meta/{accession}")


# --------------------------------------------------------------------------- #
# Satellite Situation Center (SSCWeb)
# --------------------------------------------------------------------------- #
@mcp.tool
async def ssc_observatories() -> Any:
    """List spacecraft/observatories tracked by the Satellite Situation Center.

    Use the returned IDs with SSCWeb's location services for orbit/region queries.
    """
    return await _get(
        "https://sscweb.gsfc.nasa.gov/WS/sscr/2/observatories",
        headers={"Accept": "application/json"},
    )


# --------------------------------------------------------------------------- #
# SSD/CNEOS — Solar System Dynamics / Center for Near-Earth Object Studies
# --------------------------------------------------------------------------- #
@mcp.tool
async def ssd_close_approaches(
    date_min: Optional[str] = None,
    date_max: Optional[str] = None,
    dist_max: Optional[str] = None,
    body: Optional[str] = None,
) -> Any:
    """JPL CNEOS close-approach data (CAD) for asteroids & comets.

    Dates YYYY-MM-DD (or 'now'). `dist_max` e.g. '0.05' (au) or '10LD' (lunar
    distances). `body` defaults to Earth; use 'ALL' for every planet.
    """
    return await _get(
        "https://ssd-api.jpl.nasa.gov/cad.api",
        _clean({"date-min": date_min, "date-max": date_max, "dist-max": dist_max, "body": body}),
    )


@mcp.tool
async def ssd_fireballs(date_min: Optional[str] = None, limit: Optional[int] = None) -> Any:
    """JPL CNEOS fireball atmospheric-impact data reported by US Government sensors."""
    return await _get(
        "https://ssd-api.jpl.nasa.gov/fireball.api",
        _clean({"date-min": date_min, "limit": limit}),
    )


@mcp.tool
async def ssd_sentry(designation: Optional[str] = None) -> Any:
    """JPL CNEOS Sentry Earth-impact risk data.

    Omit `designation` for the summary table of all monitored objects, or pass one
    (e.g. '99942' or '2011 AG5') for object-specific impact details.
    """
    return await _get(
        "https://ssd-api.jpl.nasa.gov/sentry.api",
        _clean({"des": designation}),
    )


# --------------------------------------------------------------------------- #
# TechPort — NASA technology projects
# --------------------------------------------------------------------------- #
@mcp.tool
async def techport_projects(updated_since: Optional[str] = None) -> Any:
    """List TechPort project IDs (optionally only those `updated_since` YYYY-MM-DD)."""
    return await _get(
        f"{NASA}/techport/api/projects",
        _clean({"updatedSince": updated_since, "api_key": NASA_KEY}),
    )


@mcp.tool
async def techport_project(project_id: int) -> Any:
    """Get a single TechPort technology project's full record by numeric ID."""
    return await _get(f"{NASA}/techport/api/projects/{project_id}", {"api_key": NASA_KEY})


# --------------------------------------------------------------------------- #
# TechTransfer — patents, software, spinoffs
# --------------------------------------------------------------------------- #
@mcp.tool
async def tech_transfer(
    category: Literal["patent", "patent_issued", "software", "spinoff"], query: str
) -> Any:
    """Search NASA's TechTransfer catalog. `query` is a free-text search string.

    `category`: patent, patent_issued (how a patent was issued), software, or spinoff.
    """
    url = f"{NASA}/techtransfer/{category}/?{quote(query)}&api_key={NASA_KEY}"
    return await _get(url)


# --------------------------------------------------------------------------- #
# TLE — two-line element sets (tle.ivanstanojevic.me)
# --------------------------------------------------------------------------- #
@mcp.tool
async def tle_search(search: str) -> Any:
    """Search current two-line element sets (orbital data) by satellite name."""
    return await _get("https://tle.ivanstanojevic.me/api/tle", {"search": search})


@mcp.tool
async def tle_get(satellite_number: int) -> Any:
    """Get the current TLE for a satellite by its catalog (NORAD) number, e.g. 25544 (ISS)."""
    return await _get(f"https://tle.ivanstanojevic.me/api/tle/{satellite_number}")


# --------------------------------------------------------------------------- #
# Vesta/Moon/Mars Trek WMTS (tile-URL builder)
# --------------------------------------------------------------------------- #
@mcp.tool
def trek_tile_url(
    body: Literal["moon", "mars", "vesta"],
    product: str,
    z: int,
    row: int,
    col: int,
    tile_matrix_set: str = "default028mm",
    image_format: str = "png",
) -> dict:
    """Build a NASA Trek WMTS tile URL for Moon/Mars/Vesta mosaics (does not fetch).

    `product` is a mosaic identifier (e.g. 'LRO_WAC_Mosaic_Global_303ppd_v02').
    Some products serve .jpg instead of .png and use a different tile matrix set —
    confirm against the per-body capabilities listing returned below.
    """
    host = {
        "moon": "https://trek.nasa.gov/tiles/Moon",
        "mars": "https://trek.nasa.gov/tiles/Mars",
        "vesta": "https://trek.nasa.gov/tiles/Vesta",
    }[body]
    tile_url = (
        f"{host}/EQ/{product}/1.0.0/default/{tile_matrix_set}"
        f"/{z}/{row}/{col}.{image_format}"
    )
    return {
        "tile_url": tile_url,
        "capabilities_listing": f"https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body={body}",
    }


def main() -> None:
    """Console entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
