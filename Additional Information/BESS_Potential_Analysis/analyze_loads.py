import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Beispiel: CSV laden
df = pd.read_csv("Lastgang 2024.csv", sep=",")  # ggf. sep anpassen (Tabulator oder Semikolon)
df['datetime'] = pd.to_datetime(df['Datum'] + ' ' + df['Zeit'], format="%d/%m/%Y %H:%M:%S")
df.set_index('datetime', inplace=True)
df = df[['Wirkleistung [kW]']].rename(columns={'Wirkleistung [kW]': 'power'})

# 🔹 1. Durchschnittlicher Tagesverlauf (nach Uhrzeit)
daily_profile = df.groupby(df.index.time).mean()

plt.figure(figsize=(10, 4))
daily_profile.plot()
plt.title("⏱ Durchschnittlicher Tagesverlauf")
plt.ylabel("Leistung [kW]")
plt.xlabel("Uhrzeit")
plt.grid(True)
plt.show()

# 🔹 2. Jahresverlauf: Tagesmaximum (für Heatmap)
daily_max = df.resample("D").max()

plt.figure(figsize=(14, 4))
daily_max.plot()
plt.title("📈 Maximale Tageslast über das Jahr")
plt.ylabel("Leistung [kW]")
plt.xlabel("Datum")
plt.grid(True)
plt.show()

# 🔹 3. Lastspitze & Tagesverlauf des Peak-Tags
peak_time = df['power'].idxmax()
peak_day = peak_time.date()
df_peak_day = df[df.index.date == peak_day]

print(f"🔺 Lastspitze: {df['power'].max()} kW am {peak_time}")

plt.figure(figsize=(10, 4))
df_peak_day['power'].plot()
plt.title(f"🔍 Tagesprofil am Lastspitzen-Tag: {peak_day}")
plt.ylabel("Leistung [kW]")
plt.xlabel("Uhrzeit")
plt.grid(True)
plt.show()

# 🔹 4. Analyse: Wie viele Hochlast-Tage (> z. B. 90 % vom Peak)?
threshold = 0.9 * df['power'].max()
df['is_high'] = df['power'] > threshold

# Gruppieren nach Tagen
high_load_counts = df['is_high'].resample('D').sum()
high_load_days = high_load_counts[high_load_counts >= 4]  # z. B. ≥ 1h (4× 15min)

print(f"📊 Tage mit ≥1h sehr hoher Last: {len(high_load_days)}")

# Optional: Plotten dieser Tage
plt.figure(figsize=(10, 4))
high_load_counts.plot()
plt.axhline(4, color='red', linestyle='--', label='1 Stunde Schwelle')
plt.title("📊 Anzahl Hochlast-Zeitfenster pro Tag")
plt.ylabel("15-min Intervalle > Schwelle")
plt.xlabel("Datum")
plt.legend()
plt.grid(True)
plt.show()

# Clustering typischer Lasttage
# Schritt 1: Tagesprofile extrahieren
daily_profiles = df['power'].groupby(df.index.date).apply(lambda x: x.values[:96])  # 96 Intervalle à 15 Min
# Länge jedes Tagesprofils ermitteln
profile_lengths = daily_profiles.apply(len)

# Tage mit unvollständigen Profilen (≠ 96 Einträge)
invalid_days = profile_lengths[profile_lengths != 96]
print("❗ Unvollständige Tage:")
print(invalid_days)
#daily_profiles = df['power'].groupby(df.index.date)
# Nur vollständige Tagesprofile behalten
daily_profiles_clean = daily_profiles[profile_lengths == 96]

# Stack in Matrix (jetzt sicher)
daily_matrix = np.stack(daily_profiles_clean.values)

# Schritt 2: Normieren (Skalierung pro Tag)
scaler = StandardScaler()
daily_scaled = scaler.fit_transform(daily_matrix)

# Schritt 3: KMeans Clustering (z. B. 4 typische Lasttage)
kmeans = KMeans(n_clusters=4, random_state=42)
labels = kmeans.fit_predict(daily_scaled)

# Schritt 4: Ergebnis plotten
plt.figure(figsize=(10, 6))
for cluster_id in range(4):
    cluster_profiles = daily_matrix[labels == cluster_id]
    mean_profile = cluster_profiles.mean(axis=0)
    plt.plot(mean_profile, label=f'Cluster {cluster_id+1} ({len(cluster_profiles)} Tage)')

plt.title("⚡ Typische Lastverläufe (K-Means Cluster)")
plt.xlabel("Zeit (15-min Intervalle)")
plt.ylabel("Leistung [kW]")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()