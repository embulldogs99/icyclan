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
from mmduprem import mmduprem


###########################################################


def barchart(ticker):
    with requests.Session() as c:
        u='https://www.barchart.com/stocks/quotes/'+ticker
        x=c.get(u)
        x=BeautifulSoup(x.content, "html.parser")
        titles=x.find_all()
        titles=str(titles)
        s=titles[titles.find("dailyLastPrice")+17:titles.find("dailyLastPrice")+17+20].replace('"','').split(",")
        if ticker="GOOG":
            s=float(s[0]+s[1])
        else:
            s=float(s[0])
        return s

#############################################################################
############## Pull Current Portfolio and Obtain Tickers  ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()
cur.execute("""SELECT ticker,shares,target_price FROM fmi.portfolio where ticker<>'CASH';""")
portfolio=cur.fetchall()

####################################################
###Pull Quandl Price information for each ticker and send it to database#########
###################################################
for ticker,shares,target_price in portfolio:
    price=barchart(ticker)
    value=round(shares*float(price),2)
    cur.execute("""UPDATE fmi.portfolio set price=%s,value=%s where ticker=%s;""", (price, value, ticker))
    conn.commit()
    #Insert calculated expected return
    exp_return=round((target_price-price)/float(price),2)
    exp_value=(target_price*shares)
    cur.execute("""UPDATE fmi.portfolio set exp_return=%s,exp_value=%s where ticker=%s;""", (exp_return,exp_value,ticker))
    conn.commit()

cur.close()
conn.close()
