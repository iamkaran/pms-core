import os
import time
from typing import Optional
import jwt
from dotenv import load_dotenv
from services.logger import logger as log
from modules.http_client import get_http_client

load_dotenv()

# Important Environment variables
TB_BASE_URL = os.getenv("TB_URL")
TB_USERNAME = os.getenv("TB_USERNAME")
TB_PASSWORD = os.getenv("TB_PASSWORD")
TB_JWT_SAFETY_DELAY = int(os.getenv("TB_JWT_SAFETY_DELAY") or 30) # Ex: 30 seconds 

# Cached variables
__jwt_token: Optional[str] = None
__expires_at: Optional[float] = None
_refresh_token: Optional[str] = None

async def _login_and_get_tokens():
    '''Fetches a new JWT token and updates the cached ones'''
    global __jwt_token, __expires_at, _refresh_token
    
    # Check if the environment variables exist
    if not TB_BASE_URL or not TB_PASSWORD or not TB_USERNAME:
        raise RuntimeError
    
    jwt_url = f"{TB_BASE_URL}/api/auth/login"
    
    json_body = {
        "username":TB_USERNAME,
        "password":TB_PASSWORD
    }
    
    client = get_http_client()
    
    resp = await client.post(url=jwt_url, json=json_body)
    resp.raise_for_status()
    output = resp.json()
    
    # Update the variables
    __jwt_token = output["token"]
    _refresh_token = output["refreshToken"]
    
    # Get the expiry timestamp
    decoded = jwt.decode(output["token"], options={"verify_signature":False})
    __expires_at = float(decoded["exp"])

async def get_tb_jwt():
    '''Checks if there is a cached token that can be used otherwise just fetch a new one'''
    global __jwt_token, __expires_at, _refresh_token
    
    now = time.time()
    if __jwt_token and now < __expires_at - TB_JWT_SAFETY_DELAY:
        # log.info("reused")
        return __jwt_token
    else:
        await _login_and_get_tokens()
        return __jwt_token
    