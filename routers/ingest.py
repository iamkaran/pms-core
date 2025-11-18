from fastapi import APIRouter, Body, HTTPException
import time
from services.logger import logger as log
from helpers.post_data import post_telemetry, TelemetrySendError
from helpers.get_related_asset import find_related_entity
from helpers.job_card_attr import get_jobcard_attrs
from helpers.job_status import get_job_status
from helpers.compute_kpi import compute_job_actuals
from helpers.send_jobcard_updates import send_jobcard_updates

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

    # Find related asset for jobcard logic
    asset_id = await find_related_entity(DEVICE_UUID)
    log.info(f"ACTIVE_JOB asset for {DEVICE_UUID}: {asset_id}")

    if asset_id is not None:
        # This block is "best effort": if it breaks, telemetry sending can still happen
        try:
            attr = await get_jobcard_attrs(asset_id=asset_id)
            log.debug("Retrieved Job card attributes")
            job_status = get_job_status(telemetry=telemetry, attribute=attr)

            log.info(f"Job Status: {job_status}")
            if job_status == "active":
                log.info("Job card is Active")
                updated_attributes, updated_telemetry = compute_job_actuals(
                    telemetry=telemetry,
                    attributes=attr,
                )
                await send_jobcard_updates(
                    asset_id=asset_id,
                    attrs=updated_attributes,
                    tel=updated_telemetry,
                )
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
