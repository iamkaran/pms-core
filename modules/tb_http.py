from typing import Any, Dict, Optional, Union
import os

from pydantic import BaseModel

from modules.get_jwt_token import get_tb_jwt
from modules.http_client import get_http_client
from services.logger import logger as log

TB_BASE_URL = os.getenv("TB_URL")
if not TB_BASE_URL:
    raise RuntimeError("TB_URL not configured")
TB_BASE_URL = TB_BASE_URL.rstrip("/")


async def tb_request(
    method: str,
    path: str,
    *,
    json_body: Optional[Union[BaseModel, Dict[str, Any]]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Any:
    
    client = get_http_client()
    token = await get_tb_jwt()
    
    headers = {
        "X-Authorization":f"Bearer {token}"
    }
    
    has_body = json_body is not None
    if has_body:
        headers["Content-type"] = "application/json"
    
    if isinstance(json_body, BaseModel):
        payload: Any = json_body.model_dump(by_alias=True, exclude_none=True)
    else:
        payload = json_body 
    
    url = TB_BASE_URL + path
    
    resp = await client.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=payload if has_body else None
    )

    resp.raise_for_status()
    
    if not resp.content:
        return None
    return resp.json()

async def tb_get(
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None
) -> Any:
    return await tb_request(method="GET", path=path, params=params)

async def tb_post(
    path:str,
    *,
    json_body: Optional[Union[BaseModel, Dict[str, Any]]] = None,
    params: Optional[Dict[str, Any]] = None   
) -> Any:
    return await tb_request(method="POST", path=path, params=params, json_body=json_body)

