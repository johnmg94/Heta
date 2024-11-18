# run_sql.py
from sqlalchemy import create_engine, inspect
import pandas as pd

engine = create_engine('sqlite:///economic_data.db')

def run_query(query):
    with engine.connect() as conn:
        result = pd.read_sql_query(query, conn)
    return result

def table_names():
    # with engine.connect() as conn:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return tables

# Example usage
# if __name__ == '__main__':
#     query = 'SELECT * FROM gdp LIMIT 5;'
#     result_df = run_query(query)
#     print(result_df)

# x = table_names()
# print(x)