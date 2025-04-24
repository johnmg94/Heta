# fetch_data.py
# from fredapi import Fred
import pandas as pd
from flask import jsonify
import requests
import json
from run_sql import run_query
import os
from dotenv import load_dotenv
import re
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


def fetch_from_fred(table_name):
    series_id = table_name
    fred_api_key = os.environ.get('FRED_API_KEY')
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={fred_api_key}&file_type=json"

    response = requests.get(url)
    if response.status_code == 200:
        py_obj = response.json()["observations"]
    if response.status_code == 200:
        py_obj = json.loads(response.text)
        df_fred = pd.DataFrame(py_obj)
        df_fred["series_id"] = table_name

        # Clean and transform data
        df_fred.dropna(inplace=True)
        df_fred["id"] = df_fred["id"].astype(int)
        df_fred["date"] = pd.to_datetime(df_fred["date"], errors='coerce').dt.date
        df_fred["value"] = df_fred["value"].astype(float)
        df_fred.drop(columns=['realtime_start', 'realtime_end'], errors='ignore', inplace=True)

    return df_fred

def fetch_from_treasury(treasury):
    # Treasury logic here
    return treasury

# BOMTVLM133S
def fetch_series(url, keywords, view_series):

    print("URL: ", url)
    try:
        r = requests.get(url)
    except Exception as e:
        print("Error: ", str(e))
    if r.status_code == 200:
        if view_series != False:
            # print("Blah")
            json_item = json.loads(r.text)
            try:
                json_item = json_item["observations"]
            except:
                print("'observations' key does not exist on json_item.")
                return jsonify(json_item)
            df = pd.DataFrame(json_item)
            count = 1
            # print(df.head())
            for index in range(len(df)):
                # if count < 5:
                    # print(index)
                    # print("COUNT", count)
                df.loc[index, 'id'] = str(index)
                # count+=1
            df = df.to_json(orient = "records")
            json_load = json.loads(df)
            # json_load_named = {res : json_load }
            response = jsonify(json_load)
            # json_out = df.to_json()
            return response
        else:
            returned_json = r.text
            json_item = json.loads(returned_json)
            if json_item != None:
                # for item in dict_item
                
                return jsonify(json_item)
            else:
                response = { 'response_status':'Your Query Combination Returned No Results.' }
                return jsonify(response)
    else:
        status_code = { 'status_code_error': str(r.status_code)}
        return jsonify(status_code)


def build_url(keywords_str):

    # Split the input string into individual keywords using commas or whitespace
    keywords = re.split(r'[,\s]+', keywords_str.strip())
    cleaned_keywords = []
    for keyword in keywords:
        # Remove special characters, keeping only alphanumeric characters
        cleaned = re.sub(r'[^A-Za-z0-9]', '', keyword)
        if cleaned:
            cleaned_keywords.append(cleaned)
    
    # Join the cleaned keywords with '+'
    joined_keywords = '+'.join(cleaned_keywords)
    
    # Append the API key to the URL
    keywords = str(joined_keywords) 
    return keywords

