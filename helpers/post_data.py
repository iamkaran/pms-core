import time
import httpx
from services.logger import logger as log
from modules.http_client import get_http_client
from dotenv import load_dotenv
import os

load_dotenv()

_client: httpx.AsyncClient | None = None

class TelemetrySendError(Exception):
    pass


async def post_telemetry(telemetry: dict, access_token: str) -> None:
    base_url = os.getenv("TB_URL")
    url = f"{base_url}/api/v1/{access_token}/telemetry"

    payload = {
        "ts": int(time.time() * 1000),
        "values": telemetry,
    }

    client = get_http_client()

    try:
        response = await client.post(url=url, json=payload)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        log.error(
            "ThingsBoard HTTP error %s: %s",
            e.response.status_code,
            e.response.text,
        )
        raise TelemetrySendError(
            f"Upstream returned {e.response.status_code}"
        ) from e
    except httpx.RequestError as e:
        log.error("Request error when sending telemetry: %s", e)
        raise TelemetrySendError("Unable to reach telemetry server") from e
