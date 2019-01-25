#!/usr/bin/env python3
"""
    Purpose: Pull Data for timestamp and insert it into minutely_coin_data
    	and minutely_sector_data
    Steps:
        - Pull Data for all supported coins from CoinMarketCap API
        - Insert raw price quotes into minutely_coin_data
        - Crunch market cap sums and divide by normalizing multiplier to get 
        	aggregated sector values to insert into minutely_sector_data
    Usage: ./cron.py
"""

from big_ol_db import BigOlDB

BigOlDB = BigOlDB()

def run():
	BigOlDB.sql_update_minutely_table()
	BigOlDB.sql_update_sector_minutely_table()

if __name__ == '__main__':
	run()
