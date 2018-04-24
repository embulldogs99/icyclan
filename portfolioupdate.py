import psycopg2
import quandl
import pandas as pd
import quandl

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
cur.close()

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
