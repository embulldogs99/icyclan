# coding: utf-8
######################################################
####################################################
######### Imports #####################

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

warnings.filterwarnings('ignore')

###########################################################
##########################################################
######## Used QUANDL Functions #########################

quandl.ApiConfig.api_key = 'omQiMysF2NQ1B-xZEJBk'

def quandl_stocks(symbol, start_date=(2010, 1, 1), end_date=None):
    query_list = ['WIKI' + '/' + symbol + '.' + str(k) for k in range(11, 12)]
    start_date = datetime.date(*start_date)
    if end_date:
        end_date = datetime.date(*end_date)
    else:
        end_date = datetime.date.today()
    return quandl.get(query_list,
            returns='pandas',
            start_date=start_date,
            end_date=end_date,
            collapse='daily',
            order='asc'
            )

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


########################################################################################
##########################################################################################
###############            YAHOO PE and EPS pullers    ##################################
##########################################################################################

def yahoopepuller(ticker):
	with requests.Session() as c:
		u="http://finance.yahoo.com/quote/"+ticker+"?p=" + ticker
		x=c.get(u)
		x=BeautifulSoup(x.content)
		titles=x.find_all()
		titles=str(titles)
		s=titles.find("PE_RATIO-value")
		pe=titles[s:s+1000]
		sn=pe.find("react-text")
		pe=pe[sn+17:sn+24]
		pe=pe.replace(">","").replace("!","").replace("<","")
		try:
			pe=float(pe)
		except:
			pe=0
		return pe

def yahooepspuller(ticker):
	with requests.Session() as c:
		u="http://finance.yahoo.com/quote/"+ticker+"?p=" + ticker
		x=c.get(u)
		x=BeautifulSoup(x.content)
		titles=x.find_all()
		titles=str(titles)
		s=titles.find("EPS_RATIO-value")
		pe=titles[s:s+1000]
		sn=pe.find("react-text")
		pe=pe[sn+17:sn+24]
		pe=pe.replace(">","").replace("!","").replace("<","")
		try:
			pe=float(pe)
		except:
			pe=0
		return pe

 ############################################################################################
 ############################################################################################
 ############################################################################################
 #############                                                ###############################
 #############                Accenture URLS                    #############################
 #############                                                ###############################
 ############################################################################################
 ############################################################################################
 ############################################################################################
 ############################################################################################


