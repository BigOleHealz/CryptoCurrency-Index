import pandas as pd
from util import functions as util, sql as queries

class Sector:

	def __init__(self, sector: str):
		self.sector = sector

	def get_sector_data(self) -> pd.DataFrame:
		sql = queries.get_sector_mktcap_from_minutely_data.format(sctr=self.sector)
		db, cursor = util.db_connect()
		cursor.execute(sql)
		df = pd.DataFrame(list(cursor.fetchall()), columns=["TimeStampID",
			"MarketCap_USD", "Volume24hr_USD", "SectorTicker"])

		return df

	def get_coins(self):
		sql = queries.get_coins_in_sector.format(sctr=self.sector)
		db, cursor = util.db_connect()
		cursor.execute(sql)

		return [elem[0] for elem in list(cursor.fetchall())]

	def populate_sector(self):
s		sql = queries.populate_sector_from_coins.format(sctr=self.sector)
		db, cursor = util.db_connect()

		import pdb; pdb.set_trace()  # breakpoint f48268b4 //

		cursor.execute(sql)
		db.commit()