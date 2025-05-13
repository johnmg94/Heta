# app.py
import os
import pandas as pd
import matplotlib as plt
import json
import requests
from dotenv import load_dotenv

def view_series():
    print('here')
    try:
        api_key = os.environ.get('FRED_API_KEY')
    except Exception as e:
        print(str(e))
    try:
        series = str(request.args.get('series'))
    except Exception as e:
        print(str(e))
    if request.method == 'GET':
        db_init = DBStart()
        api_key = '&api_key=' + str(api_key) + '&file_type=json'
        base_url = 'https://api.stlouisfed.org/fred/series/observations?series_id='
        keywords = build_url(series)
        print(str(base_url) + str(api_key) + str(keywords))
        view_series = True
        fetch_data = fetch(base_url,keywords,api_key, view_series)
        print(fetch_data)
        return fetch_data
            
        # if request.method == 'GET':
        #     table_name = 'gnpca'
        #     df = run_query(f'SELECT * FROM {table_name}')
        #     columns = df.columns
        #     json_out = df.to_json(orient = "records")
        #     json_load = json.loads(json_out)
        #     json_load_named = {table_name : json_load }
        #     response = jsonify(json_load_named)
        #     return response