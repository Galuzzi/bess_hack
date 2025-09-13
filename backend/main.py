from soc_predictor import simulate_myopic_optimization

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import pandas as pd
import io

# Import your functions. Save your original script as `forecast_module.py`
# and ensure it exposes:
# - simulate_myopic_optimization(market_price, years, date, **kwarg)
# - plot_soc_forecast(state_of_charge, date)
# If your filename differs, change import accordingly.
from forecast_module import simulate_myopic_optimization

app = FastAPI(title="BESS Data Analysis API", version="1.0")

@app.post("/simulate-soc", summary="Simulate State of Charge using Market Price Data")
async def simulate_endpoint(
    market_price_file: UploadFile = File(..., description="CSV file with market_price_<year> columns"),
    years: str = Form(..., description="Comma-separated years to simulate, e.g. '2019,2020,2021'"),
    date: str = Form(..., description="Simulation start date, e.g. '2025-09-01'"),
    # Optional parameters
    load_p_set: Optional[float] = Form(50.0),
    storage_p_nom: Optional[float] = Form(10.0),
    storage_max_hours: Optional[float] = Form(8.0),
    storage_marginal_cost: Optional[float] = Form(0.1),
):
    # Parse years
    try:
        years_list = [int(y.strip()) for y in years.split(",") if y.strip()]
        if not years_list:
            raise ValueError("No years provided")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid years parameter: {e}")

    # Read uploaded CSV
    try:
        file_bytes = await market_price_file.read()
        market_price = pd.read_csv(io.BytesIO(file_bytes), parse_dates=True, index_col=0)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV file: {e}")

    # kwarg config
    kwarg = {
        "Load": {"p_set": float(load_p_set)},
        "StorageUnit": {
            "p_nom": float(storage_p_nom),
            "max_hours": float(storage_max_hours),
            "marginal_cost": float(storage_marginal_cost),
        },
    }

    # Run simulation
    try:
        state_of_charge_df, system_cost = simulate_myopic_optimization(
            market_price=market_price,
            years=years_list,
            date=date,
            **kwarg
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {e}")

    # Convert state_of_charge_df to JSON
    soc_json = state_of_charge_df.to_dict(orient="split")
    # "split" keeps index/columns separate so frontend can rebuild DataFrame easily

    return JSONResponse(content={
        "state_of_charge": soc_json,
        "system_cost": system_cost
    })


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}