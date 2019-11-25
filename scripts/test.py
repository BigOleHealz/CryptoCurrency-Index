#!/usr/bin/env python3

# top_package = __import__(__name__.split('.')[0])
import numpy as np, requests, json, pymysql, pandas as pd, logging
from datetime import datetime
from pandas.io.json import json_normalize
from static.credentials import db_creds, api_creds
from util.config import set_configs

set_configs(__file__)

class BigOlDB:

	# def __init__(self):
	# 	logging.info("Initializing Big Ol DB")
	# 	self.db, self.cursor = self.db_connect()

	@staticmethod
	def db_connect():
		logging.info('Attempting to connect to DB')
		try:
			db = pymysql.connect(db_creds['endpoint'], db_creds['username'], 
				db_creds['password'], db_creds['dbname'])
			cursor = db.cursor()
			logging.info('Successfully connected to DB')
			return db, cursor
		except Exception as e:
			return e

	@staticmethod
	def get_updated_quotes(quote_limit=10):
		logging.info('Pulling updated quotes')
		result = requests.get(api_creds['request_url'].format(quote_limit), 
			headers=api_creds['headers']).json()
		timestamp = result["status"]["timestamp"]
		
		dff = json_normalize(result["data"])[["symbol", "quote.USD.price", 
			"quote.USD.volume_24h", "quote.USD.market_cap"]]
		dff.rename(columns={
			"symbol": "Ticker",
			"quote.USD.price": "Price_USD", 
			"quote.USD.market_cap": "MarketCap_USD",
			"quote.USD.volume_24h": "Volume24hr_USD"},
			inplace=True)

		return result

	@classmethod
	def get_supported_coins(cls):
		db, cursor = cls.db_connect()
		sql = "SELECT coin_ticker, coin_name, sector_ticker FROM coinindexcap.coins"
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["ticker", 
			"coin_name", "sector"])
		return df

	@classmethod
	def get_minutely_coin_data(cls, ticker, start):
		db, cursor = cls.db_connect()
		sql = """SELECT TimeStampID, Price_USD, Price_BTC, MarketCap_USD,
			Volume24hr_USD FROM	coinindexcap.minutely_data WHERE Ticker = '{}'""".format(ticker)
		if start: sql += " WHERE TimeStampID > '{start}'".format(start=start)
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["TimeStampID", 
			"Price_USD", "Price_BTC", "MarketCap_USD", "Volume24hr_USD"])
		return df


if __name__ == "__main__":

	coins = BigOlDB.get_minutely_coin_data('ETH')
	
	import pdb; pdb.set_trace()  # breakpoint 6a54cd68 //
