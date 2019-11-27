import pandas as pd
from util import functions as util

class Sector:

	def __init__(self, ticker: str):
		self.ticker = ticker

	def get_sector_data(self) -> pd.DataFrame:
		sql = queries.get_sector_mktcap_from_minutely_data.format(sctr=self.sector)
		db, cursor = util.db_connect()
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["TimeStampID",
			"MarketCap_USD", "Volume24hr_USD", "SectorTicker"])

		return df

	def get_coins(self):
		sql = "SELECT coin_ticker from coinindexcap.coins WHERE sector_ticker = '{sctr}"