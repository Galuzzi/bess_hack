from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import pandas as pd
import boto3
import io

app = FastAPI()

# Set your S3 bucket
S3_BUCKET = "maxxwatt-hackathon-datasets"
s3 = boto3.client("s3")

class SOCReading(BaseModel):
    timestamp: datetime
    soc: float

@app.get("/cloud/BESS/{device_id}/soc", response_model=List[SOCReading])
def get_soc_s3(device_id: str):
    key = f"energy_hackathon_data/BESS/{device_id}/bms1_soc.csv"
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        content = obj['Body'].read()
        df = pd.read_csv(io.BytesIO(content))
        df['ts'] = pd.to_datetime(df['ts'])
        return [{"timestamp": row['ts'], "soc": row['bms1_soc']} for _, row in df.head(10).iterrows()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 read error: {str(e)}")
