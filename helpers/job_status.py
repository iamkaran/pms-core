import math
from typing import Any, Mapping
from services.logger import logger as log
from models.tb_legacy_models import JobStatus

def _to_num(x: Any, default: float) -> float:
    '''Normalizes the number input'''
    try:
        num = float(x)
    except (TypeError, ValueError) as e:
        log.error(f"Error converting value: {e}")
        return default
    return num if math.isfinite(num) else default

def _to_millis(ts: Any) -> float:
    '''Returns a timestamp in milliseconds'''
    n = _to_num(ts, 0.0)
    
    if n < 1_000_000_000_000:
        return n * 1000.0
    else:
        return n

def get_job_status(
    telemetry: Mapping[str, Any],
    attribute: Mapping[str, Any]
) -> str:
    '''Computes the job status based on its place in the timeline'''
    job_status = JobStatus.UNKNOWN
    ts_millis = _to_millis(telemetry.get("timestamp"))
    cfg_start_ts = _to_num(attribute.get("cfg_start_ts"), float("nan"))
    cfg_shift_hours = _to_num(attribute.get("cfg_shift_hours"), float("nan"))
    
    # Return unknown if bad value
    if not (
        math.isfinite(ts_millis) and
        math.isfinite(cfg_start_ts) and
        math.isfinite(cfg_shift_hours)
    ): return job_status
    
    start_ms = cfg_start_ts
    shift_ms = max(0.0, cfg_shift_hours * 3600000.0)
    end_ms = start_ms + shift_ms
    log.debug(f"ts: {ts_millis}, start: {start_ms}, end: {end_ms}")
    if ts_millis < start_ms:
        job_status = JobStatus.PLANNED
    elif ts_millis <= end_ms and ts_millis >= start_ms:
        job_status = JobStatus.ACTIVE
    else:
        job_status = JobStatus.EXPIRED
    
    return str(job_status.value)
