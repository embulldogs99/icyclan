import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import time
import psycopg2

def fortniteuserstats(u):
    t=requests.Session()
    #api key given to rapidfire.gg
    api = {'TRN-Api-Key':'703cb7b0-4c42-444b-a485-379ed15319b8'}
    # pass api key as header
    r=t.get('http://api.fortnitetracker.com/v1/profile/xbl/'+str(u), headers = api)
    store=json.loads(r.text)
    squadkills=store['stats']['p9']['kills']['valueInt']
    squadmatch=store['stats']['p9']['matches']['valueInt']
    duokills=store['stats']['p10']['kills']['valueInt']
    duomatch=store['stats']['p10']['matches']['valueInt']
    solokills=store['stats']['p2']['kills']['valueInt']
    solomatch=store['stats']['p2']['matches']['valueInt']
    curtime=time.strftime("%Y-%m-%d", time.gmtime(time.time()))
    totalkills=squadkills+duokills+solokills
    totalmatch=squadmatch+duomatch+solomatch
    killspermatch=round(totalkills/float(totalmatch),2)

    #########################################################
    ##############  Database Connection   ###################
    conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
    cur = conn.cursor()
    # execute a statement
    cur.execute("UPDATE icy.leaderboard set date=%s,squadkills=%s,squadmatch=%s,duokills=%s,duomatch=%s,solokills=%s,solomatch=%s,totalkills=%s,totalmatch=%s,killspermatch=%s WHERE epicusername=%s", (str(curtime),squadkills,squadmatch,duokills,duomatch,solokills,solomatch,totalkills,totalmatch,killspermatch,u))
    conn.commit()
    # delete duplicates to clean table
    cur.execute("CREATE TABLE icy.leaderboard_temp (LIKE icy.leaderboard);")
    conn.commit()
    cur.execute("INSERT into icy.leaderboard_temp(date,epicusername,squadkills,squadmatch,duokills,duomatch,solokills,solomatch,totalkills,totalmatch,killspermatch) SELECT DISTINCT ON (epicusername) date,epicusername,squadkills,squadmatch,duokills,duomatch,solokills,solomatch,totalkills,totalmatch,killspermatch FROM icy.leaderboard;")
    conn.commit()
    cur.execute("DROP TABLE icy.leaderboard;")
    conn.commit()
    cur.execute("ALTER TABLE icy.leaderboard_temp RENAME TO icy.leaderboard;")
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()
    conn.close()


def leaderboardpopulate():
    #########################################################
    ##############  Database Connection   ###################
    conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
    cur = conn.cursor()
    # execute a statement
    cur.execute("SELECT DISTINCT epicusername from icy.leaderboard")
    conn.commit()
    ##get leaderboardlist
    rows = cur.fetchall()
    for x in rows:
        for t in x:
            fortniteuserstats(str(t))
    # close the communication with the PostgreSQL
    # close the communication with the PostgreSQL
    cur.close()
    conn.close()


leaderboardpopulate()
