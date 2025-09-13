import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

# Directory with data
DATA_DIR = "Shared Files Sept 2023 to June 2025/ZHPESS232A230002"

def load_csv(filename, value_col):
    df = pd.read_csv(os.path.join(DATA_DIR, filename), parse_dates=["ts"])
    return df.set_index("ts")[[value_col]]

# Load and merge data (same as before)
soh = load_csv("bms1_soh.csv", "bms1_soh")
soc = load_csv("bms1_soc.csv", "bms1_soc")
current = load_csv("bms1_c.csv", "bms1_c")
temp = load_csv("bms1_cell_ave_t.csv", "bms1_cell_ave_t")
voltage = load_csv("bms1_cell_ave_v.csv", "bms1_cell_ave_v")

try:
    v_max = load_csv("bms1_cell_max_v.csv", "bms1_cell_max_v")
    v_min = load_csv("bms1_cell_min_v.csv", "bms1_cell_min_v")
    voltage_imbalance = v_max - v_min
    voltage_imbalance.columns = ["voltage_imbalance"]
except Exception:
    voltage_imbalance = None

data = soh.copy()
for df in [soc, current, temp, voltage]:
    data = pd.merge_asof(data.sort_index(), df.sort_index(), left_index=True, right_index=True, direction='nearest')
if voltage_imbalance is not None:
    data = pd.merge_asof(data.sort_index(), voltage_imbalance.sort_index(), left_index=True, right_index=True, direction='nearest')
data = data.interpolate().dropna()

# Feature engineering
data["soc_swing"] = data["bms1_soc"].diff().abs().rolling(60).sum()
data["avg_current"] = data["bms1_c"].rolling(60).mean()
data["c_rate"] = data["bms1_c"] / 100
data["thermal_stress"] = (data["bms1_cell_ave_t"] > 35).rolling(60).sum()
if voltage_imbalance is not None:
    data["voltage_imbalance_trend"] = data["voltage_imbalance"].rolling(60).mean()

feature_cols = ["soc_swing", "avg_current", "c_rate", "thermal_stress"]
if voltage_imbalance is not None:
    feature_cols.append("voltage_imbalance_trend")
X = data[feature_cols].fillna(0)

# Train anomaly detector on historical data
iso = IsolationForest(contamination=0.01, random_state=42)
iso.fit(X)

# Forecast future features (simple approach: use last rolling mean)
n_forecast = 30  # days or time steps
last_index = data.index[-1]
future_index = pd.date_range(start=last_index, periods=n_forecast+1, freq='D')[1:]

future_features = pd.DataFrame(
    {col: [data[col].rolling(60).mean().iloc[-1]]*n_forecast for col in feature_cols},
    index=future_index
)

# Predict anomalies in the forecasted feature space
future_anomaly = iso.predict(future_features)
future_features["anomaly_flag"] = future_anomaly == -1

# Plot
plt.figure(figsize=(12,6))
plt.plot(data.index, data["bms1_soh"], label="Historical SOH")
plt.scatter(data.index[data["bms1_soh"].notna()], data["bms1_soh"][data["bms1_soh"].notna()], color='blue', s=5)
plt.scatter(future_features.index[future_features["anomaly_flag"]], 
            [data["bms1_soh"].iloc[-1]]*sum(future_features["anomaly_flag"]), 
            color='red', label="Forecasted Anomaly", marker='x')
plt.xlabel("Time")
plt.ylabel("SOH (%)")
plt.title("Forecasted SOH Anomalies")
plt.legend()
plt.tight_layout()
plt.show()

print("Forecasted anomaly dates:")
print(future_features.index[future_features["anomaly_flag"]])