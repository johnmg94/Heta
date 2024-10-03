# store_data.py

from sqlalchemy import create_engine
import pandas as pd

# Create an SQLite database
engine = create_engine('sqlite:///economic_data.db')

def store_data(df, table_name):
    df.to_sql(table_name, engine, if_exists='replace', index=False)

# Example usage
if __name__ == '__main__':
    from fetch_data import fetch_series
    gdp_df = fetch_series('GDP')
    store_data(gdp_df, 'gdp')
