"""NASA Earthdata CMR Search and Harmony consumer APIs."""

from __future__ import annotations

import base64
import binascii
import json
import os
import re
from collections.abc import Callable
from datetime import date, datetime, time, timezone
from typing import Any, Literal, TypedDict
from urllib.parse import quote, unquote
from uuid import UUID

import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

CMR = "https://cmr.earthdata.nasa.gov"
HARMONY = "https://harmony.earthdata.nasa.gov"

# NASA serves datasets as files or signed links. Bound MCP tool responses even
# when an upstream sends a file inline or omits Content-Length.
_RESPONSE_LIMIT = 2_000_000
_BINARY_LIMIT = 96_000
_CMR_HEADER_NAMES = {
    "cmr-hits", "cmr-request-id", "cmr-search-after", "cmr-scroll-id", "cmr-timed-out",
    "cmr-shapefile-original-point-count", "cmr-shapefile-simplified-point-count",
}
_RESPONSE_HEADERS = _CMR_HEADER_NAMES | {
    "content-disposition", "content-length", "content-type", "etag", "link", "retry-after",
}
_CMR_ADMIN_PATHS = {"caches", "clear-cache", "reset"}
_HARMONY_USER_ROUTES = re.compile(
    r"/(?:capabilities|cloud-access(?:\.sh)?"
    r"|jobs(?:/[^/]+(?:/(?:steps|pause|resume|cancel|skip-preview))?)?"
    r"|labels|stac(?:/[^/]+(?:/[^/]+)?)?|staging-bucket-policy|versions"
    r"|service-results/.+|service-image-tag(?:/.+)?|docs(?:/.*)?|schemas/.*|workflow-ui"
    r"|(?:[^/]+/)?ogc-api-coverages(?:/.*)?|ogc-api-edr(?:/.*)?|[^/]+/wms)/?"
)

Value = str | int | float | bool
Parameters = dict[str, Value | list[Value]]
Method = Literal["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"]
BBox = tuple[float, float, float, float]
HTTPClient = Callable[[], httpx.AsyncClient]


class Upload(TypedDict):
    """A multipart file supplied by the caller."""

    field: str
    filename: str
    content_type: str
    base64_data: str


class RequestBody(TypedDict, total=False):
    """Choose JSON, text, or form fields with optional multipart files."""

    json_body: Any
    text: str
    content_type: str
    form: Parameters
    files: list[Upload]


def _path(path: str) -> str:
    """Accept relative API paths while keeping credentials on the fixed origin."""
    decoded = unquote(path)
    if (
        not path.startswith("/")
        or decoded.startswith("//")
        or any(char in decoded for char in "\\?#%")
        or any(ord(char) < 32 or ord(char) == 127 for char in decoded)
        or any(segment in {".", ".."} for segment in decoded.split("/"))
    ):
        raise ToolError("Use an API path starting with / and pass query parameters separately.")
    return decoded


def _body_kwargs(body: RequestBody | None, headers: dict[str, str]) -> dict[str, Any]:
    if not body:
        return {}
    form = body.get("form", {})
    uploads = body.get("files", [])
    if sum(("json_body" in body, "text" in body, bool(form or uploads))) > 1:
        raise ToolError("Choose one request body type: JSON, text, or form and files.")

    content_type = body.get("content_type")
    if uploads or content_type == "multipart/form-data":
        if "json_body" in body or "text" in body:
            raise ToolError("A multipart body uses form fields and files.")
        parts: list[tuple[str, Any]] = []
        for key, value in httpx.QueryParams(form).multi_items():
            parts.append((key, (None, value)))
        for upload in uploads:
            try:
                data = base64.b64decode(upload["base64_data"], validate=True)
            except (binascii.Error, ValueError):
                raise ToolError("Multipart file contents must use valid base64.") from None
            parts.append(
                (upload["field"], (upload["filename"], data, upload["content_type"]))
            )
        return {"files": parts}
    if content_type:
        headers["Content-Type"] = content_type
    if "json_body" in body:
        headers.setdefault("Content-Type", "application/json")
        return {"content": json.dumps(body["json_body"]).encode()}
    if "text" in body:
        headers.setdefault("Content-Type", "text/plain; charset=utf-8")
        return {"content": body["text"].encode()}
    return {"data": form}


