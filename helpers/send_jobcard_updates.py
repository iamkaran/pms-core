from modules.tb_http import tb_get, tb_post
import time
from services.logger import logger as log
import asyncio

async def send_jobcard_updates(asset_id: str, attrs: dict, tel: dict):
    '''Send the updated attributes and telemetry to Thingsboard'''
    
    # Attributes
    log.debug(f"attributes: {attrs}")
    log.debug(f"telemetry: {tel}")
    
    tasks = []

    if attrs:
        tasks.append(tb_post(
            path=f"/api/plugins/telemetry/ASSET/{asset_id}/SERVER_SCOPE",
            json_body=attrs
        ))
        
    if tel:
        ts_ms = int(tel.get("timestamp") or time.time() * 1000)
        
        values = {k: v for k, v in tel.items() if k != "timestamp_ms"} # to exclude the duplicate timestamp
        
        body = {
            "ts":ts_ms,
            "values":values
        }
        
        tasks.append(tb_post(
            path=f"/api/plugins/telemetry/ASSET/{asset_id}/timeseries/ANY_SCOPE",
            json_body=body
        ))

    if tasks:
        await asyncio.gather(*tasks)