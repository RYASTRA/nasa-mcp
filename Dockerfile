# syntax=docker/dockerfile:1
#
# nasa-mcp — runs the MCP server over stdio inside a container so it can be
# launched with `docker run --rm -i nasa-mcp` and needs no Python/uv/pyenv on
# the host. The NASA API key is supplied at runtime via -e NASA_API_KEY, never
# baked into the image.
#
# Build the server image (default):  docker build -t nasa-mcp .
# Build + run the tests:             docker build --target test -t nasa-mcp-test . && docker run --rm nasa-mcp-test

FROM python:3.14.6-slim AS base

# PYTHONUNBUFFERED keeps the stdio JSON-RPC stream flowing (no buffered stalls).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy only what the build backend (hatchling) needs: project metadata, the
# readme it references, and the src/ package.
COPY pyproject.toml README.md ./
COPY src ./src

# Install the server + dependencies into the image's site-packages. This
# exposes the `nasa-mcp` console script on PATH.
RUN pip install .

# Run as an unprivileged user rather than root.
RUN useradd --create-home --uid 10001 appuser


# --- Test stage -------------------------------------------------------------
# Runs the suite entirely in a container — no Python on the host. Built only
# when explicitly targeted (`--target test`); the default build skips it.
FROM base AS test
RUN pip install ".[dev]"
COPY . .
USER appuser
ENTRYPOINT ["pytest"]
CMD ["-q"]


# --- Runtime stage (default) ------------------------------------------------
# FastMCP's default transport is stdio; this is what Claude Desktop speaks to.
# Must be run with `-i` (stdin open) and WITHOUT `-t` (no TTY) so the JSON-RPC
# stream isn't corrupted.
FROM base AS runtime
USER appuser
ENTRYPOINT ["nasa-mcp"]
