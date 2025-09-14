"""
This script is the core component of the system. Before running it, make sure to install the required packages:

```bash
pip install pypsa matplotlib
```

The idea is to place this logic in the backend, where it runs in the background — typically completing in under a minute.
The script simulates 5 different yearly scenarios to produce a predictive State of Charge (SoC) output.
I'm not sure how well the frontend will be able to render the matplotlib-generated plots, but we'll find out.
"""
import pandas as pd
import pypsa
import matplotlib.pyplot as plt
import io
from datetime import datetime

def optimize_simple_model(market_price_series, add_battery=True, **kwarg):
    """
    Sets up and optimizes a simple energy system model using PyPSA.

    The model includes:
    - A single electricity bus (e.g., representing Germany),
    - A generator with time-varying marginal costs from the given market price series,
    - A fixed industrial load,
    - Optionally, a battery energy storage system (BESS) with user-defined parameters.

    The function runs a linear optimal power flow (LOPF) optimization to minimize 
    total system cost over the given time period.

    read more on components here: https://pypsa.readthedocs.io/en/latest/user-guide/components.html

    Parameters:
    -----------
        market_price_series (pandas.Series): Time-indexed series of electricity market prices (€/MWh).
        add_battery (bool, optional): Whether to include a battery storage unit in the model (default: True).
        **kwarg: Dictionary containing model parameters:
            - 'Load': Dict with 'p_set' (fixed demand in MW).
            - 'StorageUnit': Dict with 'p_nom', 'max_hours', and 'marginal_cost' 
                             for battery config (only used if add_battery is True).

    Returns:
    --------
        state_of_charge (pandas.Series): Battery state of charge over time (if battery is included).
        system_cost (float): Total system cost in million euros per year.
    """

    # Create a new empty network
    n = pypsa.Network()
    
    n.set_snapshots(market_price_series.index)
    
    # Add a single bus (e.g. "DE")
    n.add("Bus", "DE")
    
    # Add a generator connected to that bus
    n.add("Generator",
          "DE Electricity Market",
          bus="DE",
          p_nom_extendable=True,
          marginal_cost=market_price_series         # €/MWh
    )
    
    # Add a load connected to the same bus
    n.add("Load",
          "Industry",
          bus="DE",
          p_set=kwarg["Load"]["p_set"]              # Fixed demand (MW)
    )

    if add_battery:
        # Add a battery
        n.add("StorageUnit",
              "BESS",
              bus="DE",
              p_nom=kwarg["StorageUnit"]["p_nom"],  # Fixed capacity (MW)
              max_hours=kwarg["StorageUnit"]["max_hours"], 
              marginal_cost=kwarg["StorageUnit"]["marginal_cost"],
             )
    
    # Optional: run linear optimal power flow (LOPF)
    n.optimize()
    
    # View results
    state_of_charge = n.storage_units_t.state_of_charge["BESS"]

    # Power rate of batteries (MW)
    battery_power = n.storage_units_t.p["BESS"]
    
    # Revenue time series (€/h) from discharging
    battery_revenue = battery_power * market_price_series

    return state_of_charge, battery_revenue

def simulate_myopic_optimization(market_price, years, date, **kwarg):
    """
    Simulates a myopic (short-term) energy system optimization for different years 
    using a simple model. The optimization uses historical or current market prices 
    up to "day-ahead" and switches to future market prices for each target year 
    beyond that point.

    This is useful for comparing how the system would behave in the near future 
    under different historical market price patterns.

    Parameters:
    -----------
        market_price (pandas.DataFrame): A DataFrame with datetime index and one column per year, 
                                         named like "market_price_<year>".
        years (list of int): List of years to simulate using future market prices.
        date (str or pd.Timestamp): The starting date of the simulation (e.g., '2025-07-01').
        **kwarg:

    Returns:
    --------
        state_of_charge (pandas.DataFrame): Battery state of charge throughout the year
        system_cost (dict): Dictionary mapping each year to its corresponding system cost (in million €/a).
    """

    current_date = pd.to_datetime(date)
    day_ahead = current_date + pd.Timedelta(days=1)
    current_date + pd.Timedelta(days=7)

    state_of_charge = pd.DataFrame()
    battery_revenue = pd.DataFrame()
    
    for year in years:
        # Extract relevant slices
        recent_prices = market_price.loc[market_price.index <= day_ahead, f"market_price_{current_date.year}"]
        future_prices = market_price.loc[market_price.index > day_ahead, f"market_price_{year}"]
        
        # Combine them into one consistent Series
        market_price_series = pd.concat([recent_prices, future_prices]).sort_index()
        
        state_of_charge_year, battery_revenue_year = optimize_simple_model(market_price_series, **kwarg)

        state_of_charge = pd.concat([state_of_charge, state_of_charge_year], axis=1)
        battery_revenue = pd.concat([battery_revenue, battery_revenue_year], axis=1)

    return state_of_charge, battery_revenue


