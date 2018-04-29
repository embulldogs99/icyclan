import requests
import bs4
from bs4 import BeautifulSoup
import warnings
import time
import datetime
import json
import pandas as pd
import io
import re
import psycopg2
import quandl
from mmduprem import mmduprem

##################################
######## QUANDL Functions #########################

quandl.ApiConfig.api_key = 'omQiMysF2NQ1B-xZEJBk'

def quandl_price_pull(ticker):
    apistring='https://www.quandl.com/api/v3/datasets/WIKI/'+ticker+'.csv'
    s=requests.get(apistring).content
    data=pd.read_csv(io.StringIO(s.decode('utf-8')))
    data=data.tail(1)
    return data


#############################################################################
############## Pull Current Portfolio and Obtain Tickers  ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()
cur.execute("""SELECT SUM(value) as total FROM fmi.portfolio;""")
portfoliovalues=cur.fetchall()
for row in portfoliovalues:
    portfoliovalue=row
snpvalue=quandl_price_pull("AS500")
nasdaqvalue=quandl_price_pull("XQC")
now=datetime.datetime.now()
currentdate=now.strftime("%Y-%m-%d")

cur.execute("""INSERT INTO fmi.portfoliohistory (date,portfolio,snp,nasdaq) VALUES (%s,%s,%s,%s);""", (currentdate,portfoliovalue,snpvalue,nasdaqvalue))
conn.commit()




cur.close()
conn.close()