acnurls=['https://newsroom.accenture.com/subjects/news/rss.xml'
,'https://newsroom.accenture.com/industries/agribusiness/rss.xml'
,'https://newsroom.accenture.com/industries/airlines/rss.xml'
,'https://newsroom.accenture.com/industries/automotive/rss.xml'
,'https://newsroom.accenture.com/industries/communications/rss.xml'
,'https://newsroom.accenture.com/industries/consumer-goods--services/rss.xml'
,'https://newsroom.accenture.com/industries/electronics-high-tech/rss.xml'
,'https://newsroom.accenture.com/industries/freight-logistics/rss.xml'
,'https://newsroom.accenture.com/industries/health-life-sciences/rss.xml'
,'https://newsroom.accenture.com/industries/industrial-equipment/rss.xml'
,'https://newsroom.accenture.com/industries/management-consulting/rss.xml'
,'https://newsroom.accenture.com/industries/media-entertainment/rss.xml'
,'https://newsroom.accenture.com/industries/public-transportation/rss.xml'
,'https://newsroom.accenture.com/industries/rail/rss.xml'
,'https://newsroom.accenture.com/industries/retail/rss.xml'
,'https://newsroom.accenture.com/industries/strategy/rss.xml'
,'https://newsroom.accenture.com/industries/travel-services-hospitality/rss.xml'
,'https://newsroom.accenture.com/subjects/subjects/rss.xml'
,'https://newsroom.accenture.com/subjects/acquisitions/rss.xml'
,'https://newsroom.accenture.com/subjects/analytics/rss.xml'
,'https://newsroom.accenture.com/subjects/client-wins-new-contracts/rss.xml'
,'https://newsroom.accenture.com/subjects/digital/rss.xml'
,'https://newsroom.accenture.com/subjects/financial-earnings/rss.xml'
,'https://newsroom.accenture.com/subjects/interactive-marketing/rss.xml'
,'https://newsroom.accenture.com/subjects/leadership-management/rss.xml'
,'https://newsroom.accenture.com/subjects/management-consulting/rss.xml'
,'https://newsroom.accenture.com/subjects/mobility/rss.xml'
,'https://newsroom.accenture.com/subjects/operations/rss.xml'
,'https://newsroom.accenture.com/subjects/outsourcing/rss.xml'
,'https://newsroom.accenture.com/subjects/research-surveys/rss.xml'
,'https://newsroom.accenture.com/subjects/strategy/rss.xml'
,'https://newsroom.accenture.com/subjects/technology/rss.xml'
,'https://newsroom.accenture.com/subjects/photos/rss.xml'


 ############################################################################################
 ############################################################################################
 ############################################################################################
 #############                                                ###############################
 #############                Reuters URLS                     ##############################
 #############                                                ###############################
 ############################################################################################
 ############################################################################################
 ############################################################################################
 ############################################################################################


,'http://feeds.reuters.com/news/artsculture'
,'http://feeds.reuters.com/reuters/businessNews'
,'http://feeds.reuters.com/reuters/companyNews'
,'http://feeds.reuters.com/reuters/entertainment'
,'http://feeds.reuters.com/reuters/environment'
,'http://feeds.reuters.com/reuters/healthNews'
,'http://feeds.reuters.com/reuters/lifestyle'
,'http://feeds.reuters.com/news/wealth'
,'http://feeds.reuters.com/reuters/MostRead'
,'http://feeds.reuters.com/reuters/oddlyEnoughNews'
,'http://feeds.reuters.com/ReutersPictures'
,'http://feeds.reuters.com/reuters/peopleNews'
,'http://feeds.reuters.com/Reuters/PoliticsNews'
,'http://feeds.reuters.com/reuters/scienceNews'
,'http://feeds.reuters.com/reuters/sportsNews'
,'http://feeds.reuters.com/reuters/technologyNews'
,'http://feeds.reuters.com/reuters/topNews'
,'http://feeds.reuters.com/Reuters/domesticNews'
,'http://feeds.reuters.com/Reuters/worldNews'
,'http://feeds.reuters.com/reuters/USVideoBreakingviews'
,'http://feeds.reuters.com/reuters/USVideoBusiness'
,'http://feeds.reuters.com/reuters/USVideoBusinessTravel'
,'http://feeds.reuters.com/reuters/USVideoChrystiaFreeland'
,'http://feeds.reuters.com/reuters/USVideoEntertainment'
,'http://feeds.reuters.com/reuters/USVideoEnvironment'
,'http://feeds.reuters.com/reuters/USVideoFelixSalmon'
,'http://feeds.reuters.com/reuters/USVideoGigaom'
,'http://feeds.reuters.com/reuters/USVideoLifestyle'
,'http://feeds.reuters.com/reuters/USVideoMostWatched'
,'http://feeds.reuters.com/reuters/USVideoLatest'
,'http://feeds.reuters.com/reuters/USVideoNewsmakers'
,'http://feeds.reuters.com/reuters/USVideoOddlyEnough'
,'http://feeds.reuters.com/reuters/USVideoPersonalFinance'
,'http://feeds.reuters.com/reuters/USVideoPolitics'
,'http://feeds.reuters.com/reuters/USVideoRoughCuts'
,'http://feeds.reuters.com/reuters/USVideoSmallBusiness'
,'http://feeds.reuters.com/reuters/USVideoTechnology'
,'http://feeds.reuters.com/reuters/USVideoTopNews'
,'http://feeds.reuters.com/reuters/USVideoWorldNews'
]

 ############################################################################################
 ############################################################################################
 ############################################################################################
 #############                                                ###############################
 #############                Regular URLS                     ##############################
 #############                                                ###############################
 ############################################################################################
 ############################################################################################
 ############################################################################################
 ############################################################################################



