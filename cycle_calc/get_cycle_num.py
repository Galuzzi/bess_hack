
import pandas as pd
import numpy as np
from pathlib import Path

# Fixed data
BASE = Path("energy_hackathon_data/BESS/ZHPESS232A230002")
PATH_BMS_SOC = BASE / "bms1_soc.csv"

TS_COL = "ts"       # common timestamp column name across

def read_series(path: Path, ts_col: str, tz: str | None = None) -> pd.Series:
    df = pd.read_csv(path)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) == 0:
        val_col = next(c for c in df.columns if c != ts_col)
    else:
        val_col = num_cols[0]
    idx = pd.to_datetime(df[ts_col], errors="coerce")
    s = pd.Series(pd.to_numeric(df[val_col], errors="coerce").values, index=idx, name=val_col)
    s = s[~s.index.isna()].sort_index()
    if tz:
        if s.index.tz is None:
            # Use ambiguous='infer' to let pandas guess DST transitions
            s.index = s.index.tz_localize(tz, ambiguous="infer")
        else:
            s.index = s.index.tz_convert(tz)
    return s

def get_cycle_number(series):
    # Time step in seconds
    time_delta = (series.index[1] - series.index[0]).total_seconds()
    
    # Step 1: (Optional) Fill missing data if needed
    series = series.interpolate()  # Ensure no NaNs
    
    # Step 2: FFT
    fft_vals = np.fft.fft(series)
    fft_freqs = np.fft.fftfreq(len(series), d=time_delta)  # 900 seconds per sample (15 min)
    
    # Step 3: Focus on positive frequencies
    positive_freqs = fft_freqs[fft_freqs > 0]
    positive_magnitudes = np.abs(fft_vals[fft_freqs > 0])
    
    # Step 4: Find dominant frequency
    dominant_freq = positive_freqs[np.argmax(positive_magnitudes)]
    
    # Step 5: Total duration in seconds
    total_duration_sec = (series.index[-1] - series.index[0]).total_seconds()
    
    # Step 6: Estimate number of cycles
    num_cycles = dominant_freq * total_duration_sec
    
    return round(num_cycles)

def main():
    # Data that is adjustable by the users. Maxium is 2025-06-13
    date = "2025-06-13"
    
    series = read_series(PATH_BMS_SOC, TS_COL).rename("bms1_soc")
    series = series.resample("h").mean()
    
    num_cycle = get_cycle_number(series)
    
    print(f"Total cycles: {num_cycle} cycles")
    
    current_date = pd.to_datetime(date)
    month_behind = current_date - pd.DateOffset(months=1)
    
    series_last_month = series[month_behind:current_date]
    num_cycle_last_month = get_cycle_number(series_last_month)
    
    print(f"Cycles in the last month: {num_cycle_last_month} cycles")

if __name__ == "__main__":
    main()