def plot_soc_forecast(date: datetime, unit="MWh"):
    """
    Plots the forecasted state of charge (SoC) distribution over a 7-day window, 
    starting from a given date, using quantile shading to represent uncertainty 
    across multiple simulation scenarios.

    The plot includes:
    - Shaded quantile ranges (0–100%, 25–75%, 37.5–62.5%) for SoC across scenarios,
    - A median SoC line,
    - A vertical marker for the day-ahead market boundary,
    - Labels, grid, and a saved PNG file of the plot.

    Parameters:
        df (pandas.DataFrame): DataFrame where each column represents 
                                             a simulation scenario, and the index is a datetime.
        date (str or pd.Timestamp): The starting date for the 7-day forecast window 
                                    (e.g., '2025-07-01').
        unit : str, optional (default = "€")
            The unit of measurement, displayed on the y-axis label.

    Returns:
        None. (Displays and saves the plot as 'state_of_charge_plot.png'.)
    """

    kwarg = {
        "Load":{
            "p_set":50 # in MW
        },
        "StorageUnit":{
            "p_nom":10, # in MW (better less than load)
            "max_hours":8, # in hours
            "marginal_cost":0.1 # in €/MW
        },
    }

    name = "State of Charge"

    # run this on the main repo level to work
    market_price = pd.read_csv("forecasting/market_price.csv", parse_dates=True, index_col=0)
    years = [2019, 2020, 2021, 2022, 2023, 2024]
    
    df, _ = simulate_myopic_optimization(
        market_price, 
        years, 
        date, 
        **kwarg
    )

    current_date = pd.to_datetime(date)
    day_ahead = current_date + pd.Timedelta(days=1)
    week_ahead = current_date + pd.Timedelta(days=7)

    # Cut the time series only for the next week
    df = df[current_date:week_ahead]

    # Calculate percentiles across columns for each timestamp
    q_0 = df.min(axis=1)  # or .quantile(0.0)
    q_25 = df.quantile(0.25, axis=1)
    q_37 = df.quantile(0.375, axis=1)
    q_50 = df.median(axis=1)
    q_62 = df.quantile(0.625, axis=1)
    q_75 = df.quantile(0.75, axis=1)
    q_100 = df.max(axis=1)  # or .quantile(1.0)

    # Start plotting
    plt.figure(figsize=(14, 6))

    # Lightest area: min to max (0–100%)
    plt.fill_between(df.index, q_0, q_100, color='black', alpha=0.2, label='0–100% range')

    # Medium area: 25–75%
    plt.fill_between(df.index, q_25, q_75, color='black', alpha=0.4, label='25–75% range')

    # Darkest area: 37.5–62.5%
    plt.fill_between(df.index, q_37, q_62, color='black', alpha=0.6, label='37.5–62.5% range')

    # median line
    plt.plot(df.index, q_50, color='blue', linestyle='-', linewidth=2, label='Median SoC')

    # Day-ahead market
    
    plt.axvline(day_ahead, color='red', linestyle='--', linewidth=2)
    plt.text(
        x=day_ahead,
        y=q_100.max(),
        s="day-ahead market",
        color='red',
        rotation=90,
        verticalalignment='top',
        horizontalalignment='right'
    )

    # Formatting
    plt.title(f"{name} Quantile Ranges")
    plt.xlabel("Time")
    plt.xlim(df.index.min(), df.index.max())
    plt.ylabel(f"{name} ({unit})")
    #plt.ylim(0, 100)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300)
    plt.close()
    buf.seek(0)  
    return buf

