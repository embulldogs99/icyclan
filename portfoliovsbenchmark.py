
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

# Create some mock data
t = np.arange(0.01, 10.0, 0.01)
data1 = snpreturns
data2 = portfolioreturns

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('time (s)')
ax1.set_ylabel('exp', color=color)
ax1.plot(t, data1, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('sin', color=color)  # we already handled the x-label with ax1
ax2.plot(t, data2, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
