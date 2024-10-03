# app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
import os
import pandas as pd
from fetch_data import fetch_series
from store_data import store_data
from run_sql import run_query, engine, table_names
from plot_data import plot_series
from regression_analysis import run_regression
# import statsmodels.api as sm
import pickle
import matplotlib as plt

app = Flask(__name__)
cors = CORS(app)

# Ensure directories exist
os.makedirs('static/plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

@app.route('/')
def home():
    test = { "name" : "hello_world"}
    return test

@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    if request.method == 'POST':
        # getting the series from the textbox
        series_id = request.form['series_id']
        df = fetch_series(series_id)
        store_data(df, series_id.lower())

        # return redirect(url_for('home'))
    # return render_template('fetch.html')

@app.route('/view_series', methods=['GET'])
def view_series():
    if request.method == 'GET':
        table_name = 'gnpca'
        df = run_query(f'SELECT * FROM {table_name}')
        json_out = df.to_json()
        return json_out
        

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
