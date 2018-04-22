import stocks_googlenews4
import psycopg2
import quandl




#############################################################################
############## Pull Current Portfolio and Obtain Tickers  ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()
cur.execute("""SELECT ticker,shares FROM fmi.portfolio;""")
portfolio=cur.fetchall()
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
