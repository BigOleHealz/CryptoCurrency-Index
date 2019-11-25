get_supported_coins = """
	SELECT
		coin_ticker,
		coin_name,
		sector_ticker
	FROM coinindexcap.coins"""

get_minutely_coin_data = """
	SELECT 
		TimeStampID,
		Price_USD,
		Price_BTC,
		MarketCap_USD,
		Volume24hr_USD
	FROM coinindexcap.minutely_data
	WHERE Ticker = '{tkr}'"""

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
	ORDER BY a.TimeStampID;"""

get_market_name = """
	SELECT market 
	FROM coinindexcap.sectors 
	WHERE ticker = '{tkr}';"""

insert_coin = """
	INSERT INTO coinindexcap.coins
	VALUES('{tkr}', '{nm}', '{sctr}')"""

insert_coin_history = """
	CREATE TABLE coinindexcap.tmp_tbl_coins LIKE coinindexcap.minutely_data;
	INSERT coinindexcap.tmp_tbl_coins SELECT * FROM coinindexcap.minutely_data;
	{upsrt}
	RENAME TABLE coinindexcap.minutely_data TO coinindexcap.tmp_tbl_delete,
		coinindexcap.tmp_tbl_coins TO coinindexcap.minutely_data;
	DROP TABLE coinindexcap.tmp_tbl_delete;
	"""