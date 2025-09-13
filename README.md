# 🔋 Berlin_Energy_Hackathon_MaxxWatt_Challenge

Use this repo to crack the MaxxWatt Berlin Energy Hackathon Challenge! You got this! 🔋💪

We provided some examplary code for data access and analysis for you. Use these as a starting point or develop your solution from scratch.

---

## 📚 Available Data

To support your solution, MaxxWatt provides a set of realistic mock datasets representing time-series data from:

- Multiple Battery Energy Storage Systems (BESS) with internal telemetry  
- A network of 6 smart meters capturing grid-side activity

Data is organized by asset and type, and includes physical signals (e.g. temperature, voltage), performance indicators (e.g. SOC, SOH), and environmental data. The files are in CSV format, with timestamps and sensor values.

Use this link for direct data access: http://maxxwatt-hackathon-datasets.s3-website.eu-central-1.amazonaws.com

---

## 📁 Directory Overview

BESS data/
├── ZHPESS232A230002/
│   └── <sensor_data>.csv
├── ZHPESS232A230003/
│   └── <sensor_data>.csv
├── ZHPESS232A230007/
│   └── <sensor_data>.csv
└── meter/
├── m1/
│   ├── com_ae.csv
│   ├── com_ap.csv
│   ├── neg_ae.csv
│   ├── pf.csv
│   └── pos_ae.csv
└── m2/ … m6/

---

## 🔋 BESS Folder (ZHPESS232A23000x)

Each BESS folder contains CSV files with time-series data from:

### 1) Battery Management System (BMS)

- `bms1_soc`, `bms1_soh`: State of Charge / Health — key performance indicators  
- `bms1_v`, `bms1_c`: Total pack voltage / current  
- `bms1_cell_ave_v`, `bms1_cell_ave_t`: Cell-level average voltage & temperature  
- `bms1_cell_max_v`, `bms1_cell_min_v`, `bms1_cell_t_diff`, etc.: Max/min cell values and spreads (health diagnostics)  
- `bms1_p1_v1 … bms1_p5_t52`: Per-pack cell voltages and temperatures for up to 5 packs × 52 cells

**✅ Use for:** SOC tracking, battery aging trends, safety diagnostics, cell balancing alerts

---

### 2) Power Conversion System (PCS)

- `pcs1_ap`: Apparent power output  
- `pcs1_dcc`, `pcs1_dcv`: DC current & voltage  
- `pcs1_ia`, `pcs1_ib`, `pcs1_ic`: AC phase currents  
- `pcs1_uab`, `pcs1_ubc`, `pcs1_uca`: AC line voltages  
- `pcs1_t_env`, `pcs1_t_a`, `pcs1_t_igbt`: Thermal monitoring of PCS and environment

**✅ Use for:** AC/DC conversion monitoring, inverter status, loss analysis, thermal envelope tracking

---

### 3) Auxiliary & Thermal Systems

- `ac1_outside_t`, `ac1_outwater_t`, `ac1_rtnwater_pre`: HVAC temperatures and pressures  
- `aux_m_ap`, `aux_m_pf`: Auxiliary power consumption & power factor

**✅ Use for:** Cooling system effectiveness, parasitic loads, energy overhead

---

### 4) Environmental & Safety Sensors

- `dh1_humi`, `dh1_temp`: Humidity and temperature sensors  
- `fa1_* … fa5_*`: Fire alarm CO levels, smoke flags, error codes

**✅ Use for:** Safety monitoring, alert systems, environment-linked degradation

---

## ⚡ Smart Meter Folder (meter/m1 … m6)

Each smart meter folder contains:

- `com_ae.csv`: Combined active energy  
- `com_ap.csv`: Combined active power  
- `neg_ae.csv`: Energy fed to grid (negative)  
- `pos_ae.csv`: Energy drawn from grid (positive)  
- `pf.csv`: Power factor

**✅ Use for:** Grid import/export monitoring, site balance, power quality analysis

