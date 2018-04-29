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
	if len(ticker)<10:
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
cur.execute("""SELECT ticker,shares,target_price FROM fmi.portfolio;""")
portfolio=cur.fetchall()

####################################################
###Pull Quandl Price information for each ticker and send it to database#########
###################################################
for ticker,shares,target_price in portfolio:
    price=quandl_adj_close(ticker)
    value=shares*price
    cur.execute("""UPDATE fmi.portfolio set price=%s,value=%s where ticker=%s;""", (price, value, ticker))
    conn.commit()
    #Insert calculated expected return
    exp_return=round((target_price-price)/float(price),2)
    exp_value=(target_price*shares)
    print(exp_return)
    cur.execute("""UPDATE fmi.portfolio set exp_return=%s,exp_value=%s where ticker=%s;""", (exp_return,exp_value,ticker))
    conn.commit()

#####################################################
#####Log Portfolio Value data and SNP500 data to database############
#####################################################
cur.execute("""SELECT SUM(value) as total FROM fmi.portfolio;""")
portfoliovalues=cur.fetchall()
for row in portfoliovalues:
    portfoliovalue=row
snpvalue=quandl_adj_close("AAPL")
now=datetime.datetime.now()
currentdate=now.strftime("%Y-%m-%d")

cur.execute("""INSERT INTO fmi.portfoliohistory (date,name,value) VALUES (%s,'Portfolio',%s);""", (currentdate,portfoliovalue))
conn.commit()
cur.execute("""INSERT INTO fmi.portfoliohistory (date,name,value) VALUES (%s,'snp500',%s);""", (currentdate,snpvalue))
conn.commit()



cur.close()
conn.close()
