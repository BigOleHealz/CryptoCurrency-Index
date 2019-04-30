#!/usr/bin/env python3
import datetime
from datetime import datetime
from pandas.io.json import json_normalize
import logging, hashlib, threading, pymysql, json, requests, numpy as np, pandas as pd
from credentials import credentials
import static.flash_messages as fl_mes

import random

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

class BigOlDB:

	def __init__(self):
		logging.info("Initializing Big Ol DB")
		try:
			self.db, self.cursor = self.db_connect()
			logging.info("Connected to DB successfully")
		except Exception as e:
			logging.info("Failed to connect to DB \\t Error: {}".format(e))

	def db_connect(self):
		logging.info("Connecting to DB")

		endpoint =  credentials['endpoint']
		username = credentials['username']
		dbname = credentials['dbname']
		password = credentials['password']

		db = pymysql.connect(endpoint, username, password, dbname)
		cursor = db.cursor()

		return db, cursor

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

	def get_supported_sectors(self):
		sql = "SELECT sectorTicker, sectorName FROM sectors"
		self.cursor.execute(sql)
		df = pd.DataFrame(list(self.cursor.fetchall()), columns=["sectorTicker", 
			"sectorName"])

		return df

	def get_minutely_coin_data(self, ticker):
		sql = "SELECT TimeStampID, Price_USD, Price_BTC, MarketCap_USD, \
			Volume24hr_USD FROM	minutely_data WHERE Ticker = '{}'".format(ticker)
		self.cursor.execute(sql)
		df = pd.DataFrame(list(self.cursor.fetchall()), columns=["TimeStampID",
			"Price_USD", "Price_BTC", "MarketCap_USD", "Volume24hr_USD"])

		return df	

	### MUST BE UPGRADED AND DELETED ###
	def sql_insert_to_minutely(self, dff):

		for i, row in dff.iterrows():
			try:
				sql = """INSERT INTO minutely_data VALUES(null, '%s', '%s',
					'%s', '%s', '%s', '%s')""" % (row["Ticker"], 
					row["TimeStampID"], row["Price_USD"], row["Price_BTC"], 
					row["MarketCap_USD"], row["Volume24hr_USD"])
				self.cursor.execute(sql)
				self.db.commit()
			except Exception as e:
				print(sql)
				pass

	### MUST BE UPGRADED AND DELETED ###
	def sql_insert_to_sector_minutely(self, dff):
		for i, row in dff.iterrows():
			try:
				sql = """INSERT INTO sector_minutely_data VALUES(null, '%s', '%s',
					'%s', '%s', '%s', '%s')""" % (row["Sector"], 
					row["TimeStampID"], row["Price_USD"], row["Price_BTC"], 
					row["MarketCap_USD"], row["MarketCap_BTC"])
				self.cursor.execute(sql)
				self.db.commit()
			except Exception as e:
				print(e)
				pass

	def get_multipliers(self):
		sql = "SELECT sectorTicker, multiplier FROM sectors"
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

	def existing_account(self, email, username):
		sql = "SELECT email, username FROM coinindexcap.users"
		self.cursor.execute(sql)

		df = pd.DataFrame(list(self.cursor.fetchall()), 
			columns=['email', 'username'])

		if email in list(df['email']):
			return fl_mes.email_already_exists
		elif username in list(df['username']):
			return fl_mes.username_already_exists
		else:
			return False



	def validate_user(self, email, password):
		hashed_password = hashlib.md5(password.encode()).hexdigest()
		sql = "SELECT email, password FROM coinindexcap.users WHERE email = '{}'".format(email)
		self.cursor.execute(sql)

		if self.cursor.rowcount == 0:
			return  fl_mes.email_not_in_db
		
		raw_tuple = self.cursor.fetchone()
		record = pd.Series({"email": raw_tuple[0], "password": raw_tuple[1]})

		if hashed_password == record['password']:
			return True
		else:
			return fl_mes.wrong_password

	def register_user(self, email, username, password, first_name, last_name, private_key='NULL'):
		hashed_password = hashlib.md5(password.encode()).hexdigest()
		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		sql = "INSERT INTO coinindexcap.users VALUES(NULL, '{em}', '{pw}', '{un}', '{pk}', 'user', '{ac}', '{fn}', '{ln}')".format(
			em=email, un=username, pw=hashed_password, pk=random.randint(1,101), ac=timestamp,
			fn=first_name, ln=last_name)

		try:
			self.cursor.execute(sql)
			self.db.commit()

			return True
		except Exception as e:
			return e