---

## 🧠 BESS Software Stack & Data Integration

### 1) Software Architecture Layers

**Battery Management System (BMS)**  
Located at module/pack level.  
Collects real-time data: voltage, current, temperature per cell.  
Executes protection functions: over/under-voltage, thermal limits, balancing.

**Power Conversion System (PCS) Controller**  
Interfaces with inverter and grid.  
Receives dispatch commands and enforces ramp rates, voltage/frequency support.

**Energy Management System (EMS)**  
Site-level optimization: market participation, revenue stacking, SoC setpoints.  
Integrates forecasts (PV/wind, prices, load) with technical constraints.

**Supervisory Control and Data Acquisition (SCADA)**  
Monitors alarms, integrates with utility control centers.  
Provides operator interface, data historian, and cybersecurity controls.

---

### 2) Key Data from the BMS

- Cell voltages: Balance tracking, over/under-voltage detection.  
- Cell/pack temperatures: Thermal management and hotspot detection.  
- Current (charge/discharge): C-rate calculation, stress estimation.  
- Cumulative energy throughput: Basis for cycle aging models.

This cell-level data is streamed upward into EMS/SCADA for analysis and long-term decision making.

---

### 3) SoC (State of Charge) Estimation

- Coulomb counting: Integrating current over time, corrected with voltage checks.  
- Model-based estimation: Kalman filters or neural networks comparing measured vs modeled behavior.  
- **Why it matters:** Accurate SoC avoids overcharge/over-discharge, maximizes usable energy while protecting cells.

---

### 4) SoH (State of Health) Estimation

- Capacity fade measurement: Comparing usable Ah/Wh against rated values.  
- Internal resistance growth: Derived from voltage response during pulses.  
- Calendar vs cycle aging models: Separate contributions from time and use.  
- **Purpose:** Enables warranty compliance, informs augmentation planning.

---

### 5) Degradation Tracking

- **Calendar aging drivers:** Temperature, SoC window.  
- **Cycle aging drivers:** Depth of discharge (DoD), C-rate, temperature swings.  
- **Data-driven models:** Combine cell telemetry with empirical curves to forecast remaining useful life (RUL).  
- **Integration:** EMS uses degradation forecasts to adjust dispatch (e.g., avoiding high DoD if long-term warranty risk is high).

---

### 6) Anomaly Detection

- **Outlier detection:** Identify cells deviating in voltage, temperature, or resistance vs pack average.  
- **Pattern recognition:** Use ML models on time-series to flag early signs of cell failure.  
- **Event detection:** Rapid current/voltage spikes may indicate internal short, loose connection, or sensor fault.  
- **Action:** Trigger alarms, isolate modules, or initiate shutdown.

---

### 7) Integration Flow

1. Cell-level BMS data (ms resolution) →  
2. Pack/cluster BMS aggregation (real-time protection, balancing) →  
3. EMS optimization (dispatch, SoC window, warranty compliance) →  
4. SCADA/utility interface (grid services, operator oversight, long-term performance reports).

---

### ✅ Takeaway

The BESS software stack is hierarchical—BMS ensures safety at the cell level, EMS optimizes system-level dispatch, and SCADA provides supervisory control. By analyzing cell-level data, operators can estimate SoC, SoH, and degradation, while anomaly detection ensures reliability and prevents catastrophic failure.

---

## 🧱 BESS Fundamentals & System Architecture

### 1) Why BESS? The grid problem it solves

**Drivers of adoption**

- Variable renewable generation (solar PV, wind) creates a temporal mismatch between production and consumption. Sunlight peaks at noon, but demand often peaks in the evening. Wind patterns are equally variable.  
- As synchronous thermal and nuclear generators retire, the system loses conventional inertia (the stabilizing mass of spinning turbines) and primary reserves (the ability to inject power within seconds). This makes the grid more sensitive to disturbances and frequency deviations.  
- Transmission bottlenecks and interconnection delays increasingly lead to renewable curtailment. Storage allows energy to be shifted in both time and geography, relieving congestion and improving utilization.  
- Rapid electrification (EVs, heat pumps, industrial processes) adds new demand peaks and steeper ramps, increasing the value of flexible storage capacity.

