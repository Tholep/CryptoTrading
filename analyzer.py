""" Technical analysis indicators
"""

import math

import pandas
from talib import abstract




class indicators():
    def rsi_cal(self, historical_data, period_count=14):
        """Performs an RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our RSI.
        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        #dataframe = self.convert_to_dataframe(historical_data)
        rsi_values = abstract.RSI(historical_data, period_count).to_frame()
        rsi_values.fillna(value=0, inplace=True)
        rsi_values.rename(columns={rsi_values.columns[0]: 'rsi'}, inplace=True)
        return rsi_values

    def macd_cal(self, historical_data):
        """Performs a macd analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
         Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        macd_values = abstract.MACD(historical_data).iloc[:]
        macd_values.fillna(value=0, inplace=True)

        return macd_values

    def stochastic_rsi_cal(self, historical_data, timeperiod=14, fastk_period=3, fastd_period=3):
        """Performs a Stochastic RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            timeperiod: Default 14, time to calculate RSI.
            fastk: Default is 3.
            fastd: Default is 3, moving average of fastk.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        stoch_rsi=abstract.STOCHRSI(historical_data,timeperiod,fastk_period,fastd_period)
        return stoch_rsi