urls=['http://ir.appliedmaterials.com/corporate.rss?c=112059&Rule=Cat=news~subcat=ALL'
,'https://nvidianews.nvidia.com/cats/press_release.xml'
,'http://www.marketwatch.com/rss/realtimeheadlines'
,'http://catocorp.gcs-web.com/rss/sec-filings.xml?items=15'
,'http://catocorp.gcs-web.com/rss/news-releases.xml?items=15'
,'http://apps.shareholder.com/rss/rss.aspx?channels=5270&companyid=MHLD&sh_auth=5661033414%2E0%2E0%2E43073%2E6dd2d10eaa7ab9aa00471f15b84e1b33'
,'http://apps.shareholder.com/rss/rss.aspx?channels=5271&companyid=MHLD&sh_auth=5661033414%2E0%2E0%2E43073%2E6dd2d10eaa7ab9aa00471f15b84e1b33'
,'http://apps.shareholder.com/rss/rss.aspx?channels=5272&companyid=MHLD&sh_auth=5661033414%2E0%2E0%2E43073%2E6dd2d10eaa7ab9aa00471f15b84e1b33'
,'http://ir.allegiantair.com/corporate.rss?c=197578&Rule=Cat=news~subcat=ALL'
,'http://ir.allegiantair.com/corporate.rss?c=197578&Rule=Cat=sec~subcat=ALL'
,'http://investor.oritani.com/rss/prfeed.aspx?iid=4047189'
,'http://investor.oritani.com/insiders.aspx?iid=4047189&rss=1'
,'http://www.snl.com/IRWebLinkX/rss/prfeed.aspx?iid=4089088'
,'http://www.snl.com/IRWebLinkX/insiders.aspx?iid=4089088&rss=1'
,'http://www.snl.com/IRWebLinkX/docs.aspx?iid=4089088&rss=1'
,'https://callawaygolf.gcs-web.com/rss/news-releases.xml'
,'https://callawaygolf.gcs-web.com/rss/sec-filings.xml'
,'https://callawaygolf.gcs-web.com/rss/events.xml'
,'http://www.b2ixml.com/rss/newsrss.asp?b=1690&l=1&k=Xq2Qb5Ue5'
,'https://www.investors.com/rss.axd?path=investingRSS.xml'
,'https://www.investors.com/rss.axd?path=businessRSS.xml'
,'https://www.investors.com/rss.axd?path=economyRSS.xml'
,'https://www.investors.com/rss.axd?path=internetAndTechRSS.xml'
,'https://www.nasa.gov/rss/dyn/breaking_news.rss'
,'https://www.nasa.gov/rss/dyn/educationnews.rss'
,'https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss'
,'https://blogs.nasa.gov/stationreport/feed/'
,'https://www.nasa.gov/rss/dyn/onthestation_rss.rss'
,'https://www.nasa.gov/rss/dyn/mission_pages/kepler/news/kepler-newsandfeatures-RSS.rss'
,'https://www.nasa.gov/rss/dyn/chandra_images.rss'
,'http://phx.corporate-ir.net/corporate.rss?c=97664&Rule=Cat=sec~subcat=ALL'
,'http://phx.corporate-ir.net/corporate.rss?c=97664&Rule=Cat=events~subcat=ALL'
,'http://phx.corporate-ir.net/corporate.rss?c=97664&Rule=Cat=news~subcat=ALL'
,'http://appleinsider.com/rss/news/'
,'http://appleinsider.com/rss/topic/podcast'
]


 ############################################################################################
 ############################################################################################
 ############################################################################################
 #############                                                ###############################
 #############                SNP 500 GOOGLE URLS              ##############################
 #############                                                ###############################
 ############################################################################################
 ############################################################################################
 ############################################################################################
 ############################################################################################