**What BESS contributes**

- Energy shifting: store low-cost or excess generation and release during peak pricing or demand windows. Example: a 4-hour system enables arbitrage and capacity value.  
- Firming & shaping: reduce volatility of renewables, enabling them to meet schedules and power purchase agreements.  
- Ancillary services: fast frequency containment, automatic generation control participation, voltage regulation, and sometimes black start capability.  
- Capacity adequacy: provide firm capacity credit to system operators, reducing risk of load shedding.

`1`

- Congestion relief & non-wires alternatives: postpone expensive grid reinforcements by strategically placing storage at constrained substations.  
- Resilience and microgrids: support critical loads during outages, smooth islanded operation, and provide black start capability in hybrid systems.

---

### 2) Units and core performance metrics

- **Power (kW, MW):** instantaneous maximum charge/discharge rate. Defines how much the battery can deliver at any moment.  
- **Energy (kWh, MWh):** total storable energy. Duration = Energy ÷ Power. For instance, a 100 MW / 400 MWh system has 4 h of nominal discharge at rated power.  
- **C-rate:** normalized power. A 1C 100 kWh system charges/discharges at 100 kW; a 0.5C system takes 2 h to charge/discharge.  
- **Depth of Discharge (DoD):** the proportion of a battery’s capacity that has been discharged relative to its total usable capacity. For example, if a battery is drained from full (100% SoC) down to 20% SoC, then 80% of its capacity has been used, so the DoD is 80%. A higher DoD means the battery is being cycled more deeply, which usually accelerates wear and reduces lifetime. Most warranties specify maximum recommended DoD values to balance usable energy with long-term health.  
- **State of Charge (SoC):** inverse of DoD; fraction of energy currently stored.  
- **State of Health (SoH):** measure of degradation; ratio of current usable capacity to original nameplate capacity.  
- **Round-Trip Efficiency (RTE):** ratio of energy output to energy input across a full charge-discharge cycle, typically 85–94% at the system level.  
- **Response time:** how fast the system reaches a setpoint. Inverter response can be milliseconds; at plant level, delays depend on controls and communications.  
- **Availability:** share of time the system is capable of meeting contracted services.  
- **Degradation:** loss of performance from calendar aging (time, temperature, SoC) and cycling aging (frequency, depth, and speed of charge/discharge).

**Usable energy vs nameplate**  
Usable energy is typically less than nameplate due to limits such as SoC windows (e.g., 10–90%), temperature restrictions, voltage cutoffs, and reserved capacity for warranty conditions.

---

### 3) From cell to plant: components and control hierarchy

#### 3.1 Electrochemical stack

- **Cell:** the smallest electrochemical unit, consisting of an anode, cathode, separator, and electrolyte. Form factors include cylindrical, prismatic, and pouch designs.  
- **Module:** several cells wired in series/parallel with an internal monitoring board measuring voltages and temperatures.  
- **Rack/Tray:** a collection of modules with a rack BMS and protective contactors. Rack voltages usually reach 600–1500 VDC, high enough for efficient power conversion.  
- **String:** multiple racks in parallel or series to achieve the required energy and power rating for a subsystem.  
- **Container/Pod:** an enclosure (commonly 20/40-ft ISO containers) housing multiple strings, HVAC systems, fire detection and suppression, cabling, and safety infrastructure.

`2`

#### 3.2 Power path and conversion

