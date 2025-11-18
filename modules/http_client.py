import httpx
from typing import Optional

_client: Optional[httpx.AsyncClient] = None

def get_http_client() -> httpx.AsyncClient:
    """Get or create a shared HTTPX AsyncClient."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=5.0)
    return _client