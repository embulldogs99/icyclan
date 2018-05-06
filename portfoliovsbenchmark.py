import Image
import matplotlib.pyplot as plt

# plt.plot(range(10))
# plt.savefig('testplot.png')
# Image.open('testplot.png').save('testplot.jpg','JPEG')



############## Pull Current Portfolio and Obtain Tickers  ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()
cur.execute("""SELECT portfolioreturn,snpreturn,nasdaqreturn FROM fmi.portfoliohistory;""")
portfolio=cur.fetchall()

start=1
####################################################
###Pull Quandl Price information for each ticker and send it to database#########
###################################################
port=[]
snp=[]
nasdaq=[]
for pr,sr,nr in portfolio:
    if start==1:
        relport=start+(start*pr)
        relsnp=start+(start*sr)
        relnasdaq=start+(start*sr)
        port=port.append(relport)
        snp=snp.append(relsnp)
        nasdaq=nasdaq.append(relnasdaq)
        start+=1
    else:
        relport=relport+(relport*pr)
        relsnp=relsnp+(relsnp*sr)
        relnasdaq=relnasdaq+(relnasdaq*sr)
        port=port.append(relport)
        snp=snp.append(relsnp)
        nasdaq=nasdaq.append(relnasdaq)


print(port)
print(snp)
print(nasdaq)


cur.close()
conn.close()
