from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime

app = FastAPI()

# Define response model
class SOCReading(BaseModel):
    timestamp: datetime
    soc: float

@app.get("/BESS/{device_id}/soc", response_model=List[SOCReading])
def get_soc(device_id: str):
    try:
        df = pd.read_csv(f"./energy_hackathon_data/BESS/{device_id}/bms1_soc.csv")
        df['ts'] = pd.to_datetime(df['ts'])
        return [{"timestamp": row['ts'], "soc": row['bms1_soc']} for _, row in df.head(10).iterrows()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
