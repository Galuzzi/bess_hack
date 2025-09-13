
# BESS Predictive Maintenance – Team Reference

This document summarizes the **components, risks, variables, and maintenance concepts** for the hackathon project.  
Use this as a quick reference when building prediction models or the dashboard.

---

## 📦 Main Components
- **Battery + BMS** – Cells, strings, packs. State-of-Charge (SoC), State-of-Health (SoH), cell balancing, limits.  
- **Power Conversion System (PCS)** – DC↔AC conversion, IGBT modules, capacitors, harmonic filters.  
- **Thermal / HVAC** – Pumps, fans, liquid cooling loops, compressors, heat exchangers.  
- **Safety Systems** – Fire/CO/VOC sensors, smoke detectors, suppression system.  
- **Auxiliary + Grid Interface** – Auxiliary loads, relays, site smart meters.  

---

## ⚠️ Failure & Degradation Modes
- **Cells** – Capacity fade, resistance rise, voltage imbalance → overheating, thermal runaway risk.  
- **Inverter/PCS** – Capacitor aging, IGBT overheating, AC imbalance, efficiency loss, derating.  
- **HVAC / Cooling** – Coolant leaks, blocked airflow, fan/compressor degradation → rising pack/module temps.  
- **Safety/Protection** – Faulty sensors, inactive suppression, recurring alarms.  
- **System-Level** – Firmware drift, protection relay mis-ops, poor maintenance.  

---

## 📊 Dataset Overview

**Dataset root:**  
<http://maxxwatt-hackathon-datasets.s3-website.eu-central-1.amazonaws.com>

**BESS Assets:**  
- `ZHPESS232A230002`, `ZHPESS232A230003`, `ZHPESS232A230007`

**Smart Meters:**  
- `meter/m1 … m6`

### Variables by Subsystem

- **Battery / BMS**  
  - `bms1_soc`, `bms1_soh`, `bms1_v`, `bms1_c`  
  - `bms1_cell_ave_v`, `bms1_cell_ave_t`, `bms1_cell_max_v`, `bms1_cell_min_v`  
  - `bms1_cell_max_t`, `bms1_cell_min_t`, `bms1_cell_v_diff`, `bms1_cell_t_diff`  
  - Pack/Cell detail: `bms1_p1_v1 … bms1_p5_v52`, `bms1_p1_t1 … bms1_p5_t52`  
  - `bms1_pos_ins`  

- **PCS / Inverter**  
  - `pcs1_ap`, `pcs1_dcc`, `pcs1_dcv`  
  - `pcs1_ia`, `pcs1_ib`, `pcs1_ic`  
  - `pcs1_uab`, `pcs1_ubc`, `pcs1_uca`  
  - `pcs1_t_env`, `pcs1_t_a`, `pcs1_t_igbt`  

- **Thermal / Aux Systems**  
  - `ac1_outside_t`, `ac1_outwater_t`, `ac1_rtnwater_t`  
  - `ac1_outwater_pre`, `ac1_rtnwater_pre`  
  - `aux_m_ap`, `aux_m_pf`, `aux_m_i`, `aux_m_pos_ae`, `aux_m_neg_ae`, `aux_m_com_ae`  

- **Environmental & Safety**  
  - `dh1_temp`, `dh1_humi`  
  - `fa1 … fa5`: `Co`, `Voc`, `SmokeFlag`, `ErrCode`, `T1`, `T2`, `Level`  

- **Smart Meters**  
  - `com_ap`, `com_ae`, `pos_ae`, `neg_ae`, `pf` (m1…m6)  

---

## 🔗 Risk ↔ Metrics Mapping

| **Risk / Failure** | **Primary Indicators** | **Key Variables** |
|---------------------|------------------------|-------------------|
| Fire / Thermal runaway | High cell temps, large ΔT across cells, voltage anomalies | `bms1_cell_max_t`, `bms1_cell_min_t`, `bms1_cell_t_diff`, `bms1_cell_max_v`, `bms1_cell_min_v`, `bms1_v`, `bms1_c`, `dh1_temp`, HVAC temps |
| Inverter / Power Electronics | Efficiency drop, IGBT overtemp, AC imbalance, derating | `pcs1_ap`, `pcs1_dcc`, `pcs1_dcv`, `pcs1_ia/b/c`, `pcs1_uab/bc/ca`, `pcs1_t_igbt`, `pcs1_t_env`, `aux_m_ap`, `aux_m_pf` |
| Cell Degradation / BMS | SoH decline, voltage spread ↑, balancing activity | `bms1_soh`, `bms1_soc`, `bms1_cell_ave_v`, `bms1_cell_v_diff`, `bms1_cell_max_v`, `bms1_cell_min_v`, `bms1_cell_t_diff` |
| HVAC / Cooling Failure | Abnormal ΔT, pressure anomalies, aux power spikes | `ac1_outwater_pre`, `ac1_rtnwater_pre`, `ac1_outwater_t`, `ac1_rtnwater_t`, `aux_m_ap`, `dh1_humi` |
| Fire Suppression Fault | Bad sensor readouts, error codes | `fa1–fa5` signals |
| Protection Failures | Protection not clearing, insulation anomalies | `bms1_pos_ins`, `fa*_ErrCode` |
| Performance Decline | Round-trip efficiency ↓, ramp delay | `pcs1_ap`, `pcs1_dcc`, `pcs1_dcv`, meters (`com_ae`, `pos_ae`, `neg_ae`, `pf`), `bms1_soc` |

---

## 🛠️ Heuristic Rules (Seed for Models)

- Thermal anomaly: if `bms1_cell_t_diff > 10°C` for >15min → raise risk(Thermal).  
- Voltage imbalance: if `bms1_cell_v_diff > 50mV` over 3 cycles → risk(Degradation).  
- Inverter efficiency: η = AC power / (DCV × DCC). Drop >2% in 7 days → risk(PowerElectronics).  
- HVAC stress: if `(rtnwater_t - outwater_t) > 8°C` or `aux_m_ap` z-score >2 → risk(HVAC).  
- RTE trend: energy-out/energy-in (meters). Decline >5% vs 30-day baseline → risk(Performance).  
- Alarm hygiene: rising count of `fa*_ErrCode` or BMS/PCS warnings → risk(Safety/Protection).  

---

## 📅 Maintenance Documentation Feature

- **Calendar of tasks:**  
  - Monthly: status checks, cleaning filters.  
  - Quarterly: tighten connections, fire suppression tests.  
  - Annual: capacity test, firmware updates, thermography.  

- **Integration with metrics:**  
  - Overdue filter cleaning → HVAC temps & aux power drift.  
  - Skipped capacity test → uncertainty in SoH trend.  

- **Visualization:**  
  - Gantt-style due/overdue bars.  
  - Risk heatmap vs days-overdue.  
  - "What-if" slider to simulate delayed maintenance.  

---

## 🚀 Extra Sensors (Future Potential)
- Acoustics / vibration (fan, compressor, transformer hum).  
- Impedance / ESR online tests for cell aging.  
- Coolant level & flow sensors.  
- Firmware/config logs.  
- Infrared imagery hooks (hotspots).  

---