- DC bus collects current from strings.  
- Bi-directional inverter (PCS) converts between DC and AC.  
- Medium-voltage transformer steps up voltage to grid level (10–35 kV).  
- Protection systems: fuses, breakers, relays, and surge arrestors ensure safe operation. Arc-flash and short-circuit studies are mandatory.  
- **Filters and harmonics:** LCL filters (inductor–capacitor–inductor filter circuits) are installed on the output of inverters to smooth the current waveform and reduce high-frequency switching noise. Without these, the rapid switching of power electronics introduces harmonics that can distort the grid waveform, cause overheating of equipment, and even trigger protective relays. Harmonic mitigation strategies—such as tuned filters, active harmonic compensation, and careful inverter design—are applied so the plant meets regional grid code limits on total harmonic distortion (THD). In practice this means the BESS injects power that is nearly sinusoidal and compatible with other grid assets, avoiding penalties and ensuring safe, stable operation.

#### 3.3 Control hierarchy

- Cell/Module BMS → Rack BMS → Battery Plant Controller (BPC) → Energy Management System (EMS)/SCADA → Grid interface (AGC, DSO/TSO, market signals).  
- **BMS:** ensures cell safety, balances voltages, calculates SoC/SoH, and controls contactors.  
- **BPC/EMS:** manages dispatch, optimizes schedules, maintains operational limits (thermal, SoC windows), and communicates with grid operators using standard protocols such as Modbus-TCP, IEC 60870-5-104, DNP3, and IEC 61850.

---

### 4) Main chemistries and implications

**Lithium-ion (market leader)**

- **LFP (LiFePO₄):** excellent thermal stability, robust safety margin, long cycle life, slightly lower energy density. Increasingly the default for stationary storage.  
- **NMC (LiNiMnCoO₂):** higher energy density, better suited for space-constrained or high-energy applications, but requires tighter thermal management and carries more fire risk.  
- **Operating envelope:** strings typically 600–1500 VDC, designed for ambient ranges −20 °C to 50 °C with active HVAC.

**Beyond Li-ion**

- **Sodium-ion:** cost-competitive, better cold-temperature performance, lower energy density; early commercialization phase.  
- **Flow batteries (e.g., vanadium redox):** decouple power and energy (electrolyte tank sizing defines capacity), excel at long duration (>6 h), nearly unlimited cycling with minimal degradation, but have lower round-trip efficiency (65–85%) and higher footprint.  
- **High-temperature batteries (NaS):** niche grid-scale deployments; require careful thermal management.  
- **Lead-acid and lead-carbon:** legacy technology, low cost but limited cycle life and depth of discharge.

**Key takeaway:** Chemistry determines system cost, performance profile, degradation behavior, safety requirements, and the range of grid services feasible.

---

### 5) Site architectures

#### 5.1 AC-coupled

[Battery Strings] → [PCS/Inverter] → [LV/MV Transformer] → [MV Switchgear] → Grid
↘ [SCADA/EMS]

**Pros:** Independent operation from co-located renewables, straightforward retrofits, simpler metering.  
This architecture is called AC-coupled because each asset (the BESS and the renewable plant) has its own dedicated inverter converting DC to AC before meeting at the AC bus.  
**Cons:** When paired with PV/wind, energy passes through two conversion steps, adding losses. It does not become DC-coupled simply by sharing an inverter; true DC-coupling requires both the PV array and the BESS to connect on the same DC bus ahead of a single hybrid PCS. In AC-coupled setups, even if both assets are colocated, they remain electrically separate until after AC conversion.

#### 5.2 DC-coupled PV-plus-storage

PV Array → DC Combiner → DC Bus ↘
[Hybrid PCS] → Transformer → Grid
Battery Strings → DC Bus ↗

**Pros:** Fewer conversion steps, can directly capture “clipped” PV energy, efficient hardware integration. In a true DC-coupled system, both the PV array and the BESS connect to the same shared DC bus before a single hybrid inverter. If the PV and BESS each maintain separate DC buses that only meet after individual conversion stages, then the architecture is not DC-coupled—it functions as AC-coupled or multi-bus even if they are collocated.  
**Cons:** Increased design complexity, shared inverter constraints, and more challenging interconnection compliance.

