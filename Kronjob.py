from BigOlDB import BigOlDB
from CoinClassifications import CoinClassifications
import datetime, time
from datetime import datetime

BigOlDB = BigOlDB()
CoinClassifications = CoinClassifications()

BigOlDB.sqlUpdateMinutelyTable()
