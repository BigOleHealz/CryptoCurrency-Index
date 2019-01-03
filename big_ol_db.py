#!/usr/bin/env python3
import datetime
import numpy
import requests
import json
# import MySQLdb
import pymysql
import threading
import pandas as pd
from datetime import datetime
from operator import itemgetter
from pandas.io.json import json_normalize
from sqlalchemy import create_engine

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class BigOlDB:

	def __init__(self):
		self.db, self.cursor, self.engine = self.db_connect()

	def db_connect(self):
		endpoint =  "mastertable.cxnyjlbkj9eg.us-east-2.rds.amazonaws.com"
		username = "root"
		dbname = "coinindexcap"
		password = "Healyisadumbcunt"

		db = pymysql.connect(endpoint, username, password, dbname)
		cursor = db.cursor()


		engine = create_engine('sqlite://', echo=False)

		return db, cursor, engine

	### ISSUE: should only retrieve tracked coins
	def get_updated_quotes(self, quote_limit=10):

		request_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit={}"\
			.format(quote_limit)

		headers = {'X-CMC_PRO_API_KEY': '15dd3c67-ac98-4ac2-84eb-5e58007e3d0b'}
		result = requests.get(request_url, headers=headers).json()

		timestamp = result["status"]["timestamp"]
			
		dff = json_normalize(result["data"])[["symbol", "quote.USD.price", 
			"quote.USD.volume_24h", "quote.USD.market_cap"]]
		dff.rename(columns={
			"symbol": "Ticker",
			"quote.USD.price": "Price_USD", 
			"quote.USD.market_cap": "MarketCap_USD",
			"quote.USD.volume_24h": "Volume24hr_USD"},
			inplace=True)
		supported_coins = self.get_supported_coins()["Ticker"].to_frame()
		dff = dff.merge(supported_coins, how="inner", on="Ticker")

		dff["TimeStampID"] = timestamp

		price_btc = dff[dff["Ticker"] == "BTC"]["Price_USD"].iloc[0]
		dff["Price_BTC"] = dff["Price_USD"] / price_btc

		return dff

	def get_supported_coins(self):
		sql = "SELECT * FROM coins"
		self.cursor.execute(sql)
		df = pd.DataFrame(list(self.cursor.fetchall()), columns=["Ticker", 
			"CoinName", "Sector"])

		return df

	def get_minutely_coin_data(self, ticker):
		sql = "SELECT TimeStampID, Price_USD, Price_BTC, MarketCap_USD, \
			Volume24hr_USD FROM	minutely_data WHERE Ticker = '{}'".format(ticker)
		self.cursor.execute(sql)
		df = pd.DataFrame(list(self.cursor.fetchall()), columns=["TimeStamp",
			"Price_USD", "Price_BTC", "MarketCap_USD", "Volume24hr_USD"])

		return df	

	def sql_insert_to_minutely(self, dff):

		for i, row in dff.iterrows():
			try:
				sql = """insert into minutely_data VALUES(null, '%s', '%s',
					'%s', '%s', '%s', '%s')""" % (row["Ticker"], 
					row["TimeStampID"], row["Price_USD"], row["Price_BTC"], 
					row["MarketCap_USD"], row["Volume24hr_USD"])
				self.cursor.execute(sql)
				self.db.commit()
			except Exception as e:
				print(sql)
				pass

	def sql_insert_to_sector_minutely(self, dff):
		for i, row in dff.iterrows():
			try:
				sql = """insert into sector_minutely_data VALUES(null, '%s', '%s',
					'%s', '%s', '%s', '%s')""" % (row["Sector"], 
					row["TimeStampID"], row["Price_USD"], row["Price_BTC"], 
					row["MarketCap_USD"], row["MarketCap_BTC"])
				self.cursor.execute(sql)
				self.db.commit()
			except Exception as e:
				print(e)
				pass

	def get_multipliers(self):
		sql = "select sectorTicker, multiplier from sectors"
		self.cursor.execute(sql)
		result = pd.DataFrame(list(self.cursor.fetchall()), columns=[
			"SectorTicker", "Multiplier"])
		
		return result

	def sql_update_minutely_table(self):
		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		df = self.get_updated_quotes(quote_limit=400)
		df["ID"] = "null"
		df["TimeStampID"] = timestamp
		df = df[["ID", "Ticker", "TimeStampID", "Price_USD", "Price_BTC", 
			"MarketCap_USD", "Volume24hr_USD"]]

		self.sql_insert_to_minutely(df)

	def sql_update_sector_minutely_table(self):
		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		df_multipliers = self.get_multipliers()
		df_coin_quotes = self.get_updated_quotes(quote_limit=400)
		price_btc = df_coin_quotes[df_coin_quotes["Ticker"] == "BTC"][
			"Price_USD"].iloc[0]
		df_sectors = self.get_supported_coins()[["Ticker", "Sector"]]

		df_coin_quotes = df_coin_quotes.merge(df_sectors, on="Ticker", how="inner")
		df_coin_quotes = df_coin_quotes.groupby("Sector").sum().reset_index()[[
			"Sector", "MarketCap_USD", "Volume24hr_USD"]]

		df_coin_quotes = df_coin_quotes.merge(df_multipliers, left_on="Sector", 
			right_on="SectorTicker", how="inner")
		df_coin_quotes["TimeStampID"] = timestamp
		df_coin_quotes["Price_USD"] = df_coin_quotes["MarketCap_USD"] *\
			df_coin_quotes["Multiplier"]
		df_coin_quotes["MarketCap_BTC"] = df_coin_quotes["MarketCap_USD"] / price_btc
		df_coin_quotes["Price_BTC"] = df_coin_quotes["Price_USD"] / price_btc

		self.sql_insert_to_sector_minutely(df_coin_quotes)



