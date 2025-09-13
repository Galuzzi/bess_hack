import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

# Directory with data
DATA_DIR = "Shared Files Sept 2023 to June 2025/ZHPESS232A230002"

# Helper to load a CSV with timestamp
def load_csv(filename, value_col):
    df = pd.read_csv(os.path.join(DATA_DIR, filename), parse_dates=["ts"])
    return df.set_index("ts")[[value_col]]

# Load all relevant data
soh = load_csv("bms1_soh.csv", "bms1_soh")
soc = load_csv("bms1_soc.csv", "bms1_soc")
current = load_csv("bms1_c.csv", "bms1_c")
temp = load_csv("bms1_cell_ave_t.csv", "bms1_cell_ave_t")
voltage = load_csv("bms1_cell_ave_v.csv", "bms1_cell_ave_v")

# Optional: voltage imbalance
try:
    v_max = load_csv("bms1_cell_max_v.csv", "bms1_cell_max_v")
    v_min = load_csv("bms1_cell_min_v.csv", "bms1_cell_min_v")
    voltage_imbalance = v_max - v_min
    voltage_imbalance.columns = ["voltage_imbalance"]
except Exception:
    voltage_imbalance = None

# Start with SOH as the base
data = soh.copy()

# Merge each dataframe on timestamp using merge_asof (nearest match)
for df in [soc, current, temp, voltage]:
    data = pd.merge_asof(data.sort_index(), df.sort_index(), left_index=True, right_index=True, direction='nearest')

if voltage_imbalance is not None:
    data = pd.merge_asof(data.sort_index(), voltage_imbalance.sort_index(), left_index=True, right_index=True, direction='nearest')

data = data.interpolate().dropna()

# Feature engineering
data["soc_swing"] = data["bms1_soc"].diff().abs().rolling(60).sum()  # 60-sample window
data["avg_current"] = data["bms1_c"].rolling(60).mean()
data["c_rate"] = data["bms1_c"] / 100  # Assume 100Ah battery, adjust as needed
data["thermal_stress"] = (data["bms1_cell_ave_t"] > 35).rolling(60).sum()
if voltage_imbalance is not None:
    data["voltage_imbalance_trend"] = data["voltage_imbalance"].rolling(60).mean()

# Target: SOH drop (difference from initial)
data["soh_drop"] = data["bms1_soh"].iloc[0] - data["bms1_soh"]

# Prepare features and target
feature_cols = ["soc_swing", "avg_current", "c_rate", "thermal_stress"]
if voltage_imbalance is not None:
    feature_cols.append("voltage_imbalance_trend")
X = data[feature_cols].fillna(0)
y = data["soh_drop"]

# Fit model
model = GradientBoostingRegressor()
model.fit(X, y)
y_pred = model.predict(X)

test = data["bms1_soh"].iloc[1] - y_pred
# Plot actual vs predicted SOH
plt.figure(figsize=(10,5))
plt.plot(data.index, data["bms1_soh"], label="Actual SOH")
plt.plot(data.index, data["bms1_soh"].iloc[1] - y_pred, label="Predicted SOH", linestyle="--")
plt.xlabel("Time")
plt.ylabel("SOH (%)")
plt.legend()
plt.title("SOH Degradation Forecast")
plt.tight_layout()
plt.show()

# Feature importance
plt.figure(figsize=(8,4))
plt.bar(feature_cols, model.feature_importances_)
plt.title("Feature Importance")
plt.ylabel("Importance")
plt.tight_layout()
plt.show()

# Calculate and print MSE and MAPE
mse = mean_squared_error(y, y_pred)
mape = mean_absolute_percentage_error(y, y_pred)
print("MSE:", mse)
print("MAPE:", mape)