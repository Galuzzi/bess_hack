import pandas as pd
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain


# Standort Prüm
location = Location(50.2089, 6.4227, 'Europe/Berlin')

# TMY-Daten einlesen
tmy_data = pd.read_csv('tmy_50.209_6.423_2005_2023.csv', skiprows=17, nrows=8760)
#tmy_data = pd.read_csv('tmy_50.209_6.423_2005_2023.csv', skiprows=17, nrows=3623)
tmy_data['time'] = pd.to_datetime(tmy_data['time(UTC)'], format="%Y%m%d:%H%M")
tmy_data.set_index('time', inplace=True)

# Wetterdaten vorbereiten
weather = pd.DataFrame({
    'ghi': tmy_data['G(h)'],
    'dni': tmy_data['Gb(n)'],
    'dhi': tmy_data['Gd(h)'],
    'temp_air': tmy_data['T2m'],
    'wind_speed': tmy_data['WS10m']
}, index=tmy_data.index)
weather.index = weather.index.tz_localize('UTC').tz_convert('Europe/Berlin')

# Zeitachse auf 2022 setzen
weather.index = pd.date_range('2022-01-01 00:00', '2022-12-31 23:00', freq='H', tz='Europe/Berlin')
#weather.index = pd.date_range('2022-01-01 00:00', '2022-05-31 23:00', freq='H', tz='Europe/Berlin')


# Alle Modulflächen mit Neigung, Azimut, Fläche
flächen = [
    {"tilt": 10, "azimuth": 210, "area": 506.4},
    {"tilt": 10, "azimuth": 30, "area": 514.4},
    {"tilt": 6,  "azimuth": 211, "area": 59.6},
    {"tilt": 7,  "azimuth": 29,  "area": 59.6},
    {"tilt": 6,  "azimuth": 210, "area": 170.8},
    {"tilt": 6,  "azimuth": 31,  "area": 174.8},
    {"tilt": 10, "azimuth": 29,  "area": 152.9},
    {"tilt": 10, "azimuth": 211, "area": 152.9},
    {"tilt": 9,  "azimuth": 300, "area": 355.5},
    {"tilt": 8,  "azimuth": 121, "area": 224.4},
]

total_area = sum(f["area"] for f in flächen)
gesamtstrom = pd.Series(0.0, index=weather.index)

# Realistische Modulparameter (Viessmann Vitovolt 300 M415 WM, geschätzt)
module_template = {
    'gamma_pdc': -0.003,
    'aoi_coefficient': 0.05  # Ashrae
}

# Simulation je Fläche
for i, f in enumerate(flächen, 1):
    anteil = f["area"] / total_area
    pdc0_scaled = 495510 * anteil  # Skaliere auf Gesamtleistung

    system = PVSystem(
        surface_tilt=f["tilt"],
        surface_azimuth=f["azimuth"],
        module_parameters={**module_template, 'pdc0': pdc0_scaled},
        inverter_parameters={'pdc0': pdc0_scaled},
        module_type='glass_polymer',
        racking_model='open_rack'
    )

    mc = ModelChain(system, location, aoi_model='ashrae')
    mc.run_model(weather)

    gesamtstrom += mc.results.ac

# Auswertung
ac_power = gesamtstrom / 1000

# Beispiel: CSV laden
df = pd.read_csv("Lastgang 2024.csv", sep=",")  # ggf. sep anpassen (Tabulator oder Semikolon)
df['datetime'] = pd.to_datetime(df['Datum'] + ' ' + df['Zeit'], format="%d/%m/%Y %H:%M:%S")
df.set_index('datetime', inplace=True)
df = df[['Wirkleistung [kW]']].rename(columns={'Wirkleistung [kW]': 'power'})


