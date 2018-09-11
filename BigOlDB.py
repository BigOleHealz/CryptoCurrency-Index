import datetime, numpy, time, requests, json, MySQLdb, threading, pandas as pd
from CoinClassifications import CoinClassifications
from datetime import datetime
from operator import itemgetter

class BigOlDB:    
    
    # Connect to DB
    file = open("C://Users/mth47/workspace/CoinIndexCap_Credentials.txt", "r")
    username, password, dbname, endpoint = file.read().splitlines()
    db = MySQLdb.connect(endpoint, username, password, dbname)
    cursor = db.cursor()

    # Get JSON of coin data from CoinMarketCap API
    tickerURL = "https://api.coinmarketcap.com/v1/ticker/?start=0&limit=1700"
    coin_data_list = requests.get(tickerURL).json()
    
    coinClass = CoinClassifications()
    db, cursor = coinClass.dbConnect()
    supported_coins = coinClass.getSupportedCoins()

    sector_dict = coinClass.getCoinSectorDict()
    sector_name_dict = coinClass.getCoinNameSectorDict()
    
    coin_data_dict_tkr = {} # Dict for all price data indexed by Ticker
    for indiv_coin_data_dict in coin_data_list:
        if indiv_coin_data_dict["symbol"] in supported_coins:
            coin_data_dict_tkr[indiv_coin_data_dict["symbol"]] = indiv_coin_data_dict

    def updateCurrentQuotes(self, tickerURL = "https://api.coinmarketcap.com/v1/ticker/?start=0&limit=1700"):
        self.coin_data_list = requests.get(tickerURL).json()

        for indiv_coin_data_dict in self.coin_data_list:
            if indiv_coin_data_dict["symbol"] in self.supported_coins:
                self.coin_data_dict_tkr[indiv_coin_data_dict["symbol"]] = indiv_coin_data_dict

    def sqlInsertCoin(self, ticker, sector_ticker, sector_name):
    
        sql = "insert into coins VALUES('%s', '%s', '%s', '%s')" % (ticker, self.coin_data_dict_tkr[ticker]["name"], sector_ticker, sector_name)
        self.cursor.execute(sql)
        self.db.commit()
    
    def sqlUpdateTimesTable(self, ts):
        
        timestamp = ts
        day = timestamp.strftime('%Y-%m-%d')
        time = timestamp.strftime('%H:%M:%S')
        
        sql = "insert into timestamps VALUES('%s', '%s', '%s')" % (timestamp, day, time)
        
        try:
            self.cursor.execute(sql) # Don't commit yet because the minutely_data table needs a record that corresponds to the date
        except:
            pass
        
        return timestamp
        
    def sqlUpdateMinutelyTable(self):
    
        timestamp = datetime.now()

        self.updateCurrentQuotes()
        
        for key in self.supported_coins:
            if self.coin_data_dict_tkr[key]['market_cap_usd']:

                ticker = self.coin_data_dict_tkr[key]['symbol'] #string
                price_usd = round(float(self.coin_data_dict_tkr[key]['price_usd']), 8) #float
                price_btc = round(float(self.coin_data_dict_tkr[key]['price_btc']), 8) #float
                market_cap_usd = round(float(self.coin_data_dict_tkr[key]['market_cap_usd']), 8) #float
                volume_24hr = round(float(self.coin_data_dict_tkr[key]['24h_volume_usd']), 8) #float
                
                try:
                    sql = "insert into minutely_data VALUES(null, '%s', '%s', '%s', '%s', '%s', '%s')" % (ticker, timestamp, price_usd, price_btc, market_cap_usd, volume_24hr)
                    self.cursor.execute(sql)
                    self.db.commit()
                except Exception as e:
                    print(e)
                    pass

        self.sqlUpdateTimesTable(timestamp)
        
        self.sqlUpdateMinutelySectorTable(timestamp)

    def sqlUpdateCoinsTable(self):
        
        for sector in self.sector_dict:
            
            for ticker in self.sector_dict[sector]:
                
                sql = "insert into coins VALUES('%s', '%s', '%s', '%s')" % (ticker, self.coin_data_dict_tkr[ticker]["name"], sector, self.sector_name_dict[sector])
                
                try:
                    self.cursor.execute(sql)
                    self.db.commit()
                except:
                    pass

    # Return Normalizing multiplier for sector
    def getMultiplier(self, ticker):
        sql = "select Multiplier from sectors where SectorTicker = '" + ticker + "';"
        self.cursor.execute(sql)
        result = float(self.cursor.fetchone()[0])
        
        return result

    def sqlUpdateMinutelySectorTable(self, timestamp): # Pass in a timestamp for anargument so that all records in the database will be associated with a time 

        supported_sectors = CoinClassifications().getSupportedSectors() # ['XPA', 'XPL', 'XE', 'XSC', 'XF', 'XPR']

        for sector in supported_sectors:
            try:
                multiplier = self.getMultiplier(sector)

                self.updateCurrentQuotes() # Update price quotes
                btc_price = float(self.coin_data_dict_tkr['BTC']['price_usd']) # Get BTC price for conversions

                sector_coins = CoinClassifications().getCoinsInSector(sector) # Ex: 'XPA' -> ['BTC', 'LTC', 'BTG', 'BCH', 'DOGE']
                
                mkt_cap_usd = sum(map(float, [self.coin_data_dict_tkr[coin]['market_cap_usd'] for coin in sector_coins])) # Sum of all Market Caps in sector
                
                etf_price_usd = mkt_cap_usd * multiplier # Normalize 
                etf_price_btc = etf_price_usd / btc_price
                mkt_cap_btc = mkt_cap_usd / btc_price

                sql = "insert into sector_minutely_data VALUES(null, '%s', '%s', '%s', '%s', '%s', '%s')" % (sector, timestamp, etf_price_usd, etf_price_btc, mkt_cap_usd, mkt_cap_btc)
                self.cursor.execute(sql)
                self.db.commit()

            except Exception as e:
                print("Error on sector market cap table", e)

    def getMinutelyCoinData(self, ticker):

        sql = "select TimeStampID, Price_USD, Price_BTC, MarketCap_USD from minutely_data where Ticker = '" + ticker + "'"

        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        timestamps = [quote[0] for quote in results]
        prices_usd = [quote[1] for quote in results]
        prices_btc = [quote[2] for quote in results]
        marketcap_usd = [quote[3] for quote in results]

        dict = {'Timestamp' : timestamps, 'PriceUSD' : prices_usd, 'PriceBTC' : prices_btc, 'MarketCapUSD' : marketcap_usd}
        df = pd.DataFrame(dict)
        return df

    def getMinutelySectorData(self, ticker):

        sql = "select TimeStampID, Price_USD, Price_BTC, MarketCap_USD, MarketCap_BTC from sector_minutely_data where Ticker = '" + ticker + "';"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        timestamps = [quote[0] for quote in results]
        prices_usd = [quote[1] for quote in results]
        prices_btc = [quote[2] for quote in results]
        mktcap_usd = [quote[3] for quote in results]
        mktcap_btc = [quote[4] for quote in results]

        return timestamps, prices_usd, prices_btc, mktcap_usd, mktcap_btc