def plot_revenue_forecast(date: datetime, unit="€"):
    """
    Plots weekly revenue forecast vs. realized revenue for a battery system.

    This function takes a time series DataFrame of battery revenue simulations 
    (e.g., from multiple year scenarios), slices the data to 1 month before and 
    after a specified `date`, aggregates it weekly, and plots the 25–75% quantile 
    range as forecast bars. It also includes realized revenue data for the historical period.

    Parameters:
    -----------
    df : pd.DataFrame
        A DataFrame with datetime index and revenue simulations as columns.
    
    date : str or pd.Timestamp
        The reference date (typically the current date). The plot will show 
        one month before and after this date.
    
    name : str
        The name of the metric being plotted (e.g., "Battery Revenue").
        This is used in the plot title and y-axis label.
    
    unit : str, optional (default = "€")
        The unit of measurement, displayed on the y-axis label.

    Output:
    -------
    - A bar plot showing:
        * Historical realized revenue (approx. 25% quantile) in orange
        * Forecast revenue range (25–75% quantile) in green/light green
    - X-axis labeled by ISO week number (1–52)
    - Plot saved as "Battery Revenue_plot.png"
    """

    kwarg = {
        "Load":{
            "p_set":50 # in MW
        },
        "StorageUnit":{
            "p_nom":10, # in MW (better less than load)
            "max_hours":8, # in hours
            "marginal_cost":0.1 # in €/MW
        },
    }

    name = "Battery Revenue"

    # run this on the main repo level to work
    market_price = pd.read_csv("forecasting/market_price.csv", parse_dates=True, index_col=0)
    years = [2019, 2020, 2021, 2022, 2023, 2024]

    _, df = simulate_myopic_optimization(
        market_price, 
        years, 
        date, 
        **kwarg
    )
    
    # Convert and define date ranges
    current_date = pd.to_datetime(date)
    month_ahead = current_date + pd.DateOffset(months=1)
    month_behind = current_date - pd.DateOffset(months=1)
    
    # Slice the DataFrame for 1 month before and after
    df = df[month_behind:month_ahead]
    
    # Ensure datetime index
    df.index = pd.to_datetime(df.index)
    
    # Resample weekly
    df_weekly = df.resample("W").sum()
    
    # Compute quantiles across columns for each week
    q_25 = df_weekly.quantile(0.25, axis=1)
    q_75 = df_weekly.quantile(0.75, axis=1)
    iqr = q_75 - q_25
    
    # Split into historical and forecast periods
    historical_mask = (q_25.index >= month_behind) & (q_25.index < current_date)
    forecast_mask = (q_25.index >= current_date) & (q_25.index <= month_ahead)
    
    # Extract week numbers from datetime index
    week_numbers = q_25.index.isocalendar().week
    
    # Plot
    plt.figure(figsize=(14, 6))
    
    # Forecast bars (Max Revenue - stacked on Min)
    plt.bar(
        week_numbers[forecast_mask],
        iqr[forecast_mask],
        bottom=q_25[forecast_mask],
        width=0.8,
        color='lightgreen',
        alpha=1.0,
        label='Forecast Revenue (75% Quantile)'
    )
    
    # Forecast bars (Min Revenue)
    plt.bar(
        week_numbers[forecast_mask],
        q_25[forecast_mask],
        bottom=0,
        width=0.8,
        color='green',
        alpha=1.0,
        label='Forecast Revenue (25% Quantile)'
    )
    
    # Historical bars
    plt.bar(
        week_numbers[historical_mask],
        q_25[historical_mask],
        bottom=0,
        width=0.8,
        color='orange',
        alpha=1.0,
        label='Realized Revenue'
    )
    
    # Formatting
    plt.title(f"Weekly {name}: Realized vs Forecast (25–75% Range)")
    plt.xlabel("Week Number")
    plt.ylabel(f"{name} ({unit})")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.xticks(week_numbers, week_numbers)  # Set week numbers as tick labels
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300)
    plt.close()
    buf.seek(0)
    return buf