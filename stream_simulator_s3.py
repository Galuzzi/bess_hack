import time
import boto3
import pandas as pd
import io
from datetime import datetime
import os

def simulate_stream_from_s3(bucket_name, object_key, delay=1.0):
    s3 = boto3.client('s3')
    metric = os.path.splitext(os.path.basename(object_key))[0]
    
    try:
        # Load object from S3
        obj = s3.get_object(Bucket=bucket_name, Key=object_key)
        content = obj['Body'].read()

        # Read as DataFrame
        df = pd.read_csv(io.BytesIO(content))

        if 'ts' in df.columns:
            df['ts'] = pd.to_datetime(df['ts'])
        else:
            now = datetime.utcnow()
            df['ts'] = [now + pd.Timedelta(seconds=i) for i in range(len(df))]

        for _, row in df.iterrows():
            data = {
                "timestamp": row['ts'].isoformat(),
                "value": row.get(metric, 0)
            }
            print(data)
            time.sleep(delay)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simulate_stream_from_s3(
        bucket_name="maxxwatt-hackathon-datasets",
        object_key="energy_hackathon_data/BESS/ZHPESS232A230002/bms1_soc.csv",
        delay=1.0  # 1 second per row
    )
