# fetch_data.py
# from fredapi import Fred
import pandas as pd
from flask import jsonify
import requests
import json
from run_sql import run_query
import os
from dotenv import load_dotenv

api_key = os.environ.get('FRED_API_KEY')

# https://api.stlouisfed.org/fred/release/series?release_id=51&api_key=&file_type=json
# https://fredaccount.stlouisfed.org/apikey?api_key=
# Replace with your actual FRED API key
# FRED_API_KEY = 'YOUR_FRED_API_KEY'
# fred = Fred(api_key=FRED_API_KEY)
# example series id: 51

# https://api.stlouisfed.org/fred/release/series?release_id=51&api_key=&file_type=json

# https://api.stlouisfed.org/fred/series/observations?series_id=5BOMTVLM133Sapi_key=&file_type=json

# https://api.stlouisfed.org/fred/series/observations?series_id=GNPCA&api_key=&file_type=json

# BOMTVLM133S

def fetch_series(series_id):
    r = requests.get('https://api.stlouisfed.org/fred/series/observations?series_id=' + str(series_id) + '&api_key=' + str(api_key) + '&file_type=json')
    returned_json = r.text
    dict_item = json.loads(returned_json)
    obs = dict_item['observations']
    # earliest_date = obs.
    df = pd.DataFrame(obs)

    # Creating a new column called id which indexes all of the rows
    df['id'] = range(len(df))
    df_new = pd.DataFrame(columns = ['id','value'])
    df_new['id'] = df['id']
    df_new['value'] = df['value']
    print(df.columns)

    return df

# x = fetch_series('GNPCA')

if __name__ == '__main__':
    gdp_df = fetch_series('GDP')
    # series_options = search_series('gdp')
    # print(series_options)


# The following code returns realtime_date and the rest of the df separately:
# def search_series(series):
#         try:
#             r = requests.get('https://api.stlouisfed.org/fred/series/search?search_text=' + str(series) + '&api_key=&file_type=json')
#         except Exception as e:
#             print("Error", + str(e))

#         if r.status_code == 200:   
#             returned_json = r.text
#         dict_item = json.loads(returned_json)

#         try:
#             realtime_date = dict_item['realtime_start']
#             return { 'realtime_date' : realtime_date}
#         except Exception as e:
#              print("Did not get realtime_start: ", e)
             
#         try:
#             seriess = dict_item['seriess']
#         except Exception as e:
#              print("Dict item does not exist: ", e)
#         if (seriess):
#             df = pd.DataFrame(seriess)
#             df['id'] = range(len(df))
#             df_new = pd.DataFrame(columns = ['id'])
#             df_new['id'] = df['id']
#             return { 'df_object' : df }