def prepare_timeseries_for_matching(pv_series, load_series, freq="15T", tz="Europe/Berlin", align_pv_to_load=True):
    """
    Bringt zwei Zeitreihen (PV + Last) auf gemeinsame Zeitskala und behandelt Zeitzonenprobleme.

    Parameter:
    - pv_series: pd.Series mit PV-Daten (index = datetime)
    - load_series: pd.Series mit Lastdaten (index = datetime)
    - freq: Zielauflösung (z. B. "15T", "1H")
    - tz: gewünschte Zeitzone (z. B. Europe/Berlin)

    Rückgabe:
    - pd.DataFrame mit Spalten ["pv", "load"]
    """

    # Zeitzonenvereinheitlichung
    if pv_series.index.tz is None:
        pv_series.index = pv_series.index.tz_localize(tz, nonexistent='shift_forward', ambiguous='NaT')
    else:
        pv_series.index = pv_series.index.tz_convert(tz)

    if load_series.index.tz is None:
        load_series.index = load_series.index.tz_localize(tz, nonexistent='shift_forward', ambiguous='NaT')
    else:
        load_series.index = load_series.index.tz_convert(tz)

    # Align PV time axis to load year if requested
    if align_pv_to_load:
        load_year = load_series.index[0].year
        pv_year = pv_series.index[0].year

        if load_year != pv_year:
            # Replace year in PV index
            new_index = pv_series.index.map(lambda dt: dt.replace(year=load_year))
            pv_series.index = new_index
            # Remove duplicates caused by leap year mismatch
            pv_series = pv_series[~pv_series.index.duplicated(keep='first')]


    # Resampling
    pv_resampled = pv_series.resample(freq).interpolate(method='time')
    load_resampled = load_series.resample(freq).mean()

    # Gemeinsame Zeitbasis
    df = pd.DataFrame({
        "pv": pv_resampled,
        "load": load_resampled
    }).dropna()

    return df


combined = prepare_timeseries_for_matching(ac_power, df['power'], freq="15T")

# === Eigenverbrauchsoptimierung mit Batterie ===
combined["used_pv"] = combined[["pv", "load"]].min(axis=1)
combined["excess_pv"] = combined["pv"] - combined["used_pv"]
combined["grid_import"] = combined["load"] - combined["used_pv"]

battery_capacity_kwh = 215 * 0.9
battery_power_kw = 100 * 0.9
interval_hours = 0.25
max_energy_per_step = battery_power_kw * interval_hours

battery_soc = battery_capacity_kwh
soc_list = []
battery_output = []
battery_charge = []

peak_limit_kw = 210 #270
#batt_ps_output = []
grid_costs = 0.0

for i, row in combined.iterrows():
    pv, load = row['pv'], row['load']
    excess = pv - load
    batt_out = 0
    battery_charge_interval = 0.0

    if load <= 0.75 * peak_limit_kw:
        if excess >= 0:
            available_capacity = battery_capacity_kwh - battery_soc
            charge_amount = min(excess * interval_hours, max_energy_per_step, available_capacity)
            battery_soc += charge_amount
            #battery_output.append(0)
            battery_charge_interval += charge_amount
            #battery_charge.append(charge_amount)
        else:
            demand = abs(excess) * interval_hours
            discharge_amount = min(demand, battery_soc, max_energy_per_step)
            battery_soc -= discharge_amount
            batt_out += discharge_amount / interval_hours
            #battery_charge.append(0)
    
    net_load = load - (row['used_pv'] + batt_out)

    if net_load > peak_limit_kw:
        required_discharge = (net_load - peak_limit_kw) * interval_hours
        possible_discharge = min(battery_soc, max_energy_per_step)
        actual_discharge = min(required_discharge, possible_discharge)
        battery_soc -= actual_discharge
        batt_out += actual_discharge / interval_hours
    elif load >= 0.7 * peak_limit_kw:
        # Optional: Batterie lädt aus dem Netz bei niedriger Last
        charge = min(battery_capacity_kwh - battery_soc, battery_power_kw * interval_hours)
        battery_soc += charge
        batt_out = 0.0
        
    battery_charge.append(battery_charge_interval)
    battery_output.append(batt_out)
    soc_list.append(battery_soc)


combined["battery_output"] = battery_output
combined["battery_soc"] = soc_list
combined["battery_charge"] = battery_charge

combined["used_pv_with_batt"] = combined["used_pv"] + combined["battery_charge"] / interval_hours
combined["grid_import_with_pv"] = combined["load"] - combined["used_pv"]
combined["grid_import_with_batt"] = combined["load"] - (combined["used_pv"] + combined["battery_output"])
combined["grid_import_with_batt"] = combined["grid_import_with_batt"].clip(lower=0)

# Kennzahlen
# in kWh
ev_batt_kwh = (combined["used_pv"] * interval_hours).sum() + combined["battery_charge"].sum()

# gesamte PV-Produktion in kWh
total_pv_kwh = (combined["pv"] * interval_hours).sum()

# korrekte Quote
ev_quote_batt = ev_batt_kwh / total_pv_kwh
autarkie_batt = (combined["load"].sum() - combined["grid_import_with_batt"].sum()) / combined["load"].sum()

print("\n🔋 MIT Batterie:")
print(f"   - Eigenverbrauchsquote: {ev_quote_batt:.1%}")
print(f"   - Autarkiegrad:         {autarkie_batt:.1%}")
print(f"   - Geladene Batterie-Energie: {combined['battery_charge'].sum():.1f} kWh")
print(f"   - SOC am Jahresende:        {combined['battery_soc'].iloc[-1]:.1f} kWh")

