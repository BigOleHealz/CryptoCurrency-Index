import pandas as pd
from cryptocmd import CmcScraper
from util import functions as util, sql as queries

class Coin:

	def __init__(self, ticker):
		self.ticker = ticker

	def get_historical_quotes(self) -> pd.DataFrame:
		scraper = CmcScraper(self.ticker)
		df = scraper.get_dataframe()
		return pd.DataFrame({'_id' : 'null', 'Ticker' : self.ticker, 'TimeStampID' : 
			df['Date'], 'Price_USD' : df['Close'], 'Price_BTC' : 'null', 
			'MarketCap_USD' : df['Market Cap'], 'Volume24hr_USD' : df['Volume']})

	def get_minutely_coin_data(self, start='2010-01-01') -> pd.DataFrame:
		sql = queries.get_minutely_coin_data.format(tkr=self.ticker, dt=start)
		db, cursor = util.db_connect()
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["TimeStampID", 
			"Price_USD", "Price_BTC", "MarketCap_USD", "Volume24hr_USD"])
		return df

	def get_coin_moving_average(self, window=10) -> pd.DataFrame:
		sql = queries.get_coin_moving_average.format(tkr=self.ticker, wndw=window)
		db, cursor = util.db_connect()
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["TimeStampID", 
			"Price_USD"])
		return df

	def get_sector(self):
		sql = queries.get_coin_sector.format(tkr=self.ticker)
		db, cursor = util.db_connect()
		cursor.execute(sql)
		
		return cursor.fetchall()[0][0]
