import MySQLdb

class CoinClassifications:
    
    # coin_sector_dict = {'XPA': ['BTC', 'LTC', 'BTG', 'BCH', 'DOGE'], 'XSC' : ['WTC', 'TRAC', 'MOD', 'AMB', 'WABI'], 'XPL' : ['ETH', 'NXT', 'EOS', 'ADA', 'LSK', 'NAS', 'NEO', 'ICX',  'ARK', 'SUB'], 'XF' : ['XRP', 'XLM', 'NANO', 'DASH', 'KIN', 'REQ'], 'XE' : ['BIX', 'BNB', 'HT', 'KCS', 'COSS'], 'XPR' :  ['XMR', 'NAV', 'PIVX', 'ZEC', 'CLOAK', 'ENG']}
    # coin_name_sector_dict = {'XPA' : 'Payment', 'XSC' : 'Supply Chain', 'XPL' : 'Platform', 'XF' : 'Financial', 'XE' : 'Exchange', 'XPR' : 'Privacy' }

    # Connect to DB
    file = open("C://Users/mth47/workspace/CoinIndexCap_Credentials.txt", "r")
    username, password, dbname, endpoint = file.read().splitlines()
    db = MySQLdb.connect(endpoint, username, password, dbname)
    cursor = db.cursor()

    db = MySQLdb.connect(endpoint, username, password, name)
    cursor = db.cursor()

    def dbConnect(self):
        return self.db, self.db.cursor()

    def getCoinsInSector(self, ticker):
        sql = "SELECT Ticker from coins where Sector = '" + ticker + "';"
        self.cursor.execute(sql)
        tickers = [elem[0] for elem in self.cursor.fetchall()]

        return tickers

    def getSupportedSectors(self):
        self.cursor.execute("SELECT SectorTicker from sectors;")
        results = self.cursor.fetchall()
        sector_tickers = [elem[0] for elem in results]

        return sector_tickers
    
    def getCoinSectorDict(self):
        return self.coin_sector_dict
    
    def getCoinNameSectorDict(self):
        return self.coin_name_sector_dict

    def getSupportedCoins(self):
        supported_coins_list = []
        for sector in self.getSupportedSectors():
            for ticker in self.coin_sector_dict[sector]:
                supported_coins_list.append(ticker)
                
        return supported_coins_list

