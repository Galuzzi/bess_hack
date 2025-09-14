from forecasting.simulate_myopic_optimization import plot_soc_forecast, plot_revenue_forecast

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from datetime import datetime
from fastapi import Query

# Import your functions. Save your original script as `forecast_module.py`
# and ensure it exposes:
# - simulate_myopic_optimization(market_price, years, date, **kwarg)
# - plot_soc_forecast(state_of_charge, date)
# If your filename differs, change import accordingly.


app = FastAPI(title="BESS Optimization API", version="1.0.0")

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


# Example FastAPI endpoint
@app.post("/plot-soc")
async def plot_soc_endpoint(
    date: datetime = Query(..., description="Forecast start date in YYYY-MM-DD format (latest: 2025-09-10)")
):
    buf = plot_soc_forecast(date)
    return StreamingResponse(buf, media_type="image/png")

@app.post("/plot-revenue")
async def plot_revenue_endpoint(
    date: datetime = Query(..., description="Forecast start date in YYYY-MM-DD format (latest: 2025-09-10)")
):
    buf = plot_revenue_forecast(date)
    return StreamingResponse(buf, media_type="image/png")