#!/usr/bin/env python3
"""
timescaledb_thermal_checker.py

Simple threshold-based checker for thermal-runaway-like behavior on a TimescaleDB
time-series table with schema: (time, system_id, metric_name, value, unit, subsystem).

Configurable thresholds and rules are defined below.
"""

import os
import sys
from datetime import datetime
import numpy as np
import pandas as pd
import psycopg
from dotenv import load_dotenv

# -----------------------
# Load environment variables from .env
# -----------------------
load_dotenv()

DB_URI = os.getenv("DB_URI")
if DB_URI is None:
    user = os.getenv("TIMESCALEDB_USER")
    password = os.getenv("TIMESCALEDB_PASSWORD")
    host = os.getenv("TIMESCALEDB_HOST")
    port = os.getenv("TIMESCALEDB_PORT")
    dbname = os.getenv("TIMESCALEDB_DB")
    DB_URI = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

SYSTEM_ID = 1
WINDOW_START = datetime(2024, 1, 1)  # for historical testing
TABLE_NAME = "bess_metrics"

# Thresholds (tune to your system)
ABS_CELL_TEMP_C = 60.0
ABS_PACK_TEMP_C = 60.0
TEMP_RISE_PER_15MIN_C = 5.0
CONSECUTIVE_RISE_COUNT = 3
MAX_CELL_TEMP_DIFF_C = 10.0
PCS_IGBT_TEMP_C = 90.0
SMOKE_FLAG_VALUE = 1

# -----------------------
# Metrics to fetch (only those needed for thermal runaway detection)
# -----------------------
METRIC_NAMES = [
    # Cell and pack temperatures (core for thermal runaway)
    "cell_max_temperature", "cell_min_temperature", "cell_temp_diff", "cell_avg_temp",
    # Per-pack cell temperatures (all cells in all packs)
    *[f"pack{pack}_cell{cell}_temp" for pack in range(1, 6) for cell in range(1, 53)],
    # Pack-level temperature (if available)
    "temperature",
    # PCS IGBT temperature (for inverter thermal events)
    "temp_igbt",
    # Fire alarm smoke flags
    *[f"fire_alarm{i}_smoke_flag" for i in range(1, 6)],
    # CO/VOC sensors (for safety, optional)
    *[f"co_sensor{i}_level" for i in range(1, 6)],
    *[f"voc_sensor{i}_level" for i in range(1, 6)],
]

# -----------------------
# SQL fetch helper
# -----------------------
def fetch_timeseries(conn, system_id, metric_names, window_start):
    """
    Returns a pandas DataFrame with columns: time, metric_name, value
    for the specified system_id and metric_names within the lookback window.
    """
    window_clause = f"'{window_start.strftime('%Y-%m-%d %H:%M:%S')}'"
    metric_list_sql = ",".join([f"%s" for _ in metric_names])
    query = f"""
        SELECT time, system_id, metric_name, value
        FROM {TABLE_NAME}
        WHERE system_id = %s
          AND time >= {window_clause}
          AND metric_name IN ({metric_list_sql})
        ORDER BY time ASC
    """
    params = [system_id] + metric_names
    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["time", "system_id", "metric_name", "value"])
    return df

def fetch_timeseries_aggregated(conn, system_id, metric_names, window_start, bucket_minutes=5):
    """
    Fetches aggregated timeseries data using TimescaleDB's time_bucket and aggregate functions.
    Returns a DataFrame with columns: bucket, metric_name, max_value, min_value, avg_value
    """
    metric_list_sql = ",".join([f"%s" for _ in metric_names])
    query = f"""
        SELECT
            time_bucket('{bucket_minutes} minutes', time) AS bucket,
            metric_name,
            MAX(value) AS max_value,
            MIN(value) AS min_value,
            AVG(value) AS avg_value
        FROM {TABLE_NAME}
        WHERE system_id = %s
          AND time >= now() - interval '{window_start} minutes'
          AND metric_name IN ({metric_list_sql})
        GROUP BY bucket, metric_name
        ORDER BY bucket ASC
    """
    params = [system_id] + metric_names
    with conn.cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["bucket", "metric_name", "max_value", "min_value", "avg_value"])
    return df

