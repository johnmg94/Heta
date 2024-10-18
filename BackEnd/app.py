# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from
from flask_cors import CORS
import os
import pandas as pd
from fetch_data import fetch_series
from store_data import store_data
from run_sql import run_query, engine, table_names
from plot_data import plot_series
from regression_analysis import run_regression
import pickle
import matplotlib as plt
import json
from store_data import DBStart, DataSeries
from parser import build_url
import requests
from dotenv import load_dotenv

app = Flask(__name__)
api = Api(app)
cors = CORS(app)

# Ensure directories exist
os.makedirs('static/plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

#Configuring Swagger
app.config['SWAGGER'] = {
    'title' : 'My API',
    'uiversion' : 3
}

swagger = Swagger(app)

@app.route('/')
def home():
    test = { "name" : "hello_world"}
    return test

@app.route('/query_db', methods=['GET', 'POST'])
def query_db():
    if request.method == 'GET':
        try:
            print("here")
            res = str(request.args.get('series'))
            print(res)
        except Exception as e:
            print(e)

        try:    
            df = run_query(f'SELECT * from {res}')
        except Exception as e:
            err = "Table SELECT did not finish: ", str(e)
            return { "error" : err}

        columns = df.columns
        json_out = df.to_json(orient = "records")
        json_load = json.loads(json_out)
        json_load_named = {res : json_load }
        response = jsonify(json_load_named)
        if (response):
            return response
        else:
            return { "Response" : "None" }


@app.route('/search_data', methods=['GET', 'POST'])
def fetch():
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
        base_url = 'https://api.stlouisfed.org/fred/series/search?search_text='
        keywords = build_url(series)
        fetch_data = fetch(base_url,keywords,api_key)
        return fetch_data
 
# Also this function will run even if the realtimestart date exists. I need to store the realtime_start date and the query in a place where a new request won't fire if those two things exist and match the incoming query
# @app.route('/search_series?query=<query>}', methods=['POST'])
# def get_series_options(query):
#     if request.method == 'POST':
#         result = search_series(query)
#         df = result['df_object']
#         store_data(df)


@app.route('/view_series', methods=['GET'])
    # Example route to demonstrate how to document Flask routes.

    # Query Parameters:
    # - param1 (str): The first parameter. Default is 'None'.
    # - param2 (int): The second parameter. Default is 'None'.

    # Returns:
    # - JSON object containing the values of param1 and param2.

    # Example:
    # /example?param1=hello&param2=123

    # """

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
        fetch_data = fetch(base_url,keywords,api_key)
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
        

@app.route('/graph', methods=['GET', 'POST'])
def graph():
    if request.method == 'POST':
        table_name = request.form['table_name']
        df = run_query(f'SELECT * FROM {table_name}')
        plot_series(df, 'Value', table_name.upper(), f'{table_name.upper()} Over Time')
        plot_path = f'plots/{table_name}.png'
        plt.savefig(f'static/{plot_path}')
        plt.close()
        return render_template('graph.html', plot_image=plot_path)
    tables = table_names()
    return render_template('graph_select.html', tables=tables)

@app.route('/sql', methods=['GET', 'POST'])
def sql():
    result = None
    if request.method == 'POST':
        query = request.form['query']
        try:
            result_df = run_query(query)
            result = result_df.to_html(classes='data')
        except Exception as e:
            result = f"Error: {e}"
    return render_template('sql.html', result=result)

@app.route('/model', methods=['GET', 'POST'])
def model():
    summary = None
    if request.method == 'POST':
        dependent_var = request.form['dependent_var']
        independent_vars = request.form.getlist('independent_vars')
        table_name = request.form['table_name']
        df = run_query(f'SELECT * FROM {table_name}').dropna()
        model = run_regression(df, dependent_var, independent_vars)
        summary = model.summary().as_html()
        # Save the model
        model_name = request.form['model_name']
        with open(f'models/{model_name}.pkl', 'wb') as f:
            pickle.dump(model, f)
    tables = table_names()
    columns = {}
    for table in tables:
        df = run_query(f'SELECT * FROM {table} LIMIT 1;')
        columns[table] = df.columns.tolist()
    return render_template('model.html', summary=summary, tables=tables, columns=columns)

def fetch(base_url, keywords, api_key):
    url = str(base_url) + str(keywords) + str(api_key)
    try:
        r = requests.get(url)
    except Exception as e:
        print("Error: ", str(e))
    if r.status_code == 200:
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
        
if __name__ == '__main__':
    app.run(debug=True)
