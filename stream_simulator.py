# stream_simulator.py

import time
import pandas as pd
from datetime import datetime
import random
import os

def simulate_stream(filepath, delay=1.0):
    df = pd.read_csv(filepath)
    metric = os.path.splitext(os.path.basename(filepath))[0]
    
    if 'ts' in df.columns:
        df['ts'] = pd.to_datetime(df['ts'])
    else:
        now = datetime.now(datetime.timezone.utc)
        df['ts'] = [now + pd.Timedelta(seconds=i) for i in range(len(df))]

    for _, row in df.iterrows():
        data = {
            "timestamp": row["ts"].isoformat(),
            "value": row.get(metric, round(random.uniform(20, 90), 2))
        }
        print(data)
        time.sleep(delay)

if __name__ == "__main__":
    simulate_stream(
        filepath="energy_hackathon_data/BESS/ZHPESS232A230002/bms1_soc.csv",  # <- adjust this path
        delay=60.0  # seconds between rows
    )