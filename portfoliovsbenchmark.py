# import Image
# import matplotlib.pyplot as plt

# plt.plot(range(10))
# plt.savefig('testplot.png')
# Image.open('testplot.png').save('testplot.jpg','JPEG')
import psycopg2
import pandas as pd

############## Pull Current Portfolio and Obtain Tickers  ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()
cur.execute("""SELECT portfolioreturn,snpreturn,nasdaqreturn FROM fmi.portfoliohistory;""")
portfolio=cur.fetchall()

data=pd.DataFrame(portfolio)


print(data["portfolioreturn")


cur.close()
conn.close()
