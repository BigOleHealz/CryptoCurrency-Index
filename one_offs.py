#!/usr/bin/env python3.7
import pymysql, pandas as pd, numpy as np
from credentials import credentials
from big_ol_db import BigOlDB

bodb = BigOlDB()

t0 = '2019-01-20 01:19:05'

def calculate_sector_multipliers(sector_ticker):
	sql_tickers = f"""SELECT Ticker FROM coinindexcap.coins WHERE Sector
		 = '{sector_ticker}'"""

	bodb.cursor.execute(sql_tickers)
	tickers = tuple([elem[0] for elem in bodb.cursor.fetchall()])

	sql_prices = f"""SELECT Ticker, TimeStampId, MarketCap_USD, Volume24hr_USD
		FROM coinindexcap.minutely_data WHERE TimeStampID = '{t0}'
		AND Ticker IN {tickers}"""

	bodb.cursor.execute(sql_prices)
	df_prices = pd.DataFrame(list(bodb.cursor.fetchall()), columns=["Ticker", "TimeStampID",
		"MarketCap_USD", "Volume24hr_USD"])

	df_prices['mktcap_sqrt'] = np.sqrt(df_prices['MarketCap_USD'])
	df_prices['volume_sqrt'] = np.sqrt(df_prices['Volume24hr_USD'])

	mktcap_multipler = 100 / sum(df_prices['mktcap_sqrt'])
	volume_multiplier = 100 / sum(df_prices['volume_sqrt'])

	return mktcap_multipler, volume_multiplier

def populate_sector_multipliers():
	for ticker in bodb.get_supported_sectors()['sectorTicker']:
		mktcap_multipler, volume_multiplier = calculate_sector_multiplier(ticker)
		sql = f"""UPDATE coinindexcap.sectors SET multiplier_mktcap = 
			{mktcap_multipler} WHERE sectorTicker = '{ticker}';"""

		bodb.cursor.execute(sql)
		bodb.db.commit()


def populate_sector_minutely_table(ticker):

	tickers = tuple(bodb.get_coins_in_sector(ticker))

	sql = f"""SELECT Ticker, TimeStampId, MarketCap_USD, Volume24hr_USD
		FROM coinindexcap.minutely_data WHERE Ticker IN {tickers} AND 
		TimeStampID > '{t0}'"""
	bodb.cursor.execute(sql)

	df = pd.DataFrame(list(bodb.cursor.fetchall()), columns=[
		"Ticker", "TimeStampID", "MarketCap", "Volume"])

	df["MarketCap_sqrt"] = np.sqrt(df["MarketCap"])
	df["Volume_sqrt"] = np.sqrt(df["Volume"])
	multipliers = bodb.get_sector_multiplier(ticker)
	
	df["MarketCap_weighted"] = df["MarketCap_sqrt"] * multipliers["Multiplier_MktCap"][0]
	df["Volume_weighted"] = df["Volume_sqrt"] * multipliers["Multiplier_Volume"][0]

	for ts in df["TimeStampID"].unique():
		dff = df[df["TimeStampID"] == ts]

		dict_mktcap, dict_volume = {}, {}

		for i, row in dff.iterrows():
			dict_mktcap[row["Ticker"]] = row["MarketCap_weighted"]
			dict_volume[row["Ticker"]] = row["Volume_weighted"]

		str_dict_mktcap = str(dict_mktcap).replace("'", '"')
		str_dict_volume = str(dict_volume).replace("'", '"')

		sql_insert = f"""INSERT INTO coinindexcap.sector_minutely_data VALUES(null, '{ticker}', '{ts}', 0, 0, 0, 0, '{str_dict_mktcap}', '{str_dict_volume}');"""

		bodb.cursor.execute(sql_insert)
		bodb.db.commit()



populate_sector_minutely_table('XF')

# for sector in bodb.get_supported_sectors()["sectorTicker"]:

# 	print(sector)
# 	populate_sector_minutely_table(sector)

# calculate_sector_multipliers('XPA')