# -----------------------
# Detection rules
# -----------------------
def detect_rules(df):
    """
    df: DataFrame with columns time, system_id, metric_name, value
    returns: list of alert dicts
    """
    alerts = []
    if df.empty:
        return alerts

    # pivot to wide: rows=timestamp, cols=metric_name -> values
    pivot = df.pivot_table(index='time', columns='metric_name', values='value', aggfunc='first')
    pivot = pivot.sort_index()

    # find all cell temp columns (pack{pack}_cell{cell}_temp)
    cell_temp_cols = [c for c in pivot.columns if c.startswith('pack') and c.endswith('_temp')]
    # also include any pack-level avg cell temperature
    if 'cell_avg_temp' in pivot.columns:
        pack_avg_col = 'cell_avg_temp'
    else:
        pack_avg_col = None

    # 1) Absolute cell temperature threshold
    if cell_temp_cols:
        latest = pivot.iloc[-1]
        hot_cells = []
        for col in cell_temp_cols:
            val = latest.get(col)
            if pd.notna(val) and float(val) >= ABS_CELL_TEMP_C:
                hot_cells.append((col, float(val)))
        if hot_cells:
            alerts.append({
                "rule": "absolute_cell_temp",
                "message": f"{len(hot_cells)} cell(s) >= {ABS_CELL_TEMP_C}°C",
                "items": hot_cells,
                "time": str(latest.name)
            })

    # 2) Absolute pack/avg temp
    if pack_avg_col and pd.notna(pivot[pack_avg_col].iloc[-1]):
        t = float(pivot[pack_avg_col].iloc[-1])
        if t >= ABS_PACK_TEMP_C:
            alerts.append({
                "rule": "absolute_pack_avg_temp",
                "message": f"pack average temperature >= {ABS_PACK_TEMP_C}°C",
                "value": t,
                "time": str(pivot.index[-1])
            })

    # 3) Rapid temperature rise (slope over 15 minutes)
    minutes_for_slope = 15
    samples_for_slope = max(1, minutes_for_slope // 5)  # at 5-min resolution
    if len(pivot) >= samples_for_slope + 1 and cell_temp_cols:
        recent = pivot.tail(samples_for_slope + 1)
        rise_cells = []
        for col in cell_temp_cols:
            arr = recent[col].dropna()
            if len(arr) >= 2:
                rise = float(arr.iloc[-1]) - float(arr.iloc[0])
                if rise >= TEMP_RISE_PER_15MIN_C:
                    rise_cells.append((col, rise))
        if rise_cells:
            alerts.append({
                "rule": "rapid_temp_rise",
                "message": f"{len(rise_cells)} cell(s) rose >= {TEMP_RISE_PER_15MIN_C}°C in {minutes_for_slope} minutes",
                "items": rise_cells,
                "time_start": str(recent.index[0]),
                "time_end": str(recent.index[-1])
            })

    # 5) Large temp spread across cells (pack imbalance)
    if cell_temp_cols:
        latest_row = pivot.iloc[-1][cell_temp_cols].dropna()
        if len(latest_row) >= 2:
            max_val = float(latest_row.max())
            min_val = float(latest_row.min())
            diff = max_val - min_val
            if diff >= MAX_CELL_TEMP_DIFF_C:
                hot = latest_row[latest_row >= (max_val - 0.1)].index.tolist()
                cold = latest_row[latest_row <= (min_val + 0.1)].index.tolist()
                alerts.append({
                    "rule": "cell_temp_spread",
                    "message": f"cell temp spread {diff:.2f}°C >= {MAX_CELL_TEMP_DIFF_C}°C",
                    "spread": diff,
                    "hot_cells": hot,
                    "cold_cells": cold,
                    "time": str(pivot.index[-1])
                })

    # 6) PCS IGBT high temp
    if 'temp_igbt' in pivot.columns and pd.notna(pivot['temp_igbt'].iloc[-1]):
        igbt_t = float(pivot['temp_igbt'].iloc[-1])
        if igbt_t >= PCS_IGBT_TEMP_C:
            alerts.append({
                "rule": "pcs_igbt_high",
                "message": f"PCS IGBT temp {igbt_t}°C >= {PCS_IGBT_TEMP_C}°C",
                "value": igbt_t,
                "time": str(pivot.index[-1])
            })

    # 7) Smoke flag / fire alarm indicators
    smoke_cols = [c for c in pivot.columns if c.endswith('smoke_flag') or 'smoke' in c.lower()]
    smoke_alerts = []
    for col in smoke_cols:
        v = pivot[col].iloc[-1]
        if pd.notna(v) and float(v) >= SMOKE_FLAG_VALUE:
            smoke_alerts.append((col, float(v)))
    if smoke_alerts:
        alerts.append({
            "rule": "smoke_flag",
            "message": "smoke flag(s) active",
            "items": smoke_alerts,
            "time": str(pivot.index[-1])
        })

    # 8) CO/VOC sensor spikes (optional)
    co_cols = [c for c in pivot.columns if c.endswith('_co') or 'co_sensor' in c]
    for col in co_cols:
        val = pivot[col].iloc[-1]
        if pd.notna(val) and float(val) > 50:  # example threshold, tune as needed
            alerts.append({
                "rule": "co_high",
                "message": f"CO sensor {col} high: {val}",
                "time": str(pivot.index[-1])
            })

    # 4) Gradient-based temperature rise detection using central difference and moving average
    if len(pivot) >= 3 and cell_temp_cols:
        grad_alerts = []
        time_seconds = (pivot.index[-1] - pivot.index[0]).total_seconds()
        dt = np.mean(np.diff(pivot.index.values).astype('timedelta64[s]').astype(float))  # average time step in seconds
        window_size = 3  # moving average window (number of samples)
        for col in cell_temp_cols:
            series = pivot[col].dropna()
            if len(series) < window_size + 2:
                continue
            # Central difference gradient
            values = series.values.astype(float)
            gradients = np.zeros_like(values)
            gradients[1:-1] = (values[2:] - values[:-2]) / (2 * dt)
            # Moving average of gradient
            ma_grad = pd.Series(gradients).rolling(window=window_size, center=True).mean()
            # Check if moving average gradient exceeds threshold (converted to degC per minute)
            threshold_grad = TEMP_RISE_PER_15MIN_C / (15 * 60)  # degC per second
            if np.any(ma_grad > threshold_grad):
                grad_alerts.append((col, float(ma_grad.max())))
        if grad_alerts:
            alerts.append({
                "rule": "gradient_temp_rise",
                "message": f"{len(grad_alerts)} cell(s) with moving average gradient above threshold",
                "items": grad_alerts,
                "time_end": str(pivot.index[-1])
            })

    return alerts

# -----------------------
# Main runner
# -----------------------
def main():
    try:
        conn = psycopg.connect(DB_URI)
    except Exception as e:
        print("ERROR: could not connect to DB:", e, file=sys.stderr)
        sys.exit(2)

    print(f"Fetching last {WINDOW_START} minutes for system_id={SYSTEM_ID} ...")
    df = fetch_timeseries(conn, SYSTEM_ID, METRIC_NAMES, WINDOW_START)
    if df.empty:
        print("No data found in the window. Exiting.")
        return

    alerts = detect_rules(df)
    if not alerts:
        print("No threshold alerts detected in the configured window.")
    else:
        print(f"Detected {len(alerts)} alert(s):")
        for a in alerts:
            print(" - RULE:", a.get("rule"))
            print("   MSG: ", a.get("message"))
            for k in ("time", "time_end", "time_start", "spread", "value", "items", "hot_cells", "cold_cells"):
                if k in a:
                    print(f"   {k}: {a[k]}")
            print()

    conn.close()
    return alerts

if __name__ == "__main__":
    main()