def _redirect(response: httpx.Response, result: dict, token: str) -> dict:
    try:
        target = response.url.join(response.headers["location"])
    except httpx.InvalidURL:
        raise ToolError("NASA returned an invalid redirect.") from None
    if target.host == "urs.earthdata.nasa.gov":
        raise ToolError("Earthdata Login is required. Set or renew EARTHDATA_TOKEN on the server.")
    if target.scheme != "https" or target.username or target.password:
        raise ToolError("NASA returned an unexpected redirect.")
    location = str(target)
    result["location"] = location.replace(token, "***") if token else location
    if target.host == httpx.URL(HARMONY).host and target.port in {None, 443}:
        match = re.fullmatch(r"/jobs/([0-9a-fA-F-]+)", target.path)
        if match:
            result["data"] = {"jobID": match[1]}
    return result


def _download_url(response: httpx.Response, token: str) -> str | None:
    url = response.url
    if response.request.method != "GET" or not (
        url.path.rstrip("/").endswith("/wms") or url.path.startswith("/service-results/")
    ):
        return None
    if any(
        key.lower() in {"token", "access_token", "authorization", "api_key"}
        or key.lower().startswith("x-amz-") for key in url.params.keys()
    ):
        return None
    location = str(url)
    return None if token and (token in location or quote(token, safe="") in location) else location


def _http_error(status: int, detail: str, token: str) -> ToolError:
    if token:
        detail = detail.replace(token, "***")
    message = f"NASA Earthdata returned HTTP {status}. {detail.strip()}".rstrip()
    if status in {401, 403}:
        message += " Check EARTHDATA_TOKEN and your NASA collection permissions."
    return ToolError(message)


async def _response_data(response: httpx.Response, result: dict, token: str) -> dict:
    media_type = response.headers.get("content-type", "").partition(";")[0].lower()
    is_json = "json" in media_type
    is_text = media_type.startswith("text/") or "xml" in media_type
    limit = _RESPONSE_LIMIT if is_json or is_text else _BINARY_LIMIT
    if response.is_error:
        limit = 512

    buffer = bytearray()
    truncated = False
    async for chunk in response.aiter_bytes(chunk_size=16_384):
        remaining = limit - len(buffer)
        buffer.extend(chunk[:remaining])
        if len(chunk) > remaining:
            truncated = True
            break

    encoding = response.encoding or "utf-8"
    if response.is_error:
        raise _http_error(response.status_code, buffer.decode(encoding, errors="replace"), token)
    if truncated:
        result["truncated"] = True
        if download_url := _download_url(response, token):
            result["download_url"] = download_url
            result["message"] = "Open the download URL directly using your Earthdata Login."
        else:
            result["message"] = (
                "Response exceeds the MCP size limit. Use a smaller search page, "
                "or request asynchronous Harmony processing for download links."
            )
    elif buffer:
        if is_json:
            try:
                result["data"] = json.loads(buffer)
            except ValueError:
                raise ToolError("NASA returned an invalid JSON response.") from None
        elif is_text:
            result["text"] = buffer.decode(encoding, errors="replace")
        else:
            result["base64_data"] = base64.b64encode(buffer).decode("ascii")
    return result


