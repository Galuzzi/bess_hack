from forecasting.simulate_myopic_optimization import plot_soc_forecast, plot_revenue_forecast

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="BESS Optimization API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:3000"] for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", summary="Health check")
def health():
    """
    Returns API health status.
    """
    return {"status": "ok"}

@app.post(
    "/plot-soc",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Returns a PNG image of the State of Charge forecast plot."
        }
    },
    summary="Get State of Charge Forecast Plot"
)
async def plot_soc_endpoint(
    date: datetime = Query(..., description="Forecast start date in YYYY-MM-DD format (latest: 2025-09-10)")
):
    """
    Generates and returns a PNG image of the State of Charge (SoC) forecast plot for the selected date.
    """
    buf = plot_soc_forecast(date)
    return StreamingResponse(buf, media_type="image/png")

@app.post(
    "/plot-revenue",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Returns a PNG image of the Revenue forecast plot."
        }
    },
    summary="Get Revenue Forecast Plot"
)
async def plot_revenue_endpoint(
    date: datetime = Query(..., description="Forecast start date in YYYY-MM-DD format (latest: 2025-09-10)")
):
    """
    Generates and returns a PNG image of the Revenue forecast plot for the selected date.
    """
    buf = plot_revenue_forecast(date)
    return StreamingResponse(buf, media_type="image/png")