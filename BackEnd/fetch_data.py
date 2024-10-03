# fetch_data.py
# from fredapi import Fred
import pandas as pd
import requests
import json
# https://api.stlouisfed.org/fred/release/series?release_id=51&api_key=1648501a052f4e7475b93f991dc4380d&file_type=json
# https://fredaccount.stlouisfed.org/apikey?api_key=1648501a052f4e7475b93f991dc4380d
# Replace with your actual FRED API key
# FRED_API_KEY = 'YOUR_FRED_API_KEY'
# fred = Fred(api_key=FRED_API_KEY)
# example series id: 51

# https://api.stlouisfed.org/fred/release/series?release_id=51&api_key=1648501a052f4e7475b93f991dc4380d&file_type=json

# https://api.stlouisfed.org/fred/series/observations?series_id=5BOMTVLM133Sapi_key=1648501a052f4e7475b93f991dc4380d&file_type=json

# https://api.stlouisfed.org/fred/series/observations?series_id=GNPCA&api_key=1648501a052f4e7475b93f991dc4380d&file_type=json

# BOMTVLM133S

def fetch_series(series_id):
    r = requests.get('https://api.stlouisfed.org/fred/series/observations?series_id=' + str(series_id) + '&api_key=1648501a052f4e7475b93f991dc4380d&file_type=json')
    returned_json = r.text
    dict_item = json.loads(returned_json)
    obs = dict_item['observations']
    df = pd.DataFrame(obs)
    df['id'] = range(len(df))
    df_new = pd.DataFrame(columns = ['id','value'])
    df_new['id'] = df['id']
    df_new['value'] = df['value']
    # df['value'] = pd.to_numeric(df['value'], errors='coerce')
    print(df_new.columns)
    print(df_new.head)
    # df.index.name = 'Date'
    # df = df.reset_index()
    return df

# x = fetch_series('GNPCA')

# Example usage
if __name__ == '__main__':
    gdp_df = fetch_series('GDP')
    print(gdp_df.head())
