get_supported_coins = """
	SELECT
		coin_ticker,
		coin_name,
		sector_ticker
	FROM coinindexcap.coins
	"""

get_minutely_coin_data = """
	SELECT 
		TimeStampID,
		Price_USD,
		Price_BTC,
		MarketCap_USD,
		Volume24hr_USD
	FROM coinindexcap.minutely_data
	WHERE Ticker = '{tkr}'
	AND TimeStampID > '{dt}'
	"""

get_coin_moving_average = """
	SELECT
		a.TimeStampID,
		Round( 
			( SELECT SUM(b.Price_USD) / COUNT(b.Price_USD)
				FROM minutely_data AS b
				WHERE DATEDIFF(a.TimeStampID, b.TimeStampID) BETWEEN 0 AND {wndw}
			),
		2 ) 
	AS 'MovingAvg'
	FROM coinindexcap.minutely_data AS a
	WHERE Ticker = '{tkr}'
	ORDER BY a.TimeStampID;
	"""

get_market_name = """
	SELECT market 
	FROM coinindexcap.sectors 
	WHERE ticker = '{tkr}';"""

insert_coin = """
	DELETE FROM coinindexcap.coins WHERE coin_ticker = '{tkr}';
	INSERT INTO coinindexcap.coins VALUES('{tkr}', '{nm}', '{sctr}');
	"""

drop_table = "DROP TABLE IF EXISTS {tbl};"

insert_coin_history = """
	DROP TABLE IF EXISTS coinindexcap.tmp_tbl_minutely;
	DROP TABLE IF EXISTS coinindexcap.old_tbl_delete;""" + """
	CREATE TABLE coinindexcap.tmp_tbl_minutely LIKE coinindexcap.minutely_data;
	INSERT coinindexcap.tmp_tbl_minutely SELECT * FROM coinindexcap.minutely_data;
	{upsrt}
	RENAME TABLE coinindexcap.minutely_data TO coinindexcap.old_tbl_delete,
		coinindexcap.tmp_tbl_minutely TO coinindexcap.minutely_data;
	DROP TABLE coinindexcap.old_tbl_delete;
	"""

get_sector_mktcap_from_minutely_data = """
	SELECT 
		a.TimeStampID,
		SUM(SQRT(a.MarketCap_USD)),
		SUM(a.Volume24hr_USD),
		b.sector_ticker
	FROM
		coinindexcap.minutely_data AS a
			LEFT JOIN
		(SELECT 
			coin_ticker, sector_ticker
		FROM
			coinindexcap.coins) AS b ON a.Ticker = b.coin_ticker
	WHERE b.sector_ticker = '{sctr}'
	GROUP BY a.TimeStampID , b.sector_ticker
	ORDER BY a.TimeStampID;
	"""

get_coin_sector = """
	SELECT sector_ticker
	FROM coinindexcap.coins
	WHERE coin_ticker = '{tkr}';
	"""

get_coins_in_sector = """
	SELECT coin_ticker 
	FROM coinindexcap.coins 
	WHERE sector_ticker = '{sctr}'
"""

populate_sector_from_coins = """
	INSERT coinindexcap.sector_minutely_data 
		SELECT * FROM 
			(SELECT
				'NULL',
				a.TimeStampID AS timestampid,
				SUM(SQRT(a.MarketCap_USD)) AS marketcap_usd,
				SUM(a.Volume24hr_USD) AS volume24hr_usd,
				b.sector_ticker AS sector_ticker
			FROM coinindexcap.minutely_data AS a
			LEFT JOIN
				(SELECT coin_ticker, sector_ticker
				FROM coinindexcap.coins)
				AS b ON a.Ticker = b.coin_ticker
				-- WHERE b.sector_ticker = '{sctr}'
				GROUP BY
					a.TimeStampID, 
					b.sector_ticker
				ORDER BY a.TimeStampID) AS c;
	"""
