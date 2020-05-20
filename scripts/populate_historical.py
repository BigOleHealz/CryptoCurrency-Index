from classes.big_ol_db import BigOlDB

def insert_coin_history_to_db(df):
	ticker = df.iloc[0]['Ticker']
	# sql_drop_old_tmp_tbl = "DROP TABLE IF EXISTS coinindexcap.tmp_tbl_coins;"
	sql_create_tmp = "CREATE TABLE coinindexcap.tmp_tbl_coins LIKE coinindexcap.minutely_data;"
	sql_copy_tbl = "INSERT coinindexcap.tmp_tbl_coins SELECT * FROM coinindexcap.minutely_data;"
	sql_upsert = df_to_sql('tmp_tbl_coins', df)
	sql_tbl_swap = """RENAME TABLE coinindexcap.minutely_data TO coinindexcap.tmp_tbl1,
		coinindexcap.tmp_tbl_coins TO coinindexcap.minutely_data;"""
	sql_drop_new_tmp_tbl = "DROP TABLE coinindexcap.tmp_tbl1;"
	db, cursor = BigOlDB.db_connect()

	# cursor.execute(sql_drop_old_tmp_tbl)
	cursor.execute(sql_create_tmp)
	cursor.execute(sql_copy_tbl)
	cursor.execute(sql_upsert)
	cursor.execute(sql_tbl_swap)
	cursor.execute(sql_drop_new_tmp_tbl)
	
	db.commit()


if __name__ == '__main__':
	ticker = 'BTC'
	data = get_historical_quotes(ticker)
	insert_coin_history_to_db(data)
