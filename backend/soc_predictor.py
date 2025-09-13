import pandas as pd
import pypsa

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
    current_date + pd.Timedelta(days=7)

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