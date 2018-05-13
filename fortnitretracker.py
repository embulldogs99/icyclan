import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import time
import psycopg2

def fortniteuserstats(u):
    t=requests.Session()
    player=u#input("player name: ")
    #api key given to rapidfire.gg
    api = {'TRN-Api-Key':'703cb7b0-4c42-444b-a485-379ed15319b8'}
    # pass api key as header
    r=t.get('http://api.fortnitetracker.com/v1/profile/xbl/'+player, headers = api)
    store=json.loads(r.text)
    print(store)

    squadkills=store['stats']['curr_p9']['kills']['valueInt']
    squadmatch=store['stats']['curr_p9']['matches']['valueInt']
    duokills=store['stats']['curr_p10']['kills']['valueInt']
    duomatch=store['stats']['curr_p10']['matches']['valueInt']
    solokills=store['stats']['p2']['kills']['valueInt']
    solomatch=store['stats']['p2']['matches']['valueInt']
    time=time.time()
    totalkills=squadkills+duokills+solokills
    totalmatch=squadmatch+duomatch+solomatch
    killspermatch=round(totalkills/float(totalmatch),2)

    #########################################################
    ##############  Database Connection   ###################
    conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
    cur = conn.cursor()
    # execute a statement
    cur.execute("INSERT INTO icy.leaderboard WHERE epicusername=%s (date,squadkills,squadmatch,duokills,duomatch,solokills,solomatch,totalkills,totalmatch,killspermatch) VALUES (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s)", (u,time,squadkills,squadmatch,duokills,duomatch,solokills,solomatch,totalkills,totalmatch,killspermatch))
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
        fortniteuserstats(x)
    # close the communication with the PostgreSQL
    # close the communication with the PostgreSQL
    cur.close()
    conn.close()

leaderboardpopulate()
