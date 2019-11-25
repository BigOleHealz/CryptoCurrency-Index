#!/usr/bin/env python3
import numpy as np, requests, json, pymysql, pandas as pd, logging
from datetime import datetime
from pandas.io.json import json_normalize
from static.credentials import db_creds, api_creds
from util import sql as queries
from cryptocmd import CmcScraper
from util.functions import df_to_sql

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

	@staticmethod
	def get_historical_quotes(ticker: str):
		scraper = CmcScraper(ticker)
		df = scraper.get_dataframe()
		return pd.DataFrame({'_id' : 'null', 'Ticker' : ticker, 'TimeStampID' : 
			df['Date'], 'Price_USD' : df['High'], 'Price_BTC' : 'null', 
			'MarketCap_USD' : df['Market Cap'], 'Volume24hr_USD' : df['Volume']})

	@classmethod
	def get_supported_coins(cls):
		sql = queries.get_supported_coins
		db, cursor = cls.db_connect()
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["ticker", 
			"coin_name", "sector"])
		return df

	@classmethod
	def get_minutely_coin_data(cls, ticker: str, start: str):
		sql = queries.get_minutely_coin_data.format(tkr=ticker)
		if start: sql += " AND TimeStampID > '{start}'".format(start=start)
		db, cursor = cls.db_connect()
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["TimeStampID", 
			"Price_USD", "Price_BTC", "MarketCap_USD", "Volume24hr_USD"])
		return df

	@classmethod
	def get_coin_moving_average(cls, ticker: str, window=10):
		sql = queries.get_coin_moving_average.format(tkr=ticker, wndw=window)
		db, cursor = cls.db_connect()
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["TimeStampID", "Price_USD"])
		return df

	@classmethod
	def insert_coin_history_to_db(cls, df, commit=True):
		ticker = df.iloc[0]['Ticker']
		sql = queries.insert_coin_history.format(upsrt=df_to_sql('tmp_tbl_coins', df))
		try:
			cursor.execute(sql)
			if commit == True: db.commit()
			return True
		except Exception as e:
			return e

	@classmethod
	def insert_coin(cls, ticker: str, name: str, sector: str):
		sql_get_market = queries.get_market_name.format(tkr=sector)
		db, cursor = cls.db_connect()
		cursor.execute(sql_get_market)
		market = cursor.fetchone()[0]

		df = cls.get_historical_quotes('DASH')
		sql_coin = queries.insert_coin.format(tkr=ticker, nm=name, sctr=sector)

		try:
			cursor.execute(sql_coin)
			cls.insert_coin_history_to_db(df, commit=False)
			db.commit()
		except Exception as e:
			print("Error:", e)


