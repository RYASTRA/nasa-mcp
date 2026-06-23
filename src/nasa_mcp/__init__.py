"""nasa-mcp: a unified MCP server for NASA's public APIs."""

from importlib.metadata import PackageNotFoundError, version

from nasa_mcp.server import main, mcp

try:
    __version__ = version("nasa-mcp")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0+dev"

__all__ = ["main", "mcp", "__version__"]
