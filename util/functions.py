import logging
from cryptocmd import CmcScraper
import pandas as pd, sqlparse, pymysql
from static.credentials import db_creds
from pypika import Query, Table

def df_to_sql(table, df):
	customers = Table(f'{table}_tmp')

	sql = Query.into(f'coinindexcap.{table}_tmp').insert(
		[tuple(row) for i, row in df.iterrows()])
	sql = str(sql).replace('"', '') + ';'
	return sql

def execute_sql(statement: str, commit=True):
	db = pymysql.connect(db_creds['endpoint'], db_creds['username'], 
			db_creds['password'], db_creds['dbname'])
	cursor = db.cursor()

	for stmnt in sqlparse.split(statement):
		cursor.execute(stmnt)
		import pdb; pdb.set_trace()  # breakpoint 1379f991 //

	if commit: db.commit()

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