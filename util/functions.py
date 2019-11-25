from cryptocmd import CmcScraper
import pandas as pd

def df_to_sql(table_name, df):
	sql = "INSERT IGNORE INTO coinindexcap.{tbl} VALUES ".format(tbl=table_name)

	for i, row in df.iterrows():
		sql += "(null, '{tkr}', '{ts}', '{pusd}', null, '{mktcp}', '{vlm}')".format(
			tkr=row['Ticker'], ts=row['TimeStampID'], pusd=row['Price_USD'], mktcp=row['MarketCap_USD'], vlm=row['Volume24hr_USD'])
		
		if i != len(df) - 1: sql += ','
		else: sql += ';'

	return sql

