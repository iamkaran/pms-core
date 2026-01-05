# modules/jobcard_attrs.py
from typing import Any, Dict, List, Optional

from services.logger import logger as log
from modules.tb_http import tb_get

JOB_ATTR_KEYS: List[str] = [
    # config
    "cfg_start_ts",
    "cfg_target_qty_pcs",
    "cfg_shift_hours",

    # baseline top-level
    "baseline_snapshot_ts",
    "baseline_start_ts",
    "baseline_prod_count_pcs",
    "baseline_occ_total",
    "baseline_duration_ms",
    "baseline_bad_qty_pcs",
    "baseline_machine_bad_prod_count_pcs",
    "baseline_user_bad_prod_count_pcs",
]

# baseline per-channel (1..10)
for i in range(1, 11):
    JOB_ATTR_KEYS.append(f"baseline_occ_{i}")
    JOB_ATTR_KEYS.append(f"baseline_duration_s_{i}")

# status / labels / events
JOB_ATTR_KEYS.extend(
    [
        "job_status",
        "prev_status_code",
        "prev_status_label",
        "status_changed_ts",
        "last_alert_event_id",
        "active_status_cur",
        "status_code_cur",
        "status_label",
        "bad_qty_pcs",
        
        "user_bad_prod_count_pcs",
        "machine_bad_prod_count_pcs",
        "bad_production_switch"
    ]
)

async def get_jobcard_attr(asset_id: str) -> Any:
    """
    Raw TB response for server-scope attributes of this asset,
    restricted to JOB_ATTR_KEYS.
    """
    params = {"keys": ",".join(JOB_ATTR_KEYS)}
    raw = await tb_get(
        f"/api/plugins/telemetry/ASSET/{asset_id}/values/attributes/SERVER_SCOPE",
        params=params,
    )
    # log.debug(f"Raw attrs for asset {asset_id}: {raw}")
    return normalize_tb_attributes(raw=raw)

def normalize_tb_attributes(raw: Any) -> Dict[str, Any]:
    '''Normalize the output of the attributes fetch'''
    
    result: Dict[str, Any] = {}
    
    for attr in raw:
        key = attr["key"]
        value = attr["value"]
        result[key] = value
    
    # log.debug(f"Normalized attributes: {result}")
    return result
