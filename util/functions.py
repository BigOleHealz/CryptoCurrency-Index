import logging
from cryptocmd import CmcScraper
import pandas as pd, sqlparse, pymysql
from static.credentials import db_creds

def df_to_sql_minutely(table_name, df):
	sql = "INSERT IGNORE INTO coinindexcap.{tbl} VALUES ".format(tbl=table_name)

	for i, row in df.iterrows():
		sql += "(null, '{tkr}', '{ts}', '{pusd}', null, '{mktcp}', '{vlm}')".format(
			tkr=row['Ticker'], ts=row['TimeStampID'], pusd=row['Price_USD'], mktcp=row['MarketCap_USD'], vlm=row['Volume24hr_USD'])
		
		if i != len(df) - 1: sql += ','
		else: sql += ';'

	return sql

def execute_sql(statement: str, commit=True):
	db = pymysql.connect(db_creds['endpoint'], db_creds['username'], 
			db_creds['password'], db_creds['dbname'])
	cursor = db.cursor()

	try:
		for stmnt in sqlparse.split(statement):
			cursor.execute(stmnt)
		if commit: db.commit()
		return list(cursor.fetchall())
	except Exception as e:
		return e

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