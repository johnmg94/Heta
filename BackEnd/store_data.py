# store_data.py
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
# table_name = table_name
class DataSeries(Base):
    __tablename__ = "table_name"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(30), nullable=True)
    value = Column(Float, nullable=True)


class DBStart():
    def __init__(self):
        self.metadata_obj = MetaData()

    def verify_table(self, table_name):
        table_exists_flag = False
        metadata_obj = MetaData()
        for t in metadata_obj.sorted_tables:
             if str(t) == str(table_name):
                table_exists_flag = True
                return table_exists_flag
                break
        if table_exists_flag == False:
            return table_exists_flag    

# class SearchQueries():
#     __tablename__ = "past_search_queries"
#     id = Column(Integer, primary_key=True)
#     date = Column(DateTime(30), nullable=True)
#     value = Column(Float, nullable=True)
#     series_id = Column()

# class SeriesDescs():

def store_data(df, table_name):
    fail_flag = False
    try:
        df.to_sql(table_name, engine, if_exists='fail', index=False)
    except Exception as e:
        print("Table already exists: " + str(e))
        fail_flag = True
        return fail_flag

if __name__ == '__main__':
        engine = create_engine('sqlite:///economic_data.db')
        Base.metadata.create_all(engine)
        session = Session(engine)
        data_series = DataSeries()

        session.add_all()


    # from fetch_data import fetch_series, search_series
    # gdp_df = fetch_series('GDP')
    # store_data(gdp_df, 'gdp')