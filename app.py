#import library
import logging
import logging.config
import sys
import yaml
import pandas
from pandas import DataFrame as df
from datetime import datetime

#import modules
from historicaldata import HistorialData
from notifier import TelegramNotifier
from strategy import strategy
#set up logger
try:
	conf=yaml.load(open("conf.yml"))
except Exception as e:
	raise e
logging.config.dictConfig(conf["logging"])
logger = logging.getLogger(__name__)

def to_dataframe(data_array):
	dataframe = df(data_array)
	dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
	dataframe['datetime'] = dataframe.timestamp.apply(
		lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c')))
        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)
        return dataframe

def main():

	try:
		telegram=TelegramNotifier(conf["notifier"]["telegram"]["api"],conf["notifier"]["telegram"]["chat_id"])
	except Exception as e:
		logger.error("Cannot load telegram object")
	

	symbol_conf=conf["symbol"]
	ex=HistorialData(symbol_conf)
	for symbol in symbol_conf.keys():
		exchange=symbol_conf[symbol]["exchange"]
		time_unit=symbol_conf[symbol]["time_unit"]
		candles=symbol_conf[symbol]["candles"]
		#get historical data from symbol and symbol identified
		logger.info("Get historical data %s:%s",exchange,symbol)
		try:
			data=ex.get_historical_data(symbol,exchange,time_unit,candles)
		except Exception as e:
			logger("Error in retrieving historical data for %s",symbol)
			pass
		
		data=to_dataframe(data)
		# Aplly strategy(s) to collected data
		logger.info("bruteforce strategies for %s",symbol)
		tatics=strategy(data,symbol_conf[symbol],conf["indicators"])
		results=tatics.strategy_launcher()

		#temporary test of results
		frame=df(results["macd_rsi_stochrsi_strategy"][0])
		frame.columns=["period","fast_k_period","fast_d_period","selling_rsi","selling_stoch_rsi","buying_rsi","busying_stoch_rsi","buying_confirmed_pullish","buying_rsi_pullish","buying_macdhist","balance","profit","recorded_transaction","recommendation"]
		frame=frame.sort_values("profit")
		logger.info("Results for symbol: %s",symbol)
		logger.info("%s",frame.iloc[-1])
		logger.info("Transaction details:")
		for ts in frame.iloc[-1]["recorded_transaction"]:
			logger.info("%s",ts)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
