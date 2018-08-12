'''
This is a trading bot which will apply strategy and make trading with online exchanges or
with virtual wallet for testing purpose
'''
#import library
import logging
import logging.config
import sys
import yaml
import pandas
from pandas import DataFrame as df
from datetime import datetime
import os
#import modules
from historicaldata import HistorialData
from notifier import TelegramNotifier
from strategy import strategy

try:
	if not os.path.exists("logs"):
		os.makedirs("logs")
	if not os.path.exists("charts"):
		os.makedirs("charts")
except Exception as e:
	logger.error("Cannot create neccessary directories for operations",exc_info=True)
	raise e

#load configuration
try:
	conf=yaml.load(open("conf/conf_OMGETH.yml"))
except Exception as e:
	logger.error("Can't loat configuration file: conf/conf_OMGETH.yml")
	raise e

#set up logger
logging.config.dictConfig(conf["logging"])
logger = logging.getLogger(__name__)


#convert to data frame
def to_dataframe(data_array):
	dataframe = df(data_array)
	dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
	dataframe['datetime'] = dataframe.timestamp.apply(
		lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c')))
        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)
        return dataframe

def virtual_trading_bot(recommendation,price):
	#buy
	if recommendation=="buy bearish" or recommendation=="buy bullish" or recommendation=="buy bullish by macd":
		if source_wallet > 0:
			purchased_crypto=((source_wallet * percentage)/100)/price
			target_wallet+=purchased_crypto
			source_wallet-=(source_wallet * percentage)/100
			logger.info ("Purchase at %s price: %s tokens",(str(price),str(purchased_crypto)))
		else:
			logger.info ("There is not enough balance in the source wallet for the transaction")

	#sell
 	if recommendation=="sell bearish" or recommendation=="sell bullish":
		if target_wallet>0:
			source_wallet+=price * target_wallet
			target_wallet= 0
			logger.info ("Sell at %s price",str(price))
		else:
			logger.info ("There is no tokens to sell out")

def main():

	

	#load configuration
	symbol=conf["symbol"].keys()[0]
	#source wallet = ETH and target wall = OMG
	source_wallet=conf["symbol"][symbol]["wallet"]
	target_wallet=0
	percentage=conf["symbol"][symbol]["percentage"]
	symbol_conf=conf["symbol"][symbol]
	#get historical data
	ex=HistorialData(conf["symbol"])

	exchange=symbol_conf["exchange"]
	time_unit=symbol_conf["time_unit"]
	candles=symbol_conf["candles"]
	st=symbol_conf["strategies"][0]
	#get historical data from symbol and symbol identified
	logger.info("Get historical data %s:%s",exchange,symbol)
	try:
		data=ex.get_historical_data(symbol,exchange,time_unit,candles)
	except Exception as e:
		logger.error("Error in retrieving historical data for %s",symbol,exc_info=True)
		raise e
		
	data=to_dataframe(data)

	# Aplly strategy(s) to collected data
	logger.debug("Bruteforce strategies for %s",symbol)
	# use the recommendation system for sell/buy decision
	tatics=strategy(data,symbol,symbol_conf,conf["indicators"])
	results=tatics.strategy_launcher()
	if not results[st].empty:
	# At the moment, trading bot only uses 1 strategy for online trading
		trading_result= results[st]
		print str(trading_result)
		recommendation=trading_result["recommendation"]
		if recommendation != "no":
			virtual_trading_bot(recommendation,trading_result["recorded_transaction"][-1][2])
	else:
		logger.info ("There is no profitable for this token")				
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
		logger.info("Terminating process...")
		sys.exit(0)
