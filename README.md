# nasa-mcp

A unified [MCP](https://modelcontextprotocol.io) server that exposes the 16 APIs in the [NASA API portal](https://api.nasa.gov) and two NASA Earthdata APIs, CMR Search and Harmony.

Built with [FastMCP](https://gofastmcp.com) + httpx, and shipped as a Docker image so it runs with **nothing but Docker** on your machine — no Python, uv, or pyenv required.

## What's covered

33 tools across 18 APIs:

| API | Tools |
|-----|-------|
| APOD | `apod` |
| Asteroids NeoWs | `neo_feed`, `neo_lookup`, `neo_browse` |
| CMR Search | `cmr_search_collections`, `cmr_search_granules`, `cmr_request` |
| DONKI (space weather) | `donki` (CME, GST, FLR, IPS, SEP, MPC, RBE, HSS, CMEAnalysis, WSAEnlilSimulations, notifications) |
| EONET | `eonet_events`, `eonet_categories` |
| EPIC | `epic` |
| Exoplanet Archive | `exoplanet_query` (ADQL via TAP) |
| GIBS | `gibs_tile_url` (WMTS tile-URL builder) |
| Harmony | `harmony_capabilities`, `harmony_submit_subset`, `harmony_job_status`, `harmony_request` |
| Mars weather (Curiosity/MSL) | `mars_weather` |
| NASA Image & Video Library | `nivl_search`, `nivl_asset` |
| Open Science Data Repository | `osdr_search`, `osdr_study_files`, `osdr_study_metadata` |
| Satellite Situation Center | `ssc_observatories` |
| SSD/CNEOS | `ssd_close_approaches`, `ssd_fireballs`, `ssd_sentry` |
| TechPort | `techport_projects`, `techport_project` |
| TechTransfer | `tech_transfer` |
| TLE | `tle_search`, `tle_get` |
| Vesta/Moon/Mars Trek | `trek_tile_url` (WMTS tile-URL builder) |

Per-API parameter reference lives in [`docs/`](docs/).

## Build

You need only **Docker** installed and running. The image isn't published to a registry, so build it once from the repo root:

```bash
docker build -t nasa-mcp .
```

That produces a local image named `nasa-mcp`. Everything below uses it. Because the image is local-only, the build must come **before** any `docker run` — otherwise Docker tries to pull a registry image that doesn't exist and fails. (Confirm it built with `docker images nasa-mcp`.)

## API key

Keyed NASA endpoints (APOD, NeoWs, EPIC, TechPort, TechTransfer) read your key from the `NASA_API_KEY` environment variable and fall back to `DEMO_KEY` if it's unset. `DEMO_KEY` is heavily rate-limited (30 req/hr, 50 req/day), so get a free key in seconds at <https://api.nasa.gov>.

DONKI uses the public `https://ccmc.gsfc.nasa.gov/DONKI-API/get/` endpoint and needs no API key. This replaces the retired DONKI route following [NASA's September 30, 2026 migration](https://ccmc.gsfc.nasa.gov/news/major-updates/). Its service options and parameters are unchanged.

You pass the key into the container at runtime with `-e` — it is never baked into the image:

```bash
docker run --rm -i -e NASA_API_KEY=your_key_here nasa-mcp
```

The non-NASA-hosted services (EONET, Exoplanet Archive, Mars weather, NIVL, OSDR, SSC, SSD/CNEOS, TLE, GIBS, Trek) need no key. `mars_weather` pulls Curiosity's live REMS feed from `mars.nasa.gov`, which is keyless.

> **Security note:** the key lives only in your `docker run -e` flag or your MCP client config — never commit it. `.dockerignore` keeps `.env` out of the build context (so it can't be baked into the image) and `.gitignore` excludes `.env` from version control.

## Earthdata and LiDAR

Public CMR searches work without a token. For Harmony processing and authorized CMR metadata, generate a bearer token from your [Earthdata Login profile](https://urs.earthdata.nasa.gov/) and set `EARTHDATA_TOKEN` in the server environment. With Docker, pass an existing environment variable with `-e EARTHDATA_TOKEN` or use `--env-file .env` with a local copy of `.env.example`. Use the same flags in your MCP client's Docker arguments.

1. Search collections by short name, for example `GEDI02_A` version `002`, `ATL03`, or `ATL08`. Use the collection concept ID with `cmr_search_granules` to look up source files for an area and time range. The `cmr-search-after` response header can be passed as `search_after` on the next page with the same filters. [CMR Search documentation](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)
2. Call `harmony_capabilities` with the collection ID to see its supported filters, formats, and variables. For a first subset, pass the ID, a bounding box in west, south, east, north order, and a date range to `harmony_submit_subset`. Pass `max_results: 1` to limit an initial request to one input file. [Harmony capabilities and Coverages API](https://harmony.earthdata.nasa.gov/docs)
3. Pass the returned `data.jobID` to `harmony_job_status` and use the result links from the finished job. Harmony controls the output formats and expiry. [Harmony Jobs API](https://harmony.earthdata.nasa.gov/docs#monitoring-jobs-with-the-jobs-api-and-the-workflow-ui)

### Advanced Earthdata requests

`cmr_request` accepts documented consumer paths under `/search/`, including concept and revision lookups, services, variables, tags, facets, timeline, holdings, and associations. Send JSON queries in `body.json_body`, AQL XML in `body.text` with `body.content_type: application/xml`, or form fields in `body.form`. Use `search_after` or `scroll_id` for the corresponding CMR pagination header. [CMR Search API reference](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)

`harmony_request` accepts Harmony's OGC Coverages, EDR, and WMS paths, plus job listing, bulk status, steps, pause, resume, cancel, preview control, labels, STAC, and S3 staging endpoints. For most transformations set `forceAsync: true` to get staged files through the Jobs API. `/cloud-access` returns temporary AWS credentials in the tool response. NASA controls access to restricted operations on both APIs. [Harmony API reference](https://harmony.earthdata.nasa.gov/docs)

Both tools accept exact upstream parameter names in `query`. Use arrays for repeated parameters. For multipart uploads, use `body.files` entries with `field`, `filename`, `content_type`, and `base64_data`, and optionally `body.form` for other fields. Set `field` to `shapefile` for CMR and Harmony Coverages uploads. Responses include `status_code`, selected `headers`, and JSON in `data`, textual results in `text`, small binary results in `base64_data`, or a redirect in `location`. Large Harmony WMS images and existing staged files can return a direct `download_url`. For other oversized responses, narrow the search or request asynchronous processing for staged file links.

## Run

The server speaks MCP over **stdio**, so run it interactively:

```bash
docker run --rm -i -e NASA_API_KEY=your_key_here nasa-mcp
```

It then waits on stdin for a JSON-RPC handshake — that's expected; your MCP client drives the conversation (Ctrl-C to exit). Keep `-i` so stdin stays open, and do **not** add `-t`: a TTY corrupts the stdio JSON-RPC stream.

## Use it from Claude

Build the image first (`docker build -t nasa-mcp .`). The tag `nasa-mcp` refers to that **local** image — there is no registry copy, so if you skip the build the client will fail trying to pull it.

**Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nasa": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "NASA_API_KEY", "nasa-mcp"],
      "env": { "NASA_API_KEY": "your_key_here" }
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add nasa --env NASA_API_KEY=your_key_here -- docker run --rm -i -e NASA_API_KEY nasa-mcp
```

`-e NASA_API_KEY` (a bare name, no `=value`) copies the variable from `docker run`'s own environment into the container; the client supplies its value from the `env` block. So the key stays out of the argument list and is never baked into the image. `docker` must be on your client's `PATH` — Docker Desktop puts it there automatically.

Then ask things like *"Show me today's APOD,"* *"Which asteroids pass within 5 lunar distances this month?"*, or *"Any geomagnetic storms logged by DONKI last week?"*

## Notes

- `gibs_tile_url` and `trek_tile_url` **construct** WMTS tile URLs rather than fetching them (those services return image tiles, not JSON). Each returns a capabilities URL so an agent can discover valid layers/products, matrix sets, and formats.
- `exoplanet_query` takes raw ADQL, e.g. `select pl_name, hostname, disc_year from ps where disc_year > 2020`.
- Trek tile paths are best-effort; some mosaics use `.jpg` or a different tile matrix set — verify against the per-body capabilities listing the tool returns.

## The RYASTRA fleet

| Repo | What it is |
|---|---|
| [nasa-defense](https://github.com/RYASTRA/nasa-defense) | Planetary-defense watch (the original watcher engine) |
| **nasa-mcp** | NASA API portal and Earthdata tools as an MCP server *(this repo)* |
| [nasa-new-worlds](https://github.com/RYASTRA/nasa-new-worlds) | New-worlds watch — exoplanet confirmations |
| [nasa-observatory](https://github.com/RYASTRA/nasa-observatory) | Fleet dashboard — one tile per watcher |
| [nasa-space-biology](https://github.com/RYASTRA/nasa-space-biology) | Faceted explorer for OSDR space-biology studies |
| [nasa-space-weather](https://github.com/RYASTRA/nasa-space-weather) | Space-weather watch |
| [nasa-tech-explorer](https://github.com/RYASTRA/nasa-tech-explorer) | NASA patents, free software & spinoffs — searchable |
