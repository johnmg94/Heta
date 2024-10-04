# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from flask_cors import CORS
import os
import pandas as pd
from fetch_data import fetch_series, search_series
from store_data import store_data
from run_sql import run_query, engine, table_names
from plot_data import plot_series
from regression_analysis import run_regression
# import statsmodels.api as sm
import pickle
import matplotlib as plt
import json
from store_data import DBStart, DataSeries
from parser import build_url

app = Flask(__name__)
cors = CORS(app)

# Ensure directories exist
os.makedirs('static/plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

@app.route('/')
def home():
    test = { "name" : "hello_world"}
    return test

@app.route('/fetch_data/<series>', methods=['GET', 'POST'])
def fetch(series):
    series = str(series)

    if request.method == 'POST':
        db_init = DBStart()
        # return_flag = db_init.verify_table(series)

        #If the return_flag is true that means the database exists, and so it is as simple as selecting the data from that table
        # if return_flag == True:
            # df = run_query(f'SELECT * FROM {series}')

        #If return flag is false, I want to check if the series requested exists in FRED:
        # elif return_flag == False:
        api_key = '&api_key=1648501a052f4e7475b93f991dc4380d&file_type=json'
        url = build_url(series, api_key)
        response = search_series(url)
        print("Searched Series Items:" , str(response))
        return response
            # with open ("temp.json", "w") as f:
            #     try:
            #         json.dumps(searched_series_items)
            #     except Exception as e:
            #         print("Error: ", str(e))

            # print("Searched_Series_Items:" , str(searched_series_items))
            # df = searched_series_items.df_object
            # df_json = df.to_json(orient = "records")
            # json_load = json.loads(df_json)
            # json_load_named = {table_name : json_load }
            # response = jsonify(json_load)
            
        
    if request.method == 'GET':
        # getting the series from the textbox
        series_id = request.form['series_id']
        df = fetch_series(series_id)
        store_data(df, series_id.lower())
# x = fetch('gdp')
        # return redirect(url_for('home'))
    # return render_template('fetch.html')


# Also this function will run even if the realtimestart date exists. I need to store the realtime_start date and the query in a place where a new request won't fire if those two things exist and match the incoming query
@app.route('/search_series?query=<query>}', methods=['POST'])
def get_series_options(query):
    if request.method == 'POST':
        result = search_series(query)
        df = result['df_object']
        store_data(df)

@app.route('/view_series', methods=['GET'])
def view_series():
    if request.method == 'GET':
        table_name = 'gnpca'
        df = run_query(f'SELECT * FROM {table_name}')
        columns = df.columns
        json_out = df.to_json(orient = "records")
        json_load = json.loads(json_out)
        json_load_named = {table_name : json_load }
        response = jsonify(json_load_named)
        return response
        

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

if __name__ == '__main__':
    app.run(debug=True)
