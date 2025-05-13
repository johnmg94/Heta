from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from
from flask_cors import CORS
import os
import pandas as pd
import psycopg2
import pickle
import matplotlib as plt
import json
from store_data import DBStart, DataSeries
from parser import build_url
import requests
from dotenv import load_dotenv
import hashlib
import jwt
import datetime
from store_data import store_data
from run_sql import run_query, engine, table_names
from plot_data import plot_series
from regression_analysis import run_regression
from db.db_functions import db_insert
from fetch_data  import fetch_series, build_url, fetch_from_fred, fetch_from_treasury

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
            

@app.route('/get_series', methods=['GET', 'POST'])
# If this URL is accessed arbitrarily, it will attempt to make a connection to the db which is not correct. There needs to be some form of authentication

def get_series():
    """
    Fetches a time series from the database if available.
    Otherwise, fetches it from an external API, stores it in the DB, then returns it.
    TODO: Add authentication to secure this route.
    """

    # Load environment variables
    load_dotenv()
    user = os.environ.get('POSTGRES_USERNAME')
    password = os.environ.get('POSTGRES_PASSWORD')

    # Get query parameter
    table_name = str(request.args.get('query'))
    subscription = str(request.args.get('subscription'))
    
    print("Table name: ", table_name)
    print("Subscription name:", subscription)

    # Database connection
    conn = psycopg2.connect(
        dbname="Heta",
        user=user,
        password=password,
        host="localhost",  # Change if remote
        port="5432"
    )
    cur = conn.cursor()

    # Validate table name to avoid SQL injection!
    if subscription.lower() not in ["fred", "treasury"]:
        return "Invalid subscription/table name", 400
    
    # Query the correct table for the series
    select_query = f"SELECT * FROM {subscription} WHERE series_id LIKE %s"
    results = []
    try:
        cur.execute(select_query, (table_name,))
        results = cur.fetchall()
    except Exception as e:
        print("Query Failed: ", e)
        conn.rollback()

    # If series exists in DB, return it as JSON
    # Code assumes table format of FRED
    if results:
        if subscription == "fred":
            df = pd.DataFrame(results, columns = ['id', 'series_id', 'date', 'value'])
            return jsonify(json.loads(df.to_json(orient="records", date_format="iso")))
        # This part likely isn't correct. Check format of treasury api
        elif subscription == "treasury":
            df = pd.DataFrame(results)
            return jsonify(json.loads(df.to_json(orient="records", date_format="iso")))
    
    # If series is not found, attempt to fetch from local API endpoint
    try:
        if subscription == "fred":
            df = fetch_from_fred(table_name)
        elif subscription == "treasury":
            df = fetch_from_treasury(table_name)
        else:
            return f"Unsupported subscription: {subscription}", 400
        # Prepare insert query dynamically
        columns = df.columns.tolist()
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO FRED ({', '.join(columns)}) VALUES ({placeholders})"

        data = [tuple(row) for row in df.itertuples(index=False, name=None)]

        # Insert new records into DB
        try:
            cur.executemany(insert_query, data)
            conn.commit()

            # Re-query the DB for the newly inserted data
            cur.execute(select_query, (table_name,))
            results = cur.fetchall()

            if results:
                df = pd.DataFrame(results, columns=['id', 'series_id', 'date', 'value'])
                return jsonify(json.loads(df.to_json(orient="records", date_format="iso")))
            else:
                return "Data inserted but not retrievable", 500

        except Exception as e:
            print("Data insertion failed:", e)
            conn.rollback()
            return "Error inserting new series", 500

    except Exception as e:
        print("External API fetch failed:", e)
        return "Error fetching from external API", 500

    return "Series not found and fetch failed", 404

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
    # Query Parameters:
    # - param1 (str): The first parameter. Default is 'None'.
    # - param2 (int): The second parameter. Default is 'None'.

    # Returns:
    # - JSON object containing the values of param1 and param2.

    # Example:
    # /example?param1=hello&param2=123

    # """


def search_data():
    # if subscription == "FRED":
        try:
            api_key = os.environ.get('FRED_API_KEY')
        except Exception as e:
            print(e)
        try:
            series = str(request.args.get('query'))
            print(series)
        except Exception as e:
            print(str(e))
        if request.method == 'GET':
            # db_init = DBStart()
            api_key = '&api_key=' + str(api_key) + '&file_type=json'
            base_url = 'https://api.stlouisfed.org/fred/series/search?search_text='
            keywords = build_url(series)
            url = str(base_url) + str(keywords) + str(api_key)
            print("Keywords: ", keywords)
            # print("Base URL", str(base_url))
            # print("Keywords", str(keywords))
            view_series = False
            fetch_data = fetch_series(url, keywords, view_series)
            return fetch_data

    # elif subscription == "Treasury":
    #     try:
    #         test = "Test"
    #     except Exception as e:
    #         print(e)
    # elif subscription == "EIA":
    #     try:
    #         test_1 = "Test"
    #     except Exception as e:
    #         print(e)

 
# Also this function will run even if the realtimestart date exists. I need to store the realtime_start date and the query in a place where a new request won't fire if those two things exist and match the incoming query
# @app.route('/search_series?query=<query>}', methods=['POST'])
# def get_series_options(query):
#     if request.method == 'POST':
#         result = search_series(query)
#         df = result['df_object']
#         store_data(df)



        

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

# This function requires keywords to be passed in 
# 
# 


        
if __name__ == '__main__':
    app.run(debug=True)
