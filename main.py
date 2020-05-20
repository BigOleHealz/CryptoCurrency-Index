
from classes.big_ol_db import BigOlDB as bodb
from classes.coin import Coin
from classes.sector import Sector
# df = bodb.get_sector_data('XPA')
# df = bodb.insert_coin(ticker='DASH', name="Dash", sector="XPR")
# df = bodb.insert_coin(ticker='XRP', name="Ripple", sector="XPR")
# df = bodb.get_historical_quotes('BTC')
bodb.update_minutely_table()

# sector = Sector('XPR')
# bodb.insert_coin(ticker='XRP', name='Ripple', sector='XPR')
import pdb; pdb.set_trace()  # breakpoint a607b05b //
