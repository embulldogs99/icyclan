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


###########################################################
##########################################################
######## Used QUANDL Functions #########################

quandl.ApiConfig.api_key = 'omQiMysF2NQ1B-xZEJBk'

def quandl_stocks(symbol, start_date=(2010, 1, 1), end_date=None):
    query_list = ['WIKI' + '/' + symbol + '.' + str(k) for k in range(11, 12)]
    start_date = datetime.date(*start_date)
    if end_date:
        end_date = datetime.date(*end_date)
    else:
        end_date = datetime.date.today()
    return quandl.get(query_list,
            returns='pandas',
            start_date=start_date,
            end_date=end_date,
            collapse='daily',
            order='asc'
            )

def quandl_adj_close(ticker):
	if len(ticker)<5:
		data=pd.DataFrame(quandl_stocks(ticker))
		#data=data[len(data)-1:]
		data=data.tail(1)
		data=str(data.max()).split(' ')[7:8]
		data=re.split(r'[`\-=;\'\\/<>?]', str(data))
		data=data[1]
		try:
			data=float(data)
		except:
			data=int(0)
		price=int(round(data,0))
		if price>1:
			return price


#############################################################################
############## Pull Current Portfolio and Obtain Tickers  ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()
cur.execute("""SELECT ticker,shares FROM fmi.portfolio;""")
portfolio=cur.fetchall()
print("gathered portfolio")


####################################################
###################################################
for ticker,shares in portfolio:
    price=quandl_adj_close(ticker)
    value=shares*price
    cur.execute("UPDATE fmi.portfolio set price=%s,value=%s where ticker=%s)", (price, value, ticker))
    conn.commit()
    # close the communication with the PostgreSQL

cur.close()
conn.close()