snp500googleurls=['https://news.google.com/news/rss/search/section/q/GOOG/GOOG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/A/A?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AA/AA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AAPL/AAPL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ABC/ABC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ABT/ABT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ACE/ACE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ACN/ACN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ADBE/ADBE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ADI/ADI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ADM/ADM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ADP/ADP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ADSK/ADSK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ADT/ADT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AEE/AEE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AEP/AEP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AES/AES?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AET/AET?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AFL/AFL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AGN/AGN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AIG/AIG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AIV/AIV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AIZ/AIZ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AKAM/AKAM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ALL/ALL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ALTR/ALTR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ALXN/ALXN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AMAT/AMAT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AMD/AMD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AMGN/AMGN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AMP/AMP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AMT/AMT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AMZN/AMZN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AN/AN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ANF/ANF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AON/AON?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/APA/APA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/APC/APC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/APD/APD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/APH/APH?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/APOL/APOL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ARG/ARG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ATI/ATI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AVB/AVB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AVP/AVP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AVY/AVY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AXP/AXP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/AZO/AZO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BA/BA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BAC/BAC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BAX/BAX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BBBY/BBBY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BBT/BBT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BBY/BBY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BCR/BCR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BDX/BDX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BEAM/BEAM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BEN/BEN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BF.B/BF.B?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BHI/BHI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BIG/BIG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BIIB/BIIB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BK/BK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BLK/BLK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BLL/BLL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BMC/BMC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BMS/BMS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BMY/BMY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BRCM/BRCM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BRK.B/BRK.B?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BSX/BSX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BTU/BTU?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BWA/BWA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/BXP/BXP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/C/C?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CA/CA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CAG/CAG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CAH/CAH?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CAM/CAM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CAT/CAT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CB/CB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CBG/CBG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CBS/CBS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CCE/CCE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CCI/CCI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CCL/CCL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CELG/CELG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CERN/CERN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CF/CF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CFN/CFN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CHK/CHK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CHRW/CHRW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CI/CI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CINF/CINF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CL/CL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CLF/CLF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CLX/CLX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CMA/CMA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CMCSA/CMCSA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CME/CME?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CMG/CMG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CMI/CMI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CMS/CMS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CNP/CNP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CNX/CNX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/COF/COF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/COG/COG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/COH/COH?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/COL/COL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/COP/COP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/COST/COST?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/COV/COV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CPB/CPB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CRM/CRM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CSC/CSC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CSCO/CSCO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CSX/CSX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CTAS/CTAS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CTL/CTL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CTSH/CTSH?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CTXS/CTXS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CVC/CVC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CVH/CVH?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CVS/CVS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/CVX/CVX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/D/D?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DD/DD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DE/DE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DELL/DELL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DF/DF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DFS/DFS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DG/DG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DGX/DGX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DHI/DHI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DHR/DHR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DIS/DIS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DISCA/DISCA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DLTR/DLTR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DNB/DNB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DNR/DNR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DO/DO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DOV/DOV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DOW/DOW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DPS/DPS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DRI/DRI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DTE/DTE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DTV/DTV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DUK/DUK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DVA/DVA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/DVN/DVN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EA/EA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EBAY/EBAY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ECL/ECL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ED/ED?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EFX/EFX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EIX/EIX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EL/EL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ELY/ELY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EMN/EMN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EMR/EMR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EOG/EOG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EQR/EQR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EQT/EQT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ESRX/ESRX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ESV/ESV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ETFC/ETFC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ETN/ETN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ETR/ETR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EW/EW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EXC/EXC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EXPD/EXPD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/EXPE/EXPE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/F/F?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FAST/FAST?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FCX/FCX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FDO/FDO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FDX/FDX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FE/FE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FFIV/FFIV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FHN/FHN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FII/FII?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FIS/FIS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FISV/FISV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FITB/FITB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FLIR/FLIR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FLR/FLR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FLS/FLS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FMC/FMC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FOSL/FOSL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FRX/FRX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FSLR/FSLR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FTI/FTI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/FTR/FTR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GAS/GAS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GCI/GCI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GD/GD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GE/GE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GILD/GILD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GIS/GIS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GLW/GLW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GME/GME?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GNW/GNW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GOOG/GOOG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GPC/GPC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GPS/GPS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GS/GS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GT/GT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/GWW/GWW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HAL/HAL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HAR/HAR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HAS/HAS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HBAN/HBAN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HCBK/HCBK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HCN/HCN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HCP/HCP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HD/HD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HES/HES?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HIG/HIG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HNZ/HNZ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HOG/HOG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HON/HON?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HOT/HOT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HP/HP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HPQ/HPQ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HRB/HRB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HRL/HRL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HRS/HRS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HSP/HSP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HST/HST?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HSY/HSY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/HUM/HUM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/IBM/IBM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ICE/ICE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/IFF/IFF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/IGT/IGT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/INTC/INTC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/INTU/INTU?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/IP/IP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/IPG/IPG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/IR/IR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/IRM/IRM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ISRG/ISRG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ITW/ITW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/IVZ/IVZ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JBL/JBL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JCI/JCI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JCP/JCP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JDSU/JDSU?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JEC/JEC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JNJ/JNJ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JNPR/JNPR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JOY/JOY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JPM/JPM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/JWN/JWN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/K/K?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KEY/KEY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KIM/KIM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KLAC/KLAC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KMB/KMB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KMI/KMI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KMX/KMX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KO/KO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KR/KR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KRFT/KRFT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/KSS/KSS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/L/L?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LEG/LEG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LEN/LEN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LH/LH?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LIFE/LIFE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LLL/LLL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LLTC/LLTC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LLY/LLY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LM/LM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LMT/LMT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LNC/LNC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LO/LO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LOW/LOW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LRCX/LRCX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LSI/LSI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LTD/LTD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LUK/LUK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LUV/LUV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/LYB/LYB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/M/M?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MA/MA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MAR/MAR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MAS/MAS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MAT/MAT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MCD/MCD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MCHP/MCHP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MCK/MCK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MCO/MCO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MDLZ/MDLZ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MDT/MDT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MET/MET?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MHP/MHP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MJN/MJN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MKC/MKC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MMC/MMC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MMM/MMM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MNST/MNST?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MO/MO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MOLX/MOLX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MON/MON?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MOS/MOS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MPC/MPC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MRK/MRK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MRO/MRO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MS/MS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MSFT/MSFT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MSI/MSI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MTB/MTB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MU/MU?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MUR/MUR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MWV/MWV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/MYL/MYL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NBL/NBL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NBR/NBR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NDAQ/NDAQ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NE/NE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NEE/NEE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NEM/NEM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NFLX/NFLX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NFX/NFX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NI/NI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NKE/NKE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NOC/NOC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NOV/NOV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NRG/NRG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NSC/NSC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NTAP/NTAP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NTRS/NTRS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NU/NU?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NUE/NUE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NVDA/NVDA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NWL/NWL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NWSA/NWSA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NYX/NYX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/OI/OI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/OKE/OKE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/OMC/OMC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ORCL/ORCL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ORLY/ORLY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/OXY/OXY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PAYX/PAYX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PBCT/PBCT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PBI/PBI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PCAR/PCAR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PCG/PCG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PCL/PCL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PCLN/PCLN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PCP/PCP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PCS/PCS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PDCO/PDCO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PEG/PEG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PEP/PEP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PETM/PETM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PFE/PFE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PFG/PFG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PG/PG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PGR/PGR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PH/PH?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PHM/PHM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PKI/PKI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PLD/PLD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PLL/PLL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PM/PM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PNC/PNC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PNR/PNR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PNW/PNW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/POM/POM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PPG/PPG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PPL/PPL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PRGO/PRGO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PRU/PRU?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PSA/PSA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PSX/PSX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PWR/PWR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PX/PX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PXD/PXD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/QCOM/QCOM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/QEP/QEP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/R/R?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RAI/RAI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RDC/RDC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RF/RF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RHI/RHI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RHT/RHT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RL/RL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ROK/ROK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ROP/ROP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ROST/ROST?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RRC/RRC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RRD/RRD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RSG/RSG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/RTN/RTN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/S/S?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SAI/SAI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SBUX/SBUX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SCG/SCG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SCHW/SCHW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SE/SE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SEE/SEE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SHW/SHW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SIAL/SIAL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SJM/SJM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SLB/SLB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SLM/SLM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SNA/SNA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SNDK/SNDK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SNI/SNI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SO/SO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SPG/SPG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SPLS/SPLS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SRCL/SRCL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SRE/SRE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/STI/STI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/STJ/STJ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/STT/STT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/STX/STX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/STZ/STZ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SWK/SWK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SWN/SWN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SWY/SWY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SYK/SYK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SYMC/SYMC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/SYY/SYY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/T/T?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TAP/TAP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TDC/TDC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TE/TE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TEG/TEG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TEL/TEL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TER/TER?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/THC/THC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TIE/TIE?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TIF/TIF?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TJX/TJX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TMK/TMK?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TMO/TMO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TRIP/TRIP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TROW/TROW?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TRV/TRV?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TSN/TSN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TSO/TSO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TSS/TSS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TWC/TWC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TWX/TWX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TXN/TXN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TXT/TXT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TYC/TYC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/UNH/UNH?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/UNM/UNM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/UNP/UNP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/UPS/UPS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/URBN/URBN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/USB/USB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/UTX/UTX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/V/V?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VAR/VAR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VFC/VFC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VIAB/VIAB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VLO/VLO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VMC/VMC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VNO/VNO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VRSN/VRSN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VTR/VTR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/VZ/VZ?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WAG/WAG?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WAT/WAT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WDC/WDC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WEC/WEC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WFC/WFC?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WFM/WFM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WHR/WHR?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WIN/WIN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WLP/WLP?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WM/WM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WMB/WMB?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WMT/WMT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WPI/WPI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WPO/WPO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WPX/WPX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WU/WU?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WY/WY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WYN/WYN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/WYNN/WYNN?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/X/X?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/XEL/XEL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/XL/XL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/XLNX/XLNX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/XOM/XOM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/XRAY/XRAY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/XRX/XRX?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/XYL/XYL?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/YHOO/YHOO?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/YUM/YUM?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ZION/ZION?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ZMH/ZMH?hl=en&gl=US&ned=us'

####other stocks
,'https://news.google.com/news/rss/search/section/q/MHLD/MHLD?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ORIT/ORIT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ALGT/ALGT?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/ELY/ELY?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NTRI/NTRI?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/PETS/PETS?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/NVDA/NVDA?hl=en&gl=US&ned=us'
,'https://news.google.com/news/rss/search/section/q/TSLA/TSLA?hl=en&gl=US&ned=us'
]





