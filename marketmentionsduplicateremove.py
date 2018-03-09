import psycopg2

#########################################################
##############  Database Connection   ###################
conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
cur = conn.cursor()

cur.execute("CREATE TABLE fmi.marketmentions_temp (LIKE fmi.marketmentions);")
conn.commit()
cur.execute("INSERT into fmi.marketmentions_temp(target,price,returns,ticker,note,date,q_eps,a_eps,report)
"SELECT DISTINCT ON (ticker,date) "
"target,price,returns,ticker,note,date,q_eps,a_eps,report"
"FROM fmi.marketmentions;")
conn.commit()
cur.execute("DROP TABLE fmi.marketmentions;")
conn.commit()
cur.execute("ALTER TABLE fmi.marketmentions_temp RENAME TO fmi.marketmentions;")
conn.commit()
# close the communication with the PostgreSQL
cur.close()
conn.close()
