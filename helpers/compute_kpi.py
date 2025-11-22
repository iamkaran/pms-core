from typing import Dict, Any
import math
from services.logger import logger as log

def compute_job_actuals(telemetry: Dict[str, Any], attributes: Dict[str, Any]):
    '''Computes actuals and also sets baselines'''
    
    # <--Build Common Inputs-->
    
    updated_attributes: Dict[str, Any] = {}
    updated_telemetry: Dict[str, Any] = {}
    
    # Find the channel count (value of k in OCCURRENCE-1 --> OCCURRENCE-k)
    CHANNEL_COUNT = 0
    
    for key in telemetry:
        if "OCCURRENCE_" in key:
            CHANNEL_COUNT += 1
    log.debug(f"Channel count: {CHANNEL_COUNT}")
    
    # Read the current counters
    
    curProd: int = int(telemetry["PRODUCTION_COUNT"])
    curOcc: Dict[str, int] = {}
    curDur: Dict[str, float] = {}
    
    for i in range(1, CHANNEL_COUNT+1):
        curOcc[str(i)] = int(telemetry.get(f"OCCURRENCE_{i}") or 0)
        curDur[str(i)] = int(telemetry.get(f"DURATION_{i}") or 0)
    
    curOccTotal = sum(curOcc.values())
    curDurTotal = sum(curDur.values())
    
    # Time & Target
    
    ts_ms = telemetry["timestamp"] * 1000
    start_ms = attributes["cfg_start_ts"]
    shift_hours = attributes["cfg_shift_hours"]
    
    runtime_s = math.floor((ts_ms - start_ms) / 1000)
    shiftDur_s = shift_hours * 3600
    shiftTarget = attributes["cfg_target_qty_pcs"]
    
    if shiftDur_s > 0:
        percentElapsed = max(0.0, min(1.0, runtime_s / shiftDur_s))
        target_till_now_pcs = math.floor(shiftTarget * percentElapsed)
    else:
        percentElapsed = 0.0
        target_till_now_pcs = 0
    
    
    # <--Decide Mode--> 
    
    need_snapshot = None
    
    baseline_snapshot_ts = attributes.get("baseline_snapshot_ts")
    baseline_start_ts = attributes.get("baseline_start_ts")
    
    need_snapshot = (baseline_snapshot_ts is None or (baseline_start_ts is not None and baseline_start_ts != start_ms))
    
    
    # <--Snapshot Mode-->
    
    if need_snapshot:
        
        # <--ATTRIBUTES-->
        
        updated_attributes["baseline_snapshot_ts"] = ts_ms
        updated_attributes["baseline_start_ts"] = start_ms
        
        updated_attributes["baseline_prod_count_pcs"] = curProd
        
        updated_attributes["baseline_occ_total"] = curOccTotal
        updated_attributes["baseline_duration_s"] = curDurTotal
        updated_attributes["baseline_duration_ms"] = curDurTotal * 1000
        
        updated_attributes["job_status"] = "active"
        updated_attributes["job_status_ts"] = ts_ms
        
        # log.info(curOcc)
        for i in range(1, CHANNEL_COUNT+1): # Set the baseline counts
            updated_attributes[f"baseline_occ_{i}"] = curOcc[str(i)]
            updated_attributes[f"baseline_duration_s_{i}"] = curDur[str(i)]
            updated_attributes[f"baseline_duration_ms_{i}"] = curDur[str(i)] * 1000
        
        # <--TELEMETRY-->
        
        updated_telemetry["act_qty_pcs"] = 0
        updated_telemetry["act_occ_total"] = 0
        updated_telemetry["runtime_s"] = runtime_s
        updated_telemetry["downtime_s"] = 0
        updated_telemetry["uptime_s"] = runtime_s
        updated_telemetry["downtime_pct"] = 0
        updated_telemetry["target_till_now_pcs"] = target_till_now_pcs
        updated_telemetry["achieved_pct"] = 0
        updated_telemetry["active_status"] = telemetry["active_status"]
        
        
    # <--Normal Mode-->
    else:
        
        # <--ATTRIBUTES-->
        
        # Fetch the baselines
        updated_attributes["job_status"] = attributes.get("job_status", "unknown")
        baseOcc: Dict[str, Any] = {}
        baseDur: Dict[str, Any] = {}
        
        actOcc: Dict[str, Any] = {}
        actDur: Dict[str, Any] = {}
        
        baseProd = attributes.get("baseline_prod_count_pcs", 0)
        
        for i in range(1, CHANNEL_COUNT+1):
            baseOcc[str(i)] = attributes.get(f"baseline_occ_{i}", 0)
            baseDur[str(i)] = attributes.get(f"baseline_duration_s_{i}", 0)
        
        # Calculate the delta's
        log.debug(f"Prod total details:\n Current prod: {curProd}, Base prod: {baseProd}")
        prod_delta = max(0, curProd - baseProd)
        
        for i in range(1, CHANNEL_COUNT+1):
            actOcc[f"act_occ_{i}"] = max(0, curOcc[str(i)] - baseOcc[str(i)])
            actDur[f"act_duration_s_{i}"] = max(0, curDur[str(i)] - baseDur[str(i)])
        
        act_occ_total = sum(actOcc.values())
        downtime_s = sum(actDur.values())
        uptime_s = max(0, runtime_s - downtime_s)
        
        # Build the telemetry
        
        updated_telemetry["act_qty_pcs"] = prod_delta
        updated_telemetry["act_occ_total"] = act_occ_total
        updated_telemetry["runtime_s"] = runtime_s
        updated_telemetry["downtime_s"] = downtime_s
        updated_telemetry["uptime_s"] = uptime_s
        updated_telemetry["downtime_pct"] = (downtime_s / runtime_s * 100) if runtime_s > 0 else 0
        
        updated_telemetry.update(actOcc)
        updated_telemetry.update(actDur)
        
        updated_telemetry["target_till_now_pcs"] = target_till_now_pcs
        
        if target_till_now_pcs > 0:
            updated_telemetry["achieved_pct"] = round(prod_delta / target_till_now_pcs * 100, 2)
        else:
            updated_telemetry["achieved_pct"] = 0
        
        updated_telemetry["active_status"] = telemetry["active_status"]
        
        # <------------- ADD-ONS ------------->

        # 1. OEE Calculations

        bad_total_attr = max(0, attributes.get("bad_qty_pcs", 0))   # [pcs]
        good_total = max(0, prod_delta - bad_total_attr)            # [pcs]

        # Ideal cycle time [s/part] (default 60 s/part if not configured)
        ideal_cycle_time = float(attributes.get("ideal_cycle_time", 60))

        # --- raw ratios (0–1, unrounded) ---

        # QUALITY: 0–1
        if prod_delta > 0:
            quality_raw = good_total / prod_delta
        else:
            quality_raw = 0.0

        # AVAILABILITY: 0–1
        total_time_s = uptime_s + downtime_s          # [s]
        if total_time_s > 0:
            availability_raw = uptime_s / total_time_s
        else:
            availability_raw = 0.0

        # PERFORMANCE: 0–1 (can be >1 if ICT is wrong, so clamp later)
        if uptime_s > 0 and ideal_cycle_time > 0:
            performance_raw = (ideal_cycle_time * prod_delta) / uptime_s
        else:
            performance_raw = 0.0

        def clamp01(x: float) -> float:
            return max(0.0, min(1.0, x))

        availability_raw = clamp01(availability_raw)
        performance_raw  = clamp01(performance_raw)
        quality_raw      = clamp01(quality_raw)

        # OEE raw ratio 0–1
        oee_raw = availability_raw * performance_raw * quality_raw

        # ---- Convert to % with 2 decimals ----
        availability_pct = round(availability_raw * 100, 2)
        performance_pct  = round(performance_raw * 100, 2)
        quality_pct      = round(quality_raw * 100, 2)
        oee_pct          = round(oee_raw * 100, 2)
        
        # Performance rate (parts/hour)
        if prod_delta is None or uptime_s is None:
            parts_per_hour = 0
        elif prod_delta <= 0 or uptime_s <= 0:
            # bad or meaningless window, treat as 0 rate
            parts_per_hour = 0
        else:
            parts_per_hour = 3600 * prod_delta / uptime_s
        
        updated_attributes["parts_per_hour"] = parts_per_hour
        updated_telemetry["parts_per_hour"] = parts_per_hour

        # ---- Store attributes (percent values, ready for display) ----
        updated_attributes["ideal_cycle_time"] = ideal_cycle_time        # [s/part]

        updated_attributes["availability_pct"] = availability_pct        # %
        updated_attributes["performance_pct"]  = performance_pct         # %
        updated_attributes["quality_pct"]      = quality_pct             # %
        updated_attributes["oee_pct"]          = oee_pct                 # %

        # (optional: keep raw ratios too if you ever need them for math)
        updated_attributes["availability"] = availability_raw            # 0–1
        updated_attributes["performance"]  = performance_raw             # 0–1
        updated_attributes["quality"]      = quality_raw                 # 0–1
        updated_attributes["oee"]          = oee_raw                     # 0–1

        updated_attributes["bad_qty_pcs"] = bad_total_attr               # [pcs]

        # ---- Store telemetry (also as %) ----
        updated_telemetry["bad_qty_pcs"] = bad_total_attr                # [pcs]
        updated_telemetry["good_qty_pcs"] = good_total                   # [pcs]

        updated_telemetry["quality_pct"] = quality_pct
        updated_telemetry["availability_pct"] = availability_pct
        updated_telemetry["performance_pct"] = performance_pct
        updated_telemetry["oee_pct"] = oee_pct

        # <------------- ADD-ONS ------------->

        
        log.debug(f"Updated telemetry{updated_telemetry}")
        log.debug(f"{curOcc}")
    
    return updated_attributes, updated_telemetry