import pandas as pd
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
import matplotlib.pyplot as plt

# Standort Prüm
location = Location(50.2089, 6.4227, 'Europe/Berlin')

# TMY-Daten einlesen
tmy_data = pd.read_csv('tmy_50.209_6.423_2005_2023.csv', skiprows=17, nrows=8760)  # Passe den Dateinamen an
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

# Aktuelle Zeitachse ermitteln
original_times = weather.index

# Neue Zeitachse erzeugen (1. Januar bis 31. Dezember 2022, stündlich)
new_times = pd.date_range('2022-01-01 00:00', '2022-12-31 23:00', freq='H', tz='Europe/Berlin')

# Ersetzen
weather.index = new_times

module_parameters = {
    'pdc0': 495510,      # 495,51 kWp TODO Check this pdc0 value
    'gamma_pdc': -0.003,
    'aoi_coefficient': 0.05  # typisch für Ashrae-Modell
}

system = PVSystem(
    surface_tilt=30,
    surface_azimuth=180,
    module_parameters=module_parameters,
    inverter_parameters={'pdc0': 495510},
    module_type='glass_polymer',          # realistisch für dein Modul
    racking_model='open_rack'             # wegen „gut hinterlüftet“ laut PDF
)

mc = ModelChain(system, location, aoi_model='ashrae')
mc.run_model(weather)

# Ergebnisse anzeigen
ac_power = mc.results.ac.loc['2022']
#ac_power = mc.results.ac
energy_yearly = ac_power.sum() / 1000  # kWh
print(f"Jahresproduktion: {energy_yearly:.2f} kWh")

# Tägliche Produktion plotten
ac_power.resample('D').sum().plot()
plt.title("Tägliche PV-Produktion (kWh)")
plt.ylabel("Energie [kWh]")
plt.xlabel("Datum")
plt.grid(True)
plt.show()