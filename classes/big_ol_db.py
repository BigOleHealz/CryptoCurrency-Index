#!/usr/bin/env python3
import requests, json, pymysql, logging
import pandas as pd
from datetime import datetime
from pandas.io.json import json_normalize
from static.credentials import db_creds, api_creds
from util import sql as queries, functions as util
from util.config import set_configs
from classes.coin import Coin

set_configs(__file__)


class BigOlDB:

	# def __init__(self):
	# 	logging.info("Initializing Big Ol DB")
	# 	self.db, self.cursor = self.db_connect()

	@staticmethod
	def get_updated_quotes(quote_limit=10) -> pd.DataFrame:
		logging.info('Pulling updated quotes')
		result = requests.get(api_creds['request_url'].format(lmt=quote_limit), 
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
		dff["TimeStampID"] = timestamp

		return dff

	@classmethod
	def get_supported_coins(cls) -> pd.DataFrame:
		sql = queries.get_supported_coins
		db, cursor = cls.db_connect()
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=[
			"coin_ticker", "coin_name", "sector"])
		return df

	@classmethod
	def insert_coin_history_to_db(cls, df, commit=True):
		ticker = df.iloc[0]['Ticker']
		sql = queries.insert_coin_history.format(upsrt=util.df_to_sql_minutely(
			'tmp_tbl_minutely', df))
		return util.execute_sql(sql, commit=commit)

	@classmethod
	def insert_coin(cls, ticker: str, name: str, sector: str):
		coin = Coin(ticker)
		db, cursor = util.db_connect()

		df = coin.get_historical_quotes()
		sql_coin = queries.insert_coin.format(tkr=ticker, nm=name, sctr=sector)

		try:
			util.execute_sql(sql_coin, commit=False)
			cls.insert_coin_history_to_db(df, commit=False)
			db.commit()
		except Exception as e:
			print("Error:", e)

	@classmethod
	def update_minutely_table(cls):
		df_updated = cls.get_updated_quotes(quote_limit=100)

		supported_coins = list(cls.get_supported_coins()["coin_ticker"])
		df_updated = df_updated[df_updated["Ticker"].isin(supported_coins)].reset_index(drop=True)
		sql = queries.insert_coin_history.format(upsrt=util.df_to_sql_minutely(
			'tmp_tbl_minutely', df_updated))
		util.execute_sql(sql, commit=True)