#### 5.3 Microgrids / Behind-the-Meter

Microgrids combine BESS with diesel gensets, PV, and local loads in either islanded or grid-connected operation.

**Key aspects:**

- Require microgrid controllers to orchestrate BESS, PV, diesel, and loads.  
- Enable smooth transitions between grid-connected and islanded states (seamless transfer).  
- Provide resilience for critical loads (hospitals, data centers, military bases).  
- Allow local optimization of renewables, fuel savings, and demand charge reduction.  
- BESS in microgrids often act as the grid-forming element, maintaining frequency and voltage when islanded.

---

#### 5.4 Hybrid / Multi-Bus Architectures

Some projects employ multi-bus or hybrid topologies that combine elements of AC- and DC-coupling.

**Examples:**

- Separate DC buses for PV and BESS feeding into coordinated PCS inverters.  
- AC-coupled BESS combined with DC-coupled PV in the same site, optimized by a site controller.  
- Hybrid PCS designs that can dynamically switch between grid-forming and grid-following modes.

**Pros:**

- Greater flexibility to adapt to site-specific requirements.  
- Can optimize for lowest CapEx or highest efficiency depending on priorities.  
- Supports mixed asset portfolios (legacy PV plus new storage).

**Cons:**

- More complex controls and integration.  
- Potentially higher interconnection study costs.  
- Requires careful SCADA/EMS design to avoid conflicts between controllers.


# Operations & Maintenance (O&M)

---

## 1) Introduction to O&M
Operations and Maintenance (O&M) is the **longest phase** of a BESS project, typically spanning **15–20 years**.  
Construction may last only 12–24 months, but O&M determines the project’s **long-term reliability, profitability, and compliance**.

Well-structured O&M ensures:
- High **availability** of the system, meeting contractual guarantees.  
- **Safety** for operators, stakeholders, and the community.  
- **Performance compliance** with warranties and service agreements.  
- **Regulatory adherence**, including cybersecurity and environmental standards.  

O&M covers:
- **Technical tasks**: monitoring, preventive servicing, augmentation.  
- **Organizational tasks**: training, workforce safety, spare parts logistics.  
- **Contractual tasks**: SLA compliance, reporting, audits.  

Poor O&M can **erode revenues, void warranties, and damage reputation**.

---

## 2) Maintenance Strategies

### 2.1 Preventive Maintenance
- **Definition:** Scheduled inspections/tests at fixed intervals.  
- **Tasks:** HVAC filter replacement, inverter cleaning, breaker testing, battery inspections, fire suppression checks.  
- **Pros:** Predictable, warranty-compliant, reduces surprise failures.  
- **Cons:** May replace still-functional parts, raising costs.  

---

### 2.2 Predictive Maintenance
- **Definition:** Uses sensors, analytics, and ML to **predict failures**.  
- **Examples:** Thermal modeling for HVAC, vibration monitoring of fans, impedance tracking of cells.  
- **Pros:** Cuts downtime, lowers costs, extends asset life.  
- **Cons:** Requires robust data + expertise; higher upfront cost.  
- **Trend:** Adoption of predictive analytics in **SCADA/EMS**, with **digital twins**.  

---

### 2.3 Corrective Maintenance
- **Definition:** **Unscheduled** repairs after alarms or failures.  
- **Examples:** PCS module replacement, battery rack swaps, fire sensor repairs.  
- **Impact:** Expensive, disruptive, requires downtime.  
- **Best practice:** Keep corrective maintenance minimal—focus on preventive/predictive.  

---

## 3) Monitoring and Control
SCADA + Remote Ops Centers are the **backbone of O&M**.

