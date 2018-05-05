"""Interface for querying historical data from specified exchange
"""

import re
import sys
import time
from datetime import datetime, timedelta

import ccxt
import structlog
#from tenacity import retry, retry_if_exception_type, stop_after_attempt

class HistorialData():


    def __init__(self, exchange_conf):
        """Initializes HistoricalData class

        Args:
            exchange_conf (dictionary taken from conf.yml): A dictionary coins/tokens with an associated market and a desired time frame to obtain data
        """

        self.logger = structlog.get_logger()

        self.exchanges = dict() 
        # Loads exchanges using ccxt.
        for exchange in exchange_conf.keys():
         
            new_exchange = getattr(ccxt, exchange)

            # sets up api permissions for user if given
            if new_exchange:
                self.exchanges[new_exchange.id] = new_exchange
            else:
                self.logger.error("Unable to load exchange %s", new_exchange)


    #@retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_historical_data(self, symbol, exchange, time_unit="1d", limit):
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
            if time_unit not in self.exchanges[exchange].timeframes:
                raise ValueError(
                    "{} does not support {} timeframe for OHLCV data. Possible values are: {}".format(
                        exchange,
                        time_unit,
                        list(self.exchanges[exchange].timeframes)
                    )
                )
        except AttributeError:
            self.logger.error(
                '%s interface does not support timeframe queries! We are unable to fetch data!',
                exchange
            )
            raise 


        if not start_date:
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

            epoch = datetime.utcfromtimestamp(0)

            timedelta_args = { timedelta_values[time_period]: int(time_quantity) }

            start_date_delta = timedelta(**timedelta_args)

            max_days_date = datetime.now() - (limit * start_date_delta)

            start_date = int((max_days_date - epoch).total_seconds() * 1000)

        historical_data = self.exchanges[exchange].fetch_ohlcv(
            symbol,
            timeframe=time_unit,
            since=start_date
        )

        if not historical_data:
            raise ValueError('No historical data provided returned by exchange.')

        # Sort by timestamp in ascending order
        historical_data.sort(key=lambda d: d[0])

        time.sleep(self.exchanges[exchange].rateLimit / 1000)

        return historical_data


    #@retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_exchange_markets(self, exchanges=[], markets=[]):
        """Get market data for all symbol pairs listed on all configured exchanges.

        Args:
            markets (list, optional): A list of markets to get from the exchanges. Default is all
                markets.
            exchanges (list, optional): A list of exchanges to collect market data from. Default is
                all enabled exchanges.

        Decorators:
            retry

        Returns:
            dict: A dictionary containing market data for all symbol pairs.
        """

        if not exchanges:
            exchanges = self.exchanges

        exchange_markets = dict()
        for exchange in exchanges:
            exchange_markets[exchange] = self.exchanges[exchange].load_markets()

            if markets:
                curr_markets = exchange_markets[exchange]

                # Only retrieve markets the users specified
                exchange_markets[exchange] = { key: curr_markets[key] for key in curr_markets if key in markets }

                for market in markets:
                    if market not in exchange_markets[exchange]:
                        self.logger.info('%s has no market %s, ignoring.', exchange, market)

            time.sleep(self.exchanges[exchange].rateLimit / 1000)

        return exchange_markets
