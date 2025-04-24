from run_sql import run_query, table_names
import hashlib
import random
import string
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Session
from sqlalchemy import MetaData
from sqlalchemy import Column
from sqlalchemy import Float

Base = declarative_base()
class Model(Base):
    def __init__(self):
        print("init")
        self.models_table = "Models"
        models_created_flag = False
        self.models_table_series = "Models_Series"
        tables = table_names()
        for item in tables:
            if item == self.models_table:
                models_created_flag = True
                break
        if models_created_flag == False:
            create_table = run_query(f'CREATE {self.models_table}')
        
    def create_model(self, user_id, model_name):
        random_component = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) 
        model_exists_check = True              
        try:
            while model_exists_check == True:
                combined_string = f"{user_id}-{model_name}-{random_component}"
                model_id_gen = hashlib.sha256(combined_string.encode()).hexdigest()
                model_exists_query = run_query(f'SELECT model_id FROM {self.models_table} WHERE model_id == {model_id_gen}')
                if (model_exists_query):
                    insert_data = run_query(f'INSERT INTO {self.models_table} (model_id_gen, user_id, model_name)')
                    model_exists_check = False
                    return model_id_gen             
        except Exception as e:
            err = "Table INSERT did not finish: ", str(e)
            return { "error" : err}
        
    def query_model(self, user_id, model_name):
        query_model = run_query(f'SELECT user_id from self.models_table WHERE user_id == {user_id}')
        # Check this for correctness
        if query_model == None:
            return f'Model does not exist.'
        return query_model
        # Route side of the app needs to convert to json
    
    # This function updates the model with new series_id's
    def update_model(user_id,model_id,series_id_list = []):
        print("Blah")

    def add_series(user_id, model_name,series_id_list = []):
        print("Blah")

