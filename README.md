# nasa-mcp

A unified [MCP](https://modelcontextprotocol.io) server that exposes **all 16 of NASA's public APIs** (from the "Browse APIs" section of [api.nasa.gov](https://api.nasa.gov)) as tools an AI agent can call — one server, one config entry, the whole catalog.

Built with [FastMCP](https://gofastmcp.com) (tested on FastMCP 3.4) + httpx, and shipped as a Docker image so it runs with **nothing but Docker** on your machine — no Python, uv, or pyenv required.

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
| Mars weather (Curiosity/MSL) | `mars_weather` |
| NASA Image & Video Library | `nivl_search`, `nivl_asset` |
| Open Science Data Repository | `osdr_search`, `osdr_study_files`, `osdr_study_metadata` |
| Satellite Situation Center | `ssc_observatories` |
| SSD/CNEOS | `ssd_close_approaches`, `ssd_fireballs`, `ssd_sentry` |
| TechPort | `techport_projects`, `techport_project` |
| TechTransfer | `tech_transfer` |
| TLE | `tle_search`, `tle_get` |
| Vesta/Moon/Mars Trek | `trek_tile_url` (WMTS tile-URL builder) |

## Build

You need only **Docker** installed and running. The image isn't published to a registry, so build it once from the repo root:

```bash
docker build -t nasa-mcp .
```

That produces a local image named `nasa-mcp`. Everything below uses it. Because the image is local-only, the build must come **before** any `docker run` — otherwise Docker tries to pull a registry image that doesn't exist and fails. (Confirm it built with `docker images nasa-mcp`.)

## API key

NASA-hosted endpoints (APOD, NeoWs, DONKI, EPIC, TechPort, TechTransfer) read your key from the `NASA_API_KEY` environment variable and fall back to `DEMO_KEY` if it's unset. `DEMO_KEY` works for light testing but is rate-limited (30 req/hr, 50 req/day). Grab a free key in seconds at <https://api.nasa.gov>.

You pass the key into the container at runtime with `-e` — it is never baked into the image:

```bash
docker run --rm -i -e NASA_API_KEY=your_key_here nasa-mcp
```

The non-NASA-hosted services (EONET, Exoplanet Archive, Mars weather, NIVL, OSDR, SSC, SSD/CNEOS, TLE, GIBS, Trek) need no key. `mars_weather` pulls Curiosity's live REMS feed from `mars.nasa.gov`, which is keyless.

> **Security note:** the key lives only in your `docker run -e` flag or your MCP client config — never commit it. `.dockerignore` keeps `.env` out of the build context (so it can't be baked into the image) and `.gitignore` excludes `.env` from version control.

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

## Development

Run the test suite entirely in a container — no Python on your host:

```bash
docker build --target test -t nasa-mcp-test .
docker run --rm nasa-mcp-test
```

The `test` stage (see the [`Dockerfile`](Dockerfile)) installs the dev extras and runs `pytest` against `tests/`.

## Notes

- `gibs_tile_url` and `trek_tile_url` **construct** WMTS tile URLs rather than fetching them (those services return image tiles, not JSON). Each returns a capabilities URL so an agent can discover valid layers/products, matrix sets, and formats.
- `exoplanet_query` takes raw ADQL, e.g. `select pl_name, hostname, disc_year from ps where disc_year > 2020`.
- Trek tile paths are best-effort; some mosaics use `.jpg` or a different tile matrix set — verify against the per-body capabilities listing the tool returns.
