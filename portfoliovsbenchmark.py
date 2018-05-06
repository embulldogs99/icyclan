
# Image.open('testplot.png').save('testplot.jpg','JPEG')
import psycopg2
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
############## Pull Current Portfolio and Obtain Tickers  ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()
cur.execute("""SELECT portfolioreturn,snpreturn,nasdaqreturn FROM fmi.portfoliohistory;""")
portfolio=cur.fetchall()

data=pd.DataFrame(portfolio)

portfolioreturns=data[[0]]
snpreturns=data[[1]]
nasdaqreturns=data[[2]]

cur.close()
conn.close()



plt.plot(portfolioreturns, snpreturns, label='vs SnP500')
plt.plot(portfolioreturns, nasdaqreturns, label='vs Nasdaq')


plt.xlabel('x label')
plt.ylabel('y label')

plt.title("Simple Plot")

plt.legend()

plt.show()
