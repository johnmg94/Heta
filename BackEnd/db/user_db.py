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
class User(Base):
    def __init__(self):
        print("init")
        self.user_table = "Users"
        users_created_flag = False
        self.user_login = False
        self.user_id = ''
        # self.users_table_series = "Models_Series"
        tables = table_names()
        for item in tables:
            if item == self.models_table:
                models_created_flag = True
                break
        if users_created_flag == False:
            create_table = run_query(f'CREATE {self.models_table}')
    
    def auth_user(self, user_id, hashed_password):
        try:
            user_exists_query = run_query(f'SELECT user_id FROM {self.user_table} WHERE user_id == {user_id}')
        except Exception as e:
            print("Username doesn't exist", str(e))
        try:
            # To DO; Query table once for user and again for both?
            hashed_password_query = run_query(f'SELECT hashed_password,user_id FROM {self.user_table} WHERE user_id = {user_id} AND hashed_password = {hashed_password}')
            # To Do: Is this right?
            self.user_login = True
            return { "auth_msg" : "Successfully logged in" }
        
        except Exception as e:
            return { "auth_msg" : "Auth Failed. Please Try Again"}

    def create_user (self, user_id, user_first, user_last, password):
        try:
            # combined_string = f"{user_id}-{model_name}-{random_component}"
            # model_id_gen = hashlib.sha256(combined_string.encode()).hexdigest()
            user_exists_query = run_query(f'SELECT user_id FROM {self.user_table} WHERE user_id == {user_id}')
            if (user_exists_query == None):
                return { "user_exists": "User Already Exists"}
            else:
                hashed_password = hashlib.sha256(password.encode().hexdigest)
                insert_data = run_query(f'INSERT INTO {self.users_table} ({user_id}, {user_first}, {user_last}, {hashed_password})')
                return str(insert_data)
            # { 
            #             "user_creation_succces": "User Created Successfully",
            #             "user_id": str(user_id),
            #             "user_fist":  str(user_first),
            #             "user_last": str(user_last)
            #             }  
                   
        except Exception as e:
            err = "User Creation did not finish: ", str(e)
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

