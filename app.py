#import library
import logging
import sys
import yaml
import pandas
from pandas import DataFrame as df
from datetime import datetime

#import modules
from historicaldata import HistorialData
from analyzer import indicators

def main():
    # Set up logger
    # try:
    # 	conf=yaml.load(open("conf.yml"))
    # except Exception as e:
    # 	logging.error("Cant load configuration files or there are errors in configuration")
    # 	#raise e
	conf=yaml.load(open("conf.yml"))
	technical_data=indicators()
	logging.basicConfig(
	        format="%(message)s",
	        stream=sys.stdout,
	        level=logging.INFO,
	    )

	exchange_conf=conf["exchange"].keys()
	ex=HistorialData(exchange_conf)
	for exchange in exchange_conf:
		logging.info("Get historical data from %s",exchange)
		data=ex.get_historical_data(conf["exchange"][exchange]["symbol"],exchange,conf["exchange"][exchange]["time_unit"],conf["exchange"][exchange]["candles"])
		data=to_dataframe(data)
		print data
		print len(data)
		# print technical_data.stochastic_rsi_cal(data)

def to_dataframe(data_array):
	dataframe = df(data_array)
	dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
	dataframe['datetime'] = dataframe.timestamp.apply(
		lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c')))
        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)
        return dataframe

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
