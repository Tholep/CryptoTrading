""" Technical analysis indicators
"""

import math
import numpy
import pandas
from talib import abstract


class indicators():
    def __init__(self):
        """
        Initialize the class
        """

    # def calculate_rsi_stoch_rsi(self,historical_data,indicators_conf):
    #     """Perform technical indicator calculation and add to the original data
    #     Args:
    #         historical_data: a historical_data contains historical data.
    #         indicators_conf: is a dictionary read from conf.yml to provide parameters for calculations.
    #     Returns:
    #         pandas.DataFrame: containing historical data and other indicators
    #     """
    #     #rsi=self.rsi_cal(historical_data,indicators_conf["rsi"]["period"])
    #     #macd=self.macd_cal(historical_data)

    #     #RSI and Stoch_RSI
    #     if indicators_conf["stoch_rsi"]["perido_range"]:

    #     else:
    #         stoch_rsi=self.stochastic_rsi_cal(historical_data,indicators_conf["stoch_rsi"]["period"],indicators_conf["stoch_rsi"]["fastk"],indicators_conf["stoch_rsi"]["fastd"])
    #     return pandas.concat([historical_data,rsi,macd,stoch_rsi],axis=1)
    
    def rsi_cal(self, historical_data, timeperiod=14):
        """Performs an RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            timeperiod (int, optional): Defaults to 14. The number of data points to consider for
                our RSI.
        Returns:
            pandas.DataFrame: A historical_data containing the indicators and hot/cold values.
        """

        #historical_data = self.convert_to_historical_data(historical_data)
        rsi_values = abstract.RSI(historical_data, timeperiod).to_frame()
        rsi_values.fillna(value=0, inplace=True)
        rsi_values.rename(columns={rsi_values.columns[0]: 'rsi'}, inplace=True)
        
        return rsi_values

    def macd_cal(self, historical_data):
        """Performs a macd analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
         
         
        Returns:
            pandas.DataFrame: A historical_data containing the indicators and hot/cold values.
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
            pandas.DataFrame: A historical_data containing the indicators and hot/cold values.
        """

        # stoch_rsi=abstract.STOCHRSI(historical_data,timeperiod,fastk_period,fastd_period)
        # stoch_rsi.fillna(value=0, inplace=True)
        rsi_timeperiod = timeperiod
        rsi_values = abstract.RSI(historical_data, rsi_timeperiod).to_frame()
        rsi_values.fillna(value=0, inplace=True)
        rsi_values.rename(columns={0: 'rsi'}, inplace=True)

        rsi_values = rsi_values.assign(stoch_rsi=numpy.nan)
        for index in range(timeperiod, rsi_values.shape[0]):
            start_index = index - timeperiod
            last_index = index + 1
            rsi_min = rsi_values['rsi'].iloc[start_index:last_index].min()
            rsi_max = rsi_values['rsi'].iloc[start_index:last_index].max()
            stoch_rsi = (100 * ((rsi_values['rsi'][index] - rsi_min) / (rsi_max - rsi_min)))
            rsi_values['stoch_rsi'][index] = stoch_rsi

        rsi_values['fast_k'] = rsi_values['stoch_rsi'].rolling(window=fastk_period).mean()
        rsi_values['fast_d'] = rsi_values['fast_k'].rolling(window=fastd_period).mean()
        rsi_values.fillna(value=0, inplace=True)
        
        return rsi_values



