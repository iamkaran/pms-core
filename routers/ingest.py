from fastapi import APIRouter, Body, HTTPException
import time
from services.logger import logger as log
from helpers.post_data import post_telemetry, TelemetrySendError
from helpers.get_related_asset import find_related_entity
from helpers.job_card_attr import get_jobcard_attr
from helpers.job_status import get_job_status
from helpers.compute_kpi import compute_job_actuals
from helpers.send_jobcard_updates import send_jobcard_updates
from datetime import datetime

router = APIRouter()


@router.post("/api/telemetry/{ACCESS_TOKEN}/{DEVICE_UUID}")
async def ingest(ACCESS_TOKEN: str, DEVICE_UUID: str, telemetry = Body()) -> dict:
    """Main Process that handles every tick."""
    start = time.time()

    # Optional: grab machine name for logging
    if isinstance(telemetry, dict) and telemetry:
        machine_name = next(iter(telemetry.keys()), None)
        if machine_name:
            log.info(f"<------ Received Telemetry! for {machine_name} ------>")
            
    # Normalize the incoming data
    try:
        telemetry = flatten_dict(telemetry)
    except ValueError as e:
        log.error(f"Error flattening dictionary: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    
    readable = datetime.fromtimestamp(telemetry["timestamp"]).strftime("%b %d, %Y %I:%M:%S %p")
    log.info(f"Timestamp: {readable}")
    # Find related asset for jobcard logic
    asset_list = await find_related_entity(DEVICE_UUID)
    log.debug(f"Retrieved the following assets:\n{asset_list}")
    if asset_list:
        for asset_id in asset_list:
            if asset_id is not None:
                # This block is "best effort": if it breaks, telemetry sending can still happen
                try:
                    attr = await get_jobcard_attr(asset_id=asset_id)
                    prev_status = attr.get("job_status")
                    job_status = get_job_status(telemetry=telemetry, attribute=attr)
                    attr["job_status"] = job_status
                    log.debug(f"Retrieved Job card attributes: {attr}")

                    log.info(f"Job Status: {job_status}")
                    if job_status == "active":
                        log.info(f"ACTIVE_JOB asset for {DEVICE_UUID}: {asset_id}")
                        # attr is already fetched above
                        updated_attributes, updated_telemetry = compute_job_actuals(
                            telemetry=telemetry,
                            attributes=attr,
                        )
                        await send_jobcard_updates(
                            asset_id=asset_id,
                            attrs=updated_attributes,
                            tel=updated_telemetry,
                        )
                    elif job_status == "expired":
                        if prev_status != job_status:
                            await send_jobcard_updates(
                                asset_id=asset_id,
                                attrs={"job_status":job_status},
                                tel= None
                            )
                        else:
                            continue
                        
                except Exception:
                    # You can tighten this later with specific exceptions
                    log.exception("Jobcard processing failed for asset %s", asset_id)

    # Always send telemetry upstream
    log.info("Posting Telemetry...")
    try:
        await post_telemetry(telemetry=telemetry, access_token=ACCESS_TOKEN)
        log.info("<------ Telemetry sent successfully ------>")
    except TelemetrySendError as e:
        log.error("Telemetry sending failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))

    elapsed = round(time.time() - start, 2)
    log.info(f"elapsed time: {elapsed}s")

    return {"success": True}

def flatten_dict(data):
    if not isinstance(data, dict) or not data:
        raise ValueError("Input must be a non-empty dictionary")
    
    flat_data = data[next(iter(data))]

    if not isinstance(flat_data, list):
        raise ValueError("Dictionary value must be a list")
    
    new_data = {}
    for obj in flat_data:
        if not isinstance(obj, dict) or not obj:
            continue
        key, value = next(iter(obj.items()))
        new_data[key] = value
    
    return new_data