# Eigenverbrauch ohne Batterie in kWh
used_pv_kwh = (combined["used_pv"] * interval_hours).sum()

# Eigenverbrauch mit Batterie in kWh
used_pv_with_batt_kwh = (combined["used_pv_with_batt"] * interval_hours).sum()

# Differenz = durch Batterie zusätzlich genutzte PV-Energie
additional_self_consumed_pv_kwh = used_pv_with_batt_kwh - used_pv_kwh

print(f"📈 Zusätzlich genutzte PV-Energie durch Batterie: {additional_self_consumed_pv_kwh:.2f} kWh")

total_pv_kwh = (combined["pv"] * interval_hours).sum()
print(f"🔍 Anteil der zusätzlichen PV-Nutzung durch Batterie: {(additional_self_consumed_pv_kwh / total_pv_kwh):.1%}")

# Eigenverbrauchsquote
ev_quote = combined["used_pv"].sum() / combined["pv"].sum()
autarkie = combined["used_pv"].sum() / combined["load"].sum()

print("\n OHNE Batterie:")
print(f"🔋 Eigenverbrauchsquote: {ev_quote:.1%}")
print(f"🏠 Autarkiegrad: {autarkie:.1%}")

used_pv_kwh = (combined["used_pv"] * 0.25).sum()
print(f"🔋 PV-Eigenverbrauch gesamt: {used_pv_kwh:.2f} kWh")

# === Peak Shaving nach Eigenverbrauchsoptimierung ===
'''    
combined["batt_ps_output"] = batt_ps_output
combined["soc_ps"] = soc_list
combined["net_load_after_ps_total"] = combined["grid_import_with_batt"] - combined["batt_ps_output"]
combined["net_load_after_ps_total"] = combined["net_load_after_ps_total"].clip(lower=0)
'''
# === Analyse ===
original_peak = combined["load"].max()
after_pv_peak = combined["grid_import_with_pv"].max()
new_peak = combined["grid_import_with_batt"].max()
leistungspreis = 166.03
savings_ps = (after_pv_peak - new_peak) * leistungspreis

print("\n📊 Zweistufige Optimierung (Eigenverbrauchsoptimierung ➜ Peak Shaving):")
print(f"🔼 Urspr\u00fcngliche Lastspitze:         {original_peak:.1f} kW")
print(f"Lastspitze nach PV: {after_pv_peak:.1f} kW")
print(f"🔽 Lastspitze nach PV + Batterie:    {new_peak:.1f} kW")
print(f"💰 Potenzielles Einsparpotenzial durch Peak Shaving: {savings_ps:.2f} € / Jahr")

# Eigenverbrauch ohne Batterie in kWh
used_pv_kwh = (combined["used_pv"] * interval_hours).sum()

# Eigenverbrauch mit Batterie in kWh
used_pv_with_batt_kwh = (combined["used_pv_with_batt"] * interval_hours).sum()

# Differenz = durch Batterie zusätzlich genutzte PV-Energie
additional_self_consumed_pv_kwh = used_pv_with_batt_kwh - used_pv_kwh

netto_arbeitspreis = 0.08
savings_ev = additional_self_consumed_pv_kwh * netto_arbeitspreis
print(f"💰 Potenzielles Einsparpotenzial durch Eigenverbauchsoptimierung: {savings_ev:.2f} € / Jahr")

total_savings = savings_ps + savings_ev
print(f"💰 Potenzielles Gesamteinsparpotenzial: {total_savings:.2f} € / Jahr")

# === Plot ===
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=combined.index, y=combined['load'], name='Original Load', line=dict(color='gray')))
fig.add_trace(go.Scatter(x=combined.index, y=combined['grid_import_with_pv'], name='Nach PV', line=dict(color='green')))
fig.add_trace(go.Scatter(x=combined.index, y=combined['grid_import_with_batt'], name='Nach PV + Batterie', line=dict(color='red')))
#fig.add_trace(go.Scatter(x=combined.index, y=combined['soc_ps'], name='SOC PS-Batterie', yaxis='y2', line=dict(color='blue', dash='dot')))

fig.update_layout(
    title="🔁 Zweistufige Optimierung: Eigenverbrauch + Peak Shaving",
    xaxis=dict(title="Zeit"),
    yaxis=dict(title="Leistung [kW]"),
    #yaxis2=dict(title="SOC [kWh]", overlaying='y', side='right', showgrid=False),
    legend=dict(x=0.01, y=0.99),
    margin=dict(l=40, r=40, t=40, b=40)
)
fig.show()