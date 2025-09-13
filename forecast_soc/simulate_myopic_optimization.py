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
    system_cost = n.objective / 1e6 # Mil €/a

    return state_of_charge, system_cost

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
    week_ahead = current_date + pd.Timedelta(days=7)

    state_of_charge = pd.DataFrame()
    system_cost = {}
    
    for year in years:
        # Extract relevant slices
        recent_prices = market_price.loc[market_price.index <= day_ahead, f"market_price_{current_date.year}"]
        future_prices = market_price.loc[market_price.index > day_ahead, f"market_price_{year}"]
        
        # Combine them into one consistent Series
        market_price_series = pd.concat([recent_prices, future_prices]).sort_index()
        
        state_of_charge_year, system_cost_year = optimize_simple_model(market_price_series, **kwarg)

        state_of_charge = pd.concat([state_of_charge, state_of_charge_year], axis=1)
        system_cost[year] = system_cost_year

    return state_of_charge, system_cost

def plot_soc_forecast(state_of_charge, date):
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
        state_of_charge (pandas.DataFrame): DataFrame where each column represents 
                                             a simulation scenario, and the index is a datetime.
        date (str or pd.Timestamp): The starting date for the 7-day forecast window 
                                    (e.g., '2025-07-01').

    Returns:
        None. (Displays and saves the plot as 'state_of_charge_plot.png'.)
    """

    current_date = pd.to_datetime(date)
    day_ahead = current_date + pd.Timedelta(days=1)
    week_ahead = current_date + pd.Timedelta(days=7)

    # Cut the time series only for the next week
    state_of_charge = state_of_charge[current_date:week_ahead]

    # Calculate percentiles across columns for each timestamp
    q_0 = state_of_charge.min(axis=1)  # or .quantile(0.0)
    q_25 = state_of_charge.quantile(0.25, axis=1)
    q_37 = state_of_charge.quantile(0.375, axis=1)
    q_50 = state_of_charge.median(axis=1)
    q_62 = state_of_charge.quantile(0.625, axis=1)
    q_75 = state_of_charge.quantile(0.75, axis=1)
    q_100 = state_of_charge.max(axis=1)  # or .quantile(1.0)

    # Start plotting
    plt.figure(figsize=(14, 6))

    # Lightest area: min to max (0–100%)
    plt.fill_between(state_of_charge.index, q_0, q_100, color='black', alpha=0.2, label='0–100% range')

    # Medium area: 25–75%
    plt.fill_between(state_of_charge.index, q_25, q_75, color='black', alpha=0.4, label='25–75% range')

    # Darkest area: 37.5–62.5%
    plt.fill_between(state_of_charge.index, q_37, q_62, color='black', alpha=0.6, label='37.5–62.5% range')

    # median line
    plt.plot(state_of_charge.index, q_50, color='blue', linestyle='-', linewidth=2, label='Median SoC')

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
    plt.title("State of Charge Quantile Ranges")
    plt.xlabel("Time")
    plt.xlim(state_of_charge.index.min(), state_of_charge.index.max())
    plt.ylabel("State of Charge (MWh)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("state_of_charge_plot.png", dpi=300)  # Save to file
    plt.show()

if __name__ == "__main__":
    # You can set whatever capacity you want
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

    # run this on the main repo level to work
    market_price = pd.read_csv("forecast_soc/market_price.csv", parse_dates=True, index_col=0)
    years = [2019, 2020, 2021, 2022, 2023, 2024]
    
    # We want to connect this date selection to the frontend. The maximul limit for this date is 2025-09-05
    date = "2025-09-01"

    state_of_charge, system_cost = simulate_myopic_optimization(
        market_price, 
        years, 
        date, 
        **kwarg
    )

    # system_cost are currently not in use. Just for testing.

    state_of_charge.to_csv("forecast_soc/state_of_charge.csv")

    plot_soc_forecast(state_of_charge, date)
