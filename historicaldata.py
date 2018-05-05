"""Interface for querying historical data from specified exchange
"""

import ccxt
import logging
#from tenacity import retry, retry_if_exception_type, stop_after_attempt

class HistorialData(object):


    def __init__(self, exchange_conf):
        """Initializes HistoricalData class

        Args:
            exchange_conf (dictionary taken from conf.yml): A dictionary coins/tokens with an associated market and a desired time frame to obtain data
        """
        self.exchanges = dict() 
        # Loads exchanges using ccxt.
        for exchange in exchange_conf:
         
            new_exchange = getattr(ccxt, exchange)({"enableRateLimit": True})
            
            # sets up api permissions for user if given
            if new_exchange:
                self.exchanges[exchange] = new_exchange
                logging.info("Loaded exchange: %s", exchange)
            else:
                logging.error("Unable to load exchange %s", exchange)

    def get_historical_data(self, symbol, exchange, time_unit="1d", limit=100):
        """Get historical OHLCV for a symbol pair

        Decorators:
            retry

        Args:
            symbol (str): Contains the symbol to operate on i.e. BURST/BTC
            exchange (str): Contains the exchange to fetch the historical data from.
            time_unit (str): A string specifying the ccxt time unit i.e. 5m or 1d.
            limit (int, optional): Maximum number of candles to fetch data for.

        Returns:
            list: Contains a list of lists which contain timestamp, open, high, low, close, volume.
        """
        try:
            
            historical_data = self.exchanges[exchange].fetch_ohlcv(symbol,timeframe=time_unit,limit=limit)
        except Exception as e:
            raise e
        

        if not historical_data:
            #logging.error("Can't fetch historical data for %s - %s", (symbol,exchange))
            raise ValueError('No historical data provided returned by exchange.')
            
        # Sort by timestamp in ascending order
        historical_data.sort(key=lambda d: d[0])

        # time.sleep(self.exchanges[exchange].rateLimit / 1000)

        return historical_data
