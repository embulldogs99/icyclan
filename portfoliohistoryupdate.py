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


def yahoopepuller(ticker):
	with requests.Session() as c:
		u="http://finance.yahoo.com/quote/"+ticker+"?p=" + ticker
		x=c.get(u)
		x=BeautifulSoup(x.content)
		titles=x.find_all()
		titles=str(titles)
		s=titles.find("PE_RATIO-value")
		pe=titles[s:s+1000]
		sn=pe.find("react-text")
		pe=pe[sn+17:sn+24]
		pe=pe.replace(">","").replace("!","").replace("<","")
		try:
			pe=float(pe)
		except:
			pe=0
		return pe


def quandl_snp500():
    with requests.Session() as c:
        u='https://www.barchart.com/stocks/quotes/$SPX'
        x=c.get(u)
        x=BeautifulSoup(x.content, "html.parser")
        print(x)
        titles=x.find_all()
        titles=str(titles)
        s=x[titles.find("dailyLastPrice"):titles.find("dailyLastPrice")+10]
        print(s)


quandl_snp500()

def quandl_nasdaq():
    now=datetime.datetime.now()
    currentdate=now.strftime("%Y-%m-%d")
    data=quandl.get('NASDAQOMX/XQC', start_date=currentdate, end_date=currentdate)
    print(data)

#############################################################################
############## Pull Current Portfolio and Obtain Tickers  ###################
# conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
# cur = conn.cursor()
# cur.execute("""SELECT SUM(value) as total FROM fmi.portfolio;""")
# portfoliovalues=cur.fetchall()
# for row in portfoliovalues:
#     portfoliovalue=row
# snpvalue=quandl_snp500()
# nasdaqvalue=quandl_nasdaq()
# now=datetime.datetime.now()
# currentdate=now.strftime("%Y-%m-%d")
#
# cur.execute("""INSERT INTO fmi.portfoliohistory (date,portfolio,snp,nasdaq) VALUES (%s,%s,%s,%s);""", (currentdate,portfoliovalue,snpvalue,nasdaqvalue))
# conn.commit()
#
#
#
#
# cur.close()
# conn.close()
