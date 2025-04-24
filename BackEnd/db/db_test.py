# from run_sql import run_query, table_names
import hashlib
import random
import string
from sqlalchemy import create_engine, Integer, String, MetaData, Column, Float, inspect, DateTime, ForeignKey
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
import pandas as pd


Base = declarative_base()
class UserTest(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String[50])
    last_name = Column(String[50])
    email = Column(String[50])


engine = create_engine('sqlite:///economic_data.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

new_user = UserTest(first_name='Jack', last_name='Grey',email='jkg@gmail.com')
session.add(new_user)
session.commit()

# inspector = inspect(engine)
users = session.query(UserTest).all()
for user in users:
    print(user.id , user.first_name, user.last_name, user.email)

session.close()

x = UserTest()