Functions:
- **Real-time monitoring:** SoC, SoH, voltage/current, temperatures, inverter status, HVAC, fire alarms.  
- **Alarm management:** Filter + prioritize to avoid “alarm fatigue.”  
- **Remote control:** Adjust setpoints, ramp rates, modes for market flexibility.  
- **Cybersecurity monitoring:** Detect intrusions, malware, unauthorized access.  
- **EMS integration:** Align dispatch optimization with technical limits.  
- **Data analytics:** Feed predictive models for anomaly detection & optimization.  

---

## 4) Degradation Management
Degradation is natural but can be managed:

- **Calendar aging:**  
  • Driven by high SoC + high temps.  
  • Mitigation: operate 20–80% SoC, optimize HVAC.  

- **Cycle aging:**  
  • Driven by deep DoD, high C-rates, high temp swings.  
  • Mitigation: avoid deep cycles, manage C-rates.  

- **Monitoring SoH:**  
  • BMS provides cell-level data (voltage, impedance, temperature).  
  • Diagnostics identify weak cells early.  

- **Augmentation planning:**  
  • Incremental: add modules every 3–5 years.  
  • Bulk: mid-life (~7–10 years), add significant capacity.  

- **End-of-life:**  
  • Recycling/disposal contracts with certified recyclers are **critical for ESG compliance**.  

---

## 5) KPIs and Reporting
KPIs align technical performance with **financial expectations**:

- **Availability (%):** Time plant is operational (≥97–99% required by lenders).  
- **Round-trip efficiency (RTE):** Ratio discharged/charged energy.  
- **Capacity retention:** Remaining usable energy vs beginning-of-life.  
- **Response time compliance:** Meeting fast frequency response (<250 ms).  
- **Safety incidents:** Frequency/severity of fire, arc flash, near misses.  
- **MTBF / MTTR:** Mean time between failures, mean time to repair.  
- **Revenue KPIs:** Arbitrage spreads, ancillary revenue, curtailment savings.  

**Reporting:** Regular reports to **owners, lenders, regulators, insurers** covering:  
- Technical KPIs  
- Financial summaries  
- Compliance audits  
- ESG reporting  

Transparency builds trust and improves financing terms.

---

## 6) Organizational and Contractual Models

- **Owner-operated:** Full control, requires in-house staff, higher OPEX.  
- **OEM-led LTSA:** OEM manages long-term service + warranties. Bankable for lenders.  
- **EPC-led O&M:** EPC continues as operator post-construction.  
- **3rd-party providers:** Independent specialists, cost-competitive.  
- **Hybrid models:** Owner manages strategy, OEM/EPC covers technical tasks.  

**Contracts include:**
- **Warranties:** Capacity, efficiency, availability guarantees.  
- **SLAs:** Response times (e.g., 4h onsite), uptime targets, penalties.  
- **Insurance:** Fire, cyber, business interruption, liability.  
- **Reporting obligations:** Regular reports for compliance.  

---

## 7) Common O&M Challenges

- **Supply chain delays:** 6–12 month lead times for key components.  
  → Mitigation: stock critical spares.  

- **Skilled workforce shortages:** Limited BESS-trained staff.  
  → Mitigation: OEM training, certification programs.  

- **Regulatory evolution:** Mid-life grid code/cyber changes.  
  → Mitigation: active monitoring, flexible design.  

- **Cybersecurity threats:** Remote assets = high-value targets.  
  → Mitigation: penetration tests, secure comms, patching.  

- **Degradation uncertainty:** Real-world > warranty assumptions.  
  → Mitigation: conservative SoC windows, augmentation reserves.  

- **Community relations:** Noise, safety concerns.  
  → Mitigation: sound barriers, drills with local responders.  

- **Cost pressures:** Drive to cut O&M budgets.  
  → Mitigation: balance savings with reliability.  

---

✅ **Summary:**  
Effective O&M blends **technical reliability, financial alignment, regulatory compliance, and stakeholder trust**. It’s the cornerstone of long-term success in BESS projects.


🚀 Good luck cracking the **MaxxWatt Challenge**!  
We’re excited to see your innovative solutions for the future of energy storage. ⚡
