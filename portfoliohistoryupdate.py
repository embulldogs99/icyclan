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
from mmduprem import portfoliohistoryduplicatedelete

##################################
######## QUANDL Functions #########################

quandl.ApiConfig.api_key = 'omQiMysF2NQ1B-xZEJBk'

def barchart_snp500():
    with requests.Session() as c:
        u='https://www.barchart.com/stocks/quotes/$SPX'
        x=c.get(u)
        x=BeautifulSoup(x.content, "html.parser")
        titles=x.find_all()
        titles=str(titles)
        s=titles[titles.find("dailyLastPrice")+17:titles.find("dailyLastPrice")+17+10].replace('"','').replace(",","")
        try:
            s=float(s)
            return s
        except:
            return 0

def barchart_nasdaq():
    with requests.Session() as c:
        u='https://www.barchart.com/etfs-funds/quotes/QQQ'
        x=c.get(u)
        x=BeautifulSoup(x.content, "html.parser")
        titles=x.find_all()
        titles=str(titles)
        s=titles[titles.find("dailyLastPrice")+17:titles.find("dailyLastPrice")+17+8].replace('"','').replace(",","")
        return float(s)

#############################################################################
############## Pull Current Portfolio and Obtain Tickers  ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()
cur.execute("""SELECT SUM(value) as total FROM fmi.portfolio;""")
portfoliovalues=cur.fetchall()
for row in portfoliovalues:
    portfoliovalue=row
snpvalue=barchart_snp500()
nasdaqvalue=barchart_nasdaq()
now=datetime.datetime.now()
currentdate=now.strftime("%Y-%m-%d")

cur.execute("""INSERT INTO fmi.portfoliohistory (date,portfolio,snp,nasdaq) VALUES (%s,%s,%s,%s);""", (currentdate,portfoliovalue,snpvalue,nasdaqvalue))
conn.commit()




cur.close()
conn.close()

portfoliohistoryduplicatedelete()

def portfoliohistoryreturnscalc():
    conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM fmi.portfoliohistory;""")
    portfolio=cur.fetchall()
    row=0
    for d,p,s,n,pr,sr,nr in portfolio:
        if row==0:
            pastport=p
            pastsnp=s
            pastnasdaq=n
            row+=1
            print(row)
        else:
            print(p)
            print(pastport)
            portfolioreturn=round((p-pastport)/pastport,2)
            snpreturn=round((s-pastsnp)/pastsnp,2)
            nasdaqreturn=round((n-pastnasdaq)/pastnasdaq,2)
            pastport=p
            pastsnp=s
            pastnasdaq=n
            row+=1
            cur.execute("""INSERT INTO fmi.portfoliohistory (portfolioreturn,snpreturn,nasdaqreturn) where date=%s VALUES (%s,%s,%s);""", (d,portfolioreturn,snpreturn,nasdaqreturn))
            conn.commit()
    cur.close()
    conn.close()

portfoliohistoryreturnscalc()
