# fetch_data.py
# from fredapi import Fred
import pandas as pd
from flask import jsonify
import requests
import json
from run_sql import run_query

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

# Need to make this accept a dict
# This function should only accept input after being parsed from the build_url funciton in parser.py
def search_series(url):
        # print("Search Input: ", str(series))
        # base_url = 'https://api.stlouisfed.org/fred/series/search?search_text='
        # api_key = '&api_key=1648501a052f4e7475b93f991dc4380d&file_type=json'

        # if len(series) > 0:
        #     count = 1
        #     for item in range(len(series)):
        #         if count < len(series):
        #              base_url = base_url + str(series[item]) + '+'
        #         else:
        #             base_url = base_url + str(series[item])
        #     base_url = base_url + api_key
        #     print("Base Url: ", str(base_url))
        try:
            r = requests.get(url)
        except Exception as e:
            print("Error", + str(e))

        if r.status_code == 200:   
            returned_json = r.text
            json_item = json.loads(returned_json)
            dict_item = json_item['seriess']
            if dict_item != None:
                 return jsonify(dict_item)
            else:
                 response = { 'response_status':'Your Query Combination Returned No Results.' }
                 return jsonify(response)
        else:
             status_code = { 'status_code_error': str(r.status_code)}
             return jsonify(status_code)

        # df = pd.DataFrame(dict_item)
        # df['id'] = range(len(df))
        # df_new = pd.DataFrame(columns = ['id'])
        # df_new['id'] = df['id']
        # return { 'df_object' : df }

        # try:
        #     realtime_date = dict_item['realtime_start']
        #     return { 'realtime_date' : realtime_date}
        # except Exception as e:
        #      print("Did not get realtime_start: ", e)

        # try:
        #     seriess = dict_item['seriess']
        # except Exception as e:
        #      print("Dict item does not exist: ", e)
        # if (seriess):
        #     df = pd.DataFrame(seriess)
        #     df['id'] = range(len(df))
        #     df_new = pd.DataFrame(columns = ['id'])
        #     df_new['id'] = df['id']
        #     return { 'df_object' : df }

if __name__ == '__main__':
    gdp_df = fetch_series('GDP')
    # series_options = search_series('gdp')
    # print(series_options)


# The following code returns realtime_date and the rest of the df separately:
# def search_series(series):
#         try:
#             r = requests.get('https://api.stlouisfed.org/fred/series/search?search_text=' + str(series) + '&api_key=1648501a052f4e7475b93f991dc4380d&file_type=json')
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