now=datetime.datetime.now()

def contentfilter():
    with requests.Session() as c:
        map=['']
        urls=snp500googleurls
        for u in urls:
            try:
                time.sleep(1)
                x=c.get(u)
                x=BeautifulSoup(x.content)
                titles=x.find_all('title')
                pubdate=x.find_all('lastbuilddate')+x.find_all('pubdate')
                for p,t in zip(pubdate,titles):
                    """Assemble our Output Variable"""
                    """Data may be nil/missing or error prone. Going to TRY this step"""
                    pub=str(p.text)
                    info=str(t.text)
                    if info.find(';')>0:
                        info=info[:info.find(';')]



    				###Dynamically determining stock based on text. Assuming results may not match original search keyword
                    stock=info[info.find('(')+1:info.find(')')].replace('NYSE:','').replace('NASDAQ:','').replace('NYSE ','').replace(':','').replace(' ','')
                    grab=info

    				# Save Initial Data to Raw File

    				# f = open('rawmarketmentions.txt'+str(now.month)+'-'+str(now.day)+'-'+str(now.year)+'-UnSelected.txt', 'a')
    				# f.write(grab+' | ' + pub +'\n')
    				# f.close()

    				## Begin filtering the data for model output
    				## First find $$$$
                    if grab.count('$') > 0:
                        targ=int(0)
                        targ=grab.find('$')
                        value=grab[targ+1:targ+5]######## now you have the targeted value

                        try:
                            value=float(value)
                            price=quandl_adj_close(stock)####### now you have the stock price from quandl
                            if price == None:
    							price=0
                        except:
                            value=0
                            price=0

                        if price>1 and value>0:

                            epsreference=yahooepspuller(stock)

                            if grab.find('EPS') >0 or grab.find('eps') > 0:
                                targetprice=round(value*4*25,0) #using marget P/E here insteead of individual stock's p/e to avoid -p/e erro
                                epsexpreturn=(targetprice-price)/price

    							#########################################################
    							##############  Database Connection   ###################
                                conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
                                cur = conn.cursor()
    							# execute a statement
                                cur.execute("INSERT INTO fmi.marketmentions (target, price, returns, ticker, note, date, q_eps, a_eps, report) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (targetprice,price,epsexpreturn,stock,grab,pub,value,epsreference,'earnings'))
                                print("inserted value")
                                conn.commit()
    							# close the communication with the PostgreSQL
                                cur.close()
                                conn.close()


                            if grab.find('arget') > 0:
                                predreturn=(value-price)/price
                                #########################################################
                                ##############  Database Connection   ###################
                                conn = psycopg2.connect("dbname='postgres' user='postgres' password='postgres' host='localhost' port='5432'")
                                cur = conn.cursor()
                                # execute a statement
                                cur.execute("INSERT INTO fmi.marketmentions (target, price, returns, ticker, note, date, q_eps, a_eps, report) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (value,price,predreturn,stock,grab,pub,None,epsreference,'analyst'))
                                print("inserted value")
                                conn.commit()
                                # close the communication with the PostgreSQL
                                cur.close()
                                conn.close()
            except:
                pass


#run for 100 cycles of 6 hours each
for i in range(1,100):
    mmduprem()
    contentfilter()
    mmduprem()
    print('end')
    time.sleep(86400/2)
