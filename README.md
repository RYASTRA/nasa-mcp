# nasa-mcp

A unified [MCP](https://modelcontextprotocol.io) server that exposes **all 16 of NASA's public APIs** (from the "Browse APIs" section of [api.nasa.gov](https://api.nasa.gov)) as tools an AI agent can call — one server, one config entry, the whole catalog.

Built with [FastMCP](https://gofastmcp.com) (tested on FastMCP 3.4) + httpx.

## What's covered

26 tools across 16 APIs:

| API | Tools |
|-----|-------|
| APOD | `apod` |
| Asteroids NeoWs | `neo_feed`, `neo_lookup`, `neo_browse` |
| DONKI (space weather) | `donki` (CME, GST, FLR, IPS, SEP, MPC, RBE, HSS, CMEAnalysis, WSAEnlilSimulations, notifications) |
| EONET | `eonet_events`, `eonet_categories` |
| EPIC | `epic` |
| Exoplanet Archive | `exoplanet_query` (ADQL via TAP) |
| GIBS | `gibs_tile_url` (WMTS tile-URL builder) |
| InSight (Mars weather) | `insight_weather` |
| NASA Image & Video Library | `nivl_search`, `nivl_asset` |
| Open Science Data Repository | `osdr_search`, `osdr_study_files`, `osdr_study_metadata` |
| Satellite Situation Center | `ssc_observatories` |
| SSD/CNEOS | `ssd_close_approaches`, `ssd_fireballs`, `ssd_sentry` |
| TechPort | `techport_projects`, `techport_project` |
| TechTransfer | `tech_transfer` |
| TLE | `tle_search`, `tle_get` |
| Vesta/Moon/Mars Trek | `trek_tile_url` (WMTS tile-URL builder) |

## Setup

Requires Python 3.10+. Using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
cd nasa-mcp
uv sync
```

Or with pip:

```bash
cd nasa-mcp
pip install -e .
```

## API key

NASA-hosted endpoints (APOD, NeoWs, DONKI, EPIC, InSight, TechPort, TechTransfer) read your key from the `NASA_API_KEY` environment variable and fall back to `DEMO_KEY` if it's unset. `DEMO_KEY` works for light testing but is rate-limited (30 req/hr, 50 req/day). Grab a free key in seconds at <https://api.nasa.gov>.

```bash
export NASA_API_KEY=your_key_here
```

The non-NASA-hosted services (EONET, Exoplanet Archive, NIVL, OSDR, SSC, SSD/CNEOS, TLE, GIBS, Trek) need no key.

> **Security note:** keep your key out of version control — set it as an environment variable or in a local `.env` (see `.env.example`), which the standard Python `.gitignore` already excludes. Don't commit it to the repo.

## Run

```bash
uv run nasa-mcp        # stdio transport
# or
python -m nasa_mcp.server
```

## Use it from Claude

**Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nasa": {
      "command": "uv",
      "args": ["run", "--directory", "/ABSOLUTE/PATH/TO/rynasa/nasa-mcp", "nasa-mcp"],
      "env": { "NASA_API_KEY": "your_key_here" }
    }
  }
}
```

**Claude Code** — from the repo:

```bash
claude mcp add nasa --env NASA_API_KEY=your_key_here -- uv run --directory "$(pwd)/nasa-mcp" nasa-mcp
```

Then ask things like *"Show me today's APOD,"* *"Which asteroids pass within 5 lunar distances this month?"*, or *"Any geomagnetic storms logged by DONKI last week?"*

## Notes

- `gibs_tile_url` and `trek_tile_url` **construct** WMTS tile URLs rather than fetching them (those services return image tiles, not JSON). Each returns a capabilities URL so an agent can discover valid layers/products, matrix sets, and formats.
- `exoplanet_query` takes raw ADQL, e.g. `select pl_name, hostname, disc_year from ps where disc_year > 2020`.
- Trek tile paths are best-effort; some mosaics use `.jpg` or a different tile matrix set — verify against the per-body capabilities listing the tool returns.
