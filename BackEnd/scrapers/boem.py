import requests
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import sqlite3
import json
import csv
import re

class BOEM:
    def __init__(self): 
        # self.page_source = ''
        self.driver_config()
        # self.bot()
        # self.scrape_each_link()
        # self.text_parser_from_link()

    def driver_config(self):
        print("INIT")
        self.VINTED_LINK = "https://www.data.boem.gov/Well/API/Default.aspx"
        self.options = Options()
        self.options = Options()
        self.options.add_argument=("user-agent=[Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0]")
        self.driver = webdriver.Chrome(options = self.options)
        self.driver.get(self.VINTED_LINK)   

    def bot(self):
        count = 0

        # During sleep time, user needs to change the page size to 200
        sleep(20)

        # This  website has 277 pages containing records of API #'s

        page_source = self.driver.page_source
        html_parse(page_source)
        for page in range(2, 277):
            # Sleeping to give the new results time to load
            sleep(5)

            page_source = self.driver.page_source
            html_parse(page_source)

            try:
                self.driver.find_element(By.PARTIAL_LINK_TEXT, str(page)).click()

            except Exception as e:
                print("The driver did not find the 'next button' in the DOM and/or it wasn't clicked: ", e)

        self.driver.close()

def html_parse(page_source):
    #Find all td elements
    try:
        soup = BeautifulSoup(page_source, 'lxml')
        td_elements = soup.find_all("td", class_="dxgv")
    except Exception as e:
        print("No 'td' elmeents found:, e")
    
    trimmed_list = []
    for item in td_elements:
        trimmed_list.append(item.text.strip())
    
    new_list = []
    re_string = r'\d{12}$'
    new_index = 0
    for index,item in enumerate(trimmed_list):
        if re.match(re_string, item):
            new_index = index
            break

    outer_list = []
    count = 0
    for index, item_2 in enumerate(trimmed_list[new_index:]):
        new_list.append(item_2)    
        count += 1
        if count%18 == 0:
            outer_list.append(new_list)
            new_list = []
            count = 0

    with open ("td_file.txt", "a", encoding="utf-8") as f:
        for record in outer_list:
            f.write(str(record))
            f.write("\n")

    # def insert_to_db(self):
    #     #Connecting to sqlite
    #     conn = sqlite3.connect('WELL_API.db')

    #     #Creating a cursor object using the cursor() method
    #     cursor = conn.cursor()

    #     cursor.executemany('INSERT INTO VINTED VALUES (null,?,?)', self.links_textfile)

    #     conn.commit()
    #     conn.close()

    # def create_table(self):
    #     #Connecting to sqlite
    #     conn = sqlite3.connect('WELL_API.db')

    #     #Creating a cursor object using the cursor() method
    #     cursor = conn.cursor()

    #     # Creating table as per requirement
    #     sql ='''CREATE TABLE WELL_API(
    #         AUTO_ID INTEGER GENERATED ALWAYS AS IDENTITY,
    #         API_WELL_NUMBER INTEGER PRIMARY KEY,
    #         WELL_TYPE_CODE TEXT,
    #         WELL_NAME char(10),
    #         WELL_NAME_SUFFIX char(20),
    #         COMPANY_NAME char(50),
    #         STATUS_DATE date,
    #         STATUS_CODE char(10),
    #         FIELD_NAME char(10),
    #         SURFACE_LEASE_NUMBER(10) char(10),
    #         SURFACE_AREA char(5),
    #         SURFACE_BLOCK INTEGER,
    #         BOTTOM_LEASE_NUMBER char(10),
    #         BOTTOM_AREA char(5),
    #         BOTTOM_BLOCK INTEGER,
    #         SPUD_DATE DATE,
    #         TOTAL_DEPTH_DATE DATE,
    #         BH_TOTAL_MD INTEGER 
    #     )'''
    #     cursor.execute(sql)
    #     conn.commit()
    #     conn.close()

if __name__ == "__main__":
    x =BOEM()
    x.bot()