async def _request(
    http: HTTPClient,
    origin: str,
    path: str,
    method: Method = "GET",
    query: Parameters | None = None,
    body: RequestBody | None = None,
    accept: str | None = None,
    pagination: dict[str, str] | None = None,
    requires_login: bool = False,
) -> dict:
    token = os.environ.get("EARTHDATA_TOKEN", "").strip()
    if requires_login and not token:
        raise ToolError("Set EARTHDATA_TOKEN on the server using an Earthdata Login bearer token.")
    headers = dict(pagination or {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if accept:
        headers["Accept"] = accept
    request_body = _body_kwargs(body, headers)

    # GET also starts jobs on Harmony. Never automatically retry or follow an
    # Earthdata request, since the initial operation may already have succeeded.
    try:
        async with http().stream(
            method, origin + path, params=query, headers=headers,
            follow_redirects=False, **request_body,
        ) as response:
            result = {
                "status_code": response.status_code,
                "headers": {
                    name: value for name, value in response.headers.items()
                    if name in _RESPONSE_HEADERS
                },
            }
            if response.has_redirect_location:
                return _redirect(response, result, token)
            return await _response_data(response, result, token)
    except httpx.HTTPError:
        raise ToolError(
            "Could not complete the Earthdata request. For a job submission, check Harmony's "
            "jobs list before trying again."
        ) from None


def _bbox(bbox: BBox) -> BBox:
    west, south, east, north = bbox
    if not (
        -180 <= west <= 180 and -180 <= east <= 180 and -90 <= south < north <= 90
        and west != east
    ):
        raise ToolError("Use a valid bounding box in west, south, east, north order.")
    return bbox


def _harmony_timestamp(value: str, end: bool = False) -> str:
    """Use UTC, treating a date as the start or end of its calendar day."""
    try:
        if len(value) == 10:
            day = date.fromisoformat(value)
            parsed = datetime.combine(day, time.max if end else time.min)
        else:
            parsed = datetime.fromisoformat(value)
    except ValueError:
        raise ToolError("Use YYYY-MM-DD or ISO 8601 timestamps for time filters.") from None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _harmony_subsets(bbox: BBox | None, start: str | None, end: str | None) -> list[str]:
    axes = []
    if bbox is not None:
        west, south, east, north = _bbox(bbox)
        axes.extend([f"lon({west}:{east})", f"lat({south}:{north})"])
    if start or end:
        lower = f'"{_harmony_timestamp(start)}"' if start else "*"
        upper = f'"{_harmony_timestamp(end, end=True)}"' if end else "*"
        if start and end and lower > upper:
            raise ToolError("The start time must be at or before the end time.")
        axes.append(f"time({lower}:{upper})")
    return axes


def _register_cmr(mcp: FastMCP, http: HTTPClient) -> None:

    @mcp.tool
    async def cmr_search_collections(
        keyword: str | None = None,
        short_name: str | None = None,
        version: str | None = None,
        provider: str | None = None,
        page_size: int = 20,
        search_after: str | None = None,
    ) -> dict:
        """Find Earthdata datasets. Use cmr-search-after in headers for the next page.

        Examples of LiDAR collection short names: GEDI02_A, ATL03 and ATL08.
        """
        if not 1 <= page_size <= 2000:
            raise ToolError("CMR page_size must be between 1 and 2000.")
        query = {
            "keyword": keyword, "short_name": short_name, "version": version,
            "provider": provider, "page_size": page_size,
        }
        return await _request(
            http, CMR, "/search/collections.umm_json",
            query={key: value for key, value in query.items() if value is not None},
            pagination={"CMR-Search-After": search_after} if search_after else None,
        )

    @mcp.tool
    async def cmr_search_granules(
        collection_id: str,
        bbox: BBox | None = None,
        temporal: str | None = None,
        page_size: int = 20,
        search_after: str | None = None,
    ) -> dict:
        """Find source files for a CMR collection concept ID.

        bbox is west, south, east, north in degrees. temporal is CMR's
        comma-separated ISO 8601 range. Reuse cmr-search-after from headers
        with the same filters to retrieve the next page.
        """
        if not 1 <= page_size <= 2000:
            raise ToolError("CMR page_size must be between 1 and 2000.")
        query: Parameters = {"collection_concept_id": collection_id, "page_size": page_size}
        if bbox is not None:
            query["bounding_box"] = ",".join(map(str, _bbox(bbox)))
        if temporal:
            query["temporal"] = temporal
        return await _request(
            http, CMR, "/search/granules.umm_json", query=query,
            pagination={"CMR-Search-After": search_after} if search_after else None,
        )

    @mcp.tool
    async def cmr_request(
        path: str,
        method: Method = "GET",
        query: Parameters | None = None,
        body: RequestBody | None = None,
        accept: str | None = None,
        search_after: str | None = None,
        scroll_id: str | None = None,
    ) -> dict:
        """Call a documented CMR Search endpoint under /search/.

        Supports concept and revision retrieval, advanced filters, facets,
        timeline, holdings, services, variables, tags, and associations.
        Use a list for repeated query/form fields; preserve CMR's exact field
        names, including brackets. Use body.json_body for JSON queries,
        body.text with a content type for AQL, or body.files for shapefiles.
        The optional server EARTHDATA_TOKEN enables authorized metadata access.
        """
        decoded = _path(path)
        route = decoded.rstrip("/").split("/")
        if (
            len(route) < 3 or route[1] != "search" or not route[2]
            or route[2].split(".")[0] in _CMR_ADMIN_PATHS
        ):
            raise ToolError("Use a CMR Search consumer API path under /search/.")
        pagination = {}
        if search_after:
            pagination["CMR-Search-After"] = search_after
        if scroll_id:
            pagination["CMR-Scroll-Id"] = scroll_id
        return await _request(http, CMR, path, method, query, body, accept, pagination)


def _register_harmony(mcp: FastMCP, http: HTTPClient) -> None:

    @mcp.tool
    async def harmony_capabilities(
        collection: str, version: Literal[1, 2, 3] = 3,
    ) -> dict:
        """Get allowed subsetting, transformations, variables and formats for a dataset.

        collection is a CMR collection concept ID or dataset short name.
        """
        key = "collectionId" if re.fullmatch(r"C[0-9]+-.+", collection) else "shortName"
        return await _request(
            http, HARMONY, "/capabilities", query={key: collection, "version": version},
            accept="application/json",
        )

    @mcp.tool
    async def harmony_submit_subset(
        collection_id: str,
        bbox: BBox | None = None,
        start: str | None = None,
        end: str | None = None,
        variables: list[str] | None = None,
        granule_id: str | None = None,
        output_format: str | None = None,
        max_results: int | None = None,
    ) -> dict:
        """Start an asynchronous Harmony subset and return its job ID.

        Use CMR's collection concept ID or short name. bbox is west, south,
        east, north. Dates are inclusive UTC dates or ISO 8601 timestamps.
        max_results limits input granules when set. Check harmony_capabilities
        first. For polygon uploads and advanced options, use harmony_request.
        """
        if not (bbox is not None or start or end or granule_id or max_results):
            raise ToolError("Specify a bounding box, time range, granule ID, or input limit.")
        if max_results is not None and max_results < 1:
            raise ToolError("max_results must be positive.")
        if not collection_id or "/" in collection_id:
            raise ToolError("Use a CMR collection concept ID or dataset short name.")
        axes = _harmony_subsets(bbox, start, end)
        query: Parameters = {"forceAsync": True}
        if axes:
            query["subset"] = axes
        if variables:
            query["variable"] = ",".join(variables)
        if granule_id:
            query["granuleId"] = granule_id
        if output_format:
            query["format"] = output_format
        if max_results is not None:
            query["maxResults"] = max_results
        variable_path = "parameter_vars" if variables else "all"
        path = (
            f"/{quote(collection_id, safe='')}/ogc-api-coverages/1.0.0/"
            f"collections/{variable_path}/coverage/rangeset"
        )
        _path(path)
        return await _request(http, HARMONY, path, query=query, requires_login=True)

    @mcp.tool
    async def harmony_job_status(job_id: str, page: int | None = None) -> dict:
        """Get a Harmony job's progress, status, and result links.

        Pass the job ID from submission. Paginate large result lists with page.
        """
        try:
            job_id = str(UUID(job_id))
        except ValueError:
            raise ToolError("Use the UUID returned by Harmony for the job ID.") from None
        return await _request(
            http, HARMONY, f"/jobs/{job_id}",
            query={"page": page} if page is not None else None,
            accept="application/json", requires_login=True,
        )

    @mcp.tool
    async def harmony_request(
        path: str,
        method: Method = "GET",
        query: Parameters | None = None,
        body: RequestBody | None = None,
        accept: str | None = None,
    ) -> dict:
        """Call Harmony's documented consumer APIs with their original options.

        Covers OGC Coverages, EDR, WMS, capabilities, jobs and controls,
        bulk status, steps, labels, STAC, and S3 staging. Use a list for
        repeated parameters and body.files with field=shapefile for uploads.
        Use forceAsync=true on transformation requests to get a job ID and
        staged result links. /cloud-access returns temporary S3 credentials
        to the caller. The server uses its configured Earthdata Login token.
        """
        decoded = _path(path)
        if (decoded != "/" and not _HARMONY_USER_ROUTES.fullmatch(decoded)) or (
            decoded.startswith(("/service-image-tag", "/service-results/"))
            and method not in {"GET", "HEAD"}
        ):
            raise ToolError("Use a documented Harmony consumer API path.")
        return await _request(http, HARMONY, path, method, query, body, accept)


def register_earthdata(mcp: FastMCP, http: HTTPClient) -> None:
    """Register Earthdata tools on the main NASA MCP server."""
    _register_cmr(mcp, http)
    _register_harmony(mcp, http)
