#!/usr/bin/env python3
import pymysql, pandas as pd, numpy as np
from credentials import credentials
from big_ol_db import BigOlDB

bodb = BigOlDB()

def calculate_sector_multipliers(sector_ticker):
	sql_tickers = f"""SELECT Ticker FROM coinindexcap.coins WHERE Sector
		 = '{sector_ticker}'"""

	
	bodb.cursor.execute(sql_tickers)
	tickers = tuple([elem[0] for elem in bodb.cursor.fetchall()])

	sql_prices = f"""SELECT Ticker, TimeStampId, MarketCap_USD, Volume24hr_USD
	FROM coinindexcap.minutely_data WHERE TimeStampID BETWEEN 
	'2019-01-02 02:05:00' AND '2019-01-02 23:00:00' AND Ticker IN {tickers}"""


	bodb.cursor.execute(sql_prices)
	df_prices = pd.DataFrame(list(bodb.cursor.fetchall()), columns=["Ticker", "TimeStampID",
		"MarketCap_USD", "Volume24hr_USD"])

	df_prices.drop_duplicates(subset=['Ticker'], keep='first', inplace=True)



	df_prices['mktcap_sqrt'] = np.sqrt(df_prices['MarketCap_USD'])
	df_prices['volume_sqrt'] = np.sqrt(df_prices['Volume24hr_USD'])

	mktcap_multipler = 100 / sum(df_prices['mktcap_sqrt'])
	volume_multiplier = 100 / sum(df_prices['volume_sqrt'])


	return mktcap_multipler, volume_multiplier

def populate_sector_multipliers()
	for ticker in bodb.get_supported_sectors()['sectorTicker']:
		mktcap_multipler, volume_multiplier = calculate_sector_multiplier(ticker)
		sql = f"""UPDATE coinindexcap.sectors SET multiplier_mktcap = 
			{mktcap_multipler} WHERE sectorTicker = '{ticker}';"""

		bodb.cursor.execute(sql)
		bodb.db.commit()


