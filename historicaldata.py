"""Interface for querying historical data from specified symbol
"""
import ccxt
import logging
import re
from datetime import datetime, timedelta
import time
logger = logging.getLogger(__name__)

class HistorialData(object):


    def __init__(self, symbol_conf):
        """Initializes HistoricalData class

        Args:
            symbol_conf (dictionary taken from conf.yml): A dictionary coins/tokens with an associated market and a desired time frame to obtain data
        """
        self.exchanges = dict() 
        # Loads symbols using ccxt.
        for symbol in symbol_conf.keys():
            exchange=symbol_conf[symbol]["exchange"]
            new_exchange = getattr(ccxt, exchange)({"enableRateLimit": True})
            
            # sets up api permissions for user if given
            if exchange in self.exchanges:
                pass
            elif new_exchange:
                self.exchanges[exchange] = new_exchange
                logger.info("Loaded exchange: %s", exchange)
            else:
                logger.error("Unable to load exchange %s", exchange)

    def get_historical_data(self, symbol, exchange, time_unit="1d", limit=100):
        """Get historical OHLCV for a symbol pair

        Decorators:
            retry

        Args:
            symbol (str): Contains the symbol to operate on i.e. BURST/BTC
            exchange (str): Contains the exchnageto fetch the historical data from.
            time_unit (str): A string specifying the ccxt time unit i.e. 5m or 1d.
            limit (int, optional): Maximum number of candles to fetch data for.

        Returns:
            list: Contains a list of lists which contain timestamp, open, high, low, close, volume.
        """
        timeframe_regex = re.compile('([0-9]+)([a-zA-Z])')
        timeframe_matches = timeframe_regex.match(time_unit)
        time_quantity = timeframe_matches.group(1)
        time_period = timeframe_matches.group(2)

        timedelta_values = {
            'm': 'minutes',
            'h': 'hours',
            'd': 'days',
            'w': 'weeks',
            'M': 'months',
            'y': 'years'
        }
        
        timedelta_args = { timedelta_values[time_period]: int(time_quantity) }

        delta = timedelta(**timedelta_args)

        max_days_date = datetime.utcnow() - (limit * delta)

        start_date = int((max_days_date - datetime(1970,1,1)).total_seconds() * 1000)
        try:
            
            historical_data = self.exchanges[exchange].fetch_ohlcv(symbol,timeframe=time_unit,since=start_date)
        except Exception as e:
            raise e
        

        if not historical_data:
            #logger.error("Can't fetch historical data for %s - %s", (symbol,symbol))
            logger.info('No historical data provided returned by %s for symbol %s.',(exchange,symbol))
            
        # Sort by timestamp in ascending order
        historical_data.sort(key=lambda d: d[0])

        time.sleep(self.exchanges[exchange].rateLimit / 1000)

        return historical_data
