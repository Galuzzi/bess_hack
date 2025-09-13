from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import pandas as pd
import boto3
import io

# NEW: import UNSIGNED + Config and ClientError for clearer handling
from botocore import UNSIGNED
from botocore.client import Config
from botocore.exceptions import ClientError

app = FastAPI()

# Set your S3 bucket (public)
S3_BUCKET = "maxxwatt-hackathon-datasets"

# Create an unsigned S3 client (no credentials needed)
s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))

class SOCReading(BaseModel):
    timestamp: datetime
    soc: float

@app.get("/cloud/BESS/{device_id}/soc", response_model=List[SOCReading])
def get_soc_s3(device_id: str):
    key = f"energy_hackathon_data/BESS/{device_id}/bms1_soc.csv"
    try:
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        content = obj["Body"].read()
        # Parse CSV; ensure timestamp column is parsed
        df = pd.read_csv(io.BytesIO(content))
        if "ts" not in df.columns or "bms1_soc" not in df.columns:
            raise HTTPException(status_code=500, detail="CSV missing required columns: 'ts' and/or 'bms1_soc'.")

        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.dropna(subset=["ts"])

        # Return first 10 rows (you can sort by ts if needed)
        return [
            {"timestamp": row["ts"], "soc": float(row["bms1_soc"])}
            for _, row in df.head(10).iterrows()
        ]

    except ClientError as e:
        # Handle common S3 errors more gracefully
        code = e.response.get("Error", {}).get("Code", "Unknown")
        if code in ("NoSuchKey", "404"):
            raise HTTPException(status_code=404, detail=f"Object not found: s3://{S3_BUCKET}/{key}")
        raise HTTPException(status_code=502, detail=f"S3 client error ({code}): {str(e)}")
    except Exception as e:
        # Fallback for unexpected issues (CSV parse, etc.)
        raise HTTPException(status_code=500, detail=f"S3 read error: {str(e)}")
    

get_soc_s3('ZHPESS232A230002')