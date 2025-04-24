from dotenv import load_dotenv
import os
import pandas as pd
import re
import sqlalchemy
from sqlalchemy import create_engine
import json
from sqlalchemy import text
import psycopg2

# Drop table
# Create table
# Insert values into table from df

def db_insert(search_df, table_name):
    load_dotenv()
    user = os.environ.get('POSTGRES_USERNAME')
    password = os.environ.get('POSTGRES_PASSWORD')
    # Define connection parameters
    conn = psycopg2.connect(
        dbname="Heta",
        user=user,
        password=password,
        host="localhost",  # Change if remote
        port="5432"
    )

    cur = conn.cursor()
    # cur.execute('''DROP TABLE ''' + str(table_name))
    arr = search_df.columns
    query_string = ''' CREATE TABLE IF NOT EXISTS ''' + str(table_name) + ''' (''' 
    count = 0
    end = len(arr)
    for item in arr:
        if count + 1 == end:
            query_string = query_string + item + " TEXT"
        else:
            if item == "group_popularity" or item == "popularity":
                query_string = query_string + item + " INT, "
            else:
                query_string = query_string + item + " TEXT, "
            count += 1
    query_string = query_string + ''' ); '''

    print(query_string)


    cur.execute(query_string)
    conn.commit()

    count = 0
    end = len(arr)
    insert_query = f"INSERT INTO '{table_name}' ("
    append_query = ''' \n VALUES ('''
    for item in arr:
        if count + 1 == end:
            insert_query = insert_query + item + ")"
            append_query = append_query + "%s);"
        else:
            insert_query = insert_query + item + ", "
            append_query = append_query + "%s,"
            count += 1
    insert_query = insert_query + append_query
    print(insert_query)

    data = [tuple(row) for row in search_df.itertuples(index=False, name=None)]
    print(f"Number of columns: {len(arr)}")
    print(f"Length of first row: {len(data[1])}")
    print(data[1])
    cur.executemany(insert_query, data[1:])
    conn.commit()
    cur.close()
    conn.close()