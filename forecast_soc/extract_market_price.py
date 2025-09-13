"""
This is a script that merges all of the SMARD_market_price data into one. 
Its not nessesary to run this script once you already have market_price.csv
"""
import pandas as pd

def extract_market_price(years):
    """
    Extracts and processes electricity market price data for Germany/Luxembourg 
    from CSV files for the specified years.

    Parameters:
    -----------
        years (list of int): List of years to load data for 
                             (e.g., [2020, 2021, 2022]).
    """

    results = pd.DataFrame()
    for year in years:
        market_price = pd.read_csv(
            f"forecast_soc/SMARD_market_price_{year}.csv",
            sep=';',
            decimal=',',           # If numbers use comma as decimal point
            parse_dates=True,      # If there are date columns
            dayfirst=True          # If dates are in DD.MM.YYYY format
        )
        market_price["Datum von"] = pd.to_datetime(market_price["Datum von"], format="%d.%m.%Y %H:%M")
        market_price["Datum bis"] = pd.to_datetime(market_price["Datum bis"], format="%d.%m.%Y %H:%M")
        
        de_price = market_price[["Datum von","Deutschland/Luxemburg [€/MWh] Originalauflösungen"]]
        de_price.columns = ["DE Electricity Market",f"market_price_{year}"]
        de_price = de_price.set_index("DE Electricity Market")
        
        # Drop leap days (Feb 29)
        de_price = de_price[~((de_price.index.month == 2) & (de_price.index.day == 29))]

        # ✅ Reset the year to 2025 for all timestamps
        de_price.index = de_price.index.map(lambda dt: dt.replace(year=2025))

        # remove duplicate index
        de_price = de_price.groupby(de_price.index).mean()

        results = pd.concat([results,de_price], axis = 1)

    # Fill nan values
    results = results.interpolate(method="linear")
    
    return results

if __name__ == "__main__":
    years = [2019, 2020, 2021, 2022, 2023, 2024]

    market_price = extract_market_price(years)
    market_price_25 = extract_market_price([2025])

    market_price = pd.concat([market_price,market_price_25], axis=1)

    market_price.to_csv("forecast_soc/market_price.csv")