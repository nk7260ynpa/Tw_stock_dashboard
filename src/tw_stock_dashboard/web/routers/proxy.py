"""反向代理路由。

將 `/app/<service>/*` 的請求轉發到 db_network 內部容器，
讓瀏覽器能透過 Dashboard（唯一對外 port 8002）存取所有子服務。
"""

import logging
from urllib.parse import urlsplit, urlunsplit

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import Response, StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["proxy"])

# 服務 ID → 容器內部 host:port（透過 db_network DNS 解析）
SERVICE_MAP: dict[str, str] = {
    "hot": "tw_stock_hot:5050",
    "news": "tw_stock_news:8003",
    "tools": "tw_stock_tools:8000",
    "webpage": "tw-stock-webpage:8000",
    "specialinfo": "tw-stock-specialinfo:5055",
    "db-operating": "tw_stock_db_operating:8080",
    "ml": "tw-stock-ml:5002",
    "indicator": "tw-stock-indicator:5001",
}

# Hop-by-hop headers（HTTP/1.1 RFC 2616 Section 13.5.1）不可轉發
HOP_BY_HOP_HEADERS: set[str] = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    # 壓縮相關：由 httpx 自動解壓，不可原樣轉發
    "content-encoding",
    "content-length",
}

# 共享 AsyncClient，啟動時建立、shutdown 時關閉
_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    """取得共享 httpx.AsyncClient。

    Returns:
        共享的非同步 HTTP client。
    """
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            follow_redirects=False,
        )
    return _client


async def close_client() -> None:
    """關閉共享 client（於 FastAPI shutdown 時呼叫）。"""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _filter_request_headers(headers: dict[str, str], target_host: str) -> dict[str, str]:
    """過濾並改寫轉發到目標服務的 request headers。

    Args:
        headers: 原始 request headers。
        target_host: 目標 host:port。

    Returns:
        過濾後的 headers。
    """
    forwarded: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() in HOP_BY_HOP_HEADERS:
            continue
        if key.lower() == "host":
            continue
        forwarded[key] = value
    forwarded["host"] = target_host
    return forwarded


def _rewrite_location(location: str, service: str, target_host: str) -> str:
    """改寫 3xx redirect 的 Location header，加回 `/app/<service>` 前綴。

    Args:
        location: 原始 Location 值。
        service: 服務 ID。
        target_host: 目標 host:port（用於判斷絕對 URL 是否指向同一服務）。

    Returns:
        改寫後的 Location。
    """
    prefix = f"/app/{service}"
    # 相對路徑（以 / 開頭）
    if location.startswith("/"):
        return f"{prefix}{location}"
    # 絕對 URL：若 host 指向同一目標則改寫，否則原樣回傳
    try:
        parts = urlsplit(location)
    except ValueError:
        return location
    if parts.scheme in ("http", "https") and parts.netloc == target_host:
        new_path = f"{prefix}{parts.path or '/'}"
        return urlunsplit(("", "", new_path, parts.query, parts.fragment))
    return location


def _filter_response_headers(
    headers: httpx.Headers, service: str, target_host: str
) -> dict[str, str]:
    """過濾並改寫回傳給瀏覽器的 response headers。

    Args:
        headers: 目標服務的原始 response headers。
        service: 服務 ID。
        target_host: 目標 host:port。

    Returns:
        過濾並改寫後的 headers。
    """
    filtered: dict[str, str] = {}
    for key, value in headers.items():
        lower = key.lower()
        if lower in HOP_BY_HOP_HEADERS:
            continue
        if lower == "location":
            filtered[key] = _rewrite_location(value, service, target_host)
            continue
        filtered[key] = value
    return filtered


@router.api_route(
    "/app/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
@router.api_route(
    "/app/{service}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def proxy(service: str, request: Request, path: str = "") -> Response:
    """將 `/app/<service>/<path>` 轉發至對應的內部容器。

    Args:
        service: 服務 ID，必須在 SERVICE_MAP 中。
        request: FastAPI Request 物件。
        path: 剝除前綴後的剩餘路徑。

    Returns:
        目標服務的 StreamingResponse。
    """
    target_host = SERVICE_MAP.get(service)
    if target_host is None:
        return Response(content=f"未知服務: {service}", status_code=404)

    # 組裝目標 URL（保留 query string）
    query = request.url.query
    normalized_path = path if path else ""
    target_url = f"http://{target_host}/{normalized_path}"
    if query:
        target_url = f"{target_url}?{query}"

    # 準備 request
    forwarded_headers = _filter_request_headers(dict(request.headers), target_host)
    body = await request.body()

    client = get_client()
    req = client.build_request(
        method=request.method,
        url=target_url,
        headers=forwarded_headers,
        content=body if body else None,
    )

    try:
        upstream = await client.send(req, stream=True)
    except httpx.ConnectError as exc:
        logger.warning("proxy connect error: %s -> %s: %s", service, target_url, exc)
        return Response(
            content=f"無法連線至 {service}（{target_host}）：{exc}",
            status_code=502,
        )
    except httpx.RequestError as exc:
        logger.warning("proxy request error: %s -> %s: %s", service, target_url, exc)
        return Response(content=f"代理錯誤：{exc}", status_code=502)

    response_headers = _filter_response_headers(upstream.headers, service, target_host)

    async def _stream_body():
        try:
            async for chunk in upstream.aiter_raw():
                yield chunk
        finally:
            await upstream.aclose()

    return StreamingResponse(
        _stream_body(),
        status_code=upstream.status_code,
        headers=response_headers,
    )
