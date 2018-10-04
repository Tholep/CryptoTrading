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
from strategy import macd_rsi_stochrsi
from utilities import to_dataframe
#set up logger
try:
	conf=yaml.load(open("conf/conf_recommender.yml"))
except Exception as e:
	raise e
try:
	if not os.path.exists("logs"):
		os.makedirs("logs")
	if not os.path.exists("charts"):
		os.makedirs("charts")
except Exception as e:
		logger.error("Cannot create neccessary directories for operations",exc_info=True)
logging.config.dictConfig(conf["logging"])
logger = logging.getLogger(__name__)	

def main():
	symbol_conf=conf["symbol"]
	ex=HistorialData(symbol_conf)
	for symbol in symbol_conf.keys():
		exchange=symbol_conf[symbol]["exchange"]
		time_unit=symbol_conf[symbol]["time_unit"]
		candles=symbol_conf[symbol]["candles"]
		#get historical data from symbol and symbol identified
		logger.debug("Get historical data %s:%s",exchange,symbol)
		try:
			data=ex.get_historical_data(symbol,exchange,time_unit,candles)
		except Exception as e:
			logger.error("Error in retrieving historical data for %s",symbol,exc_info=True)
			continue
		
		data=to_dataframe(data)
		# Aplly strategy(s) to collected data
		for st in symbol_conf[symbol]["strategies"]:
			klass=globals()[st]
			tatics=klass(data,symbol,symbol_conf[symbol],conf["indicators"],bruteforce=True)
			result=tatics.launch()
			if isinstance(result,list):
				#check configuration and update with new parameters if having
				if "indicators" in symbol_conf[symbol]:
					# stochastic RSI parameters
					if symbol_conf[symbol]["indicators"]["stoch_rsi"]["period"] != trading_result["period"]:
						logger.info("Change stoch_rsi_period from %s to %s", str(symbol_conf[symbol]["indicators"]["stoch_rsi"]["period"]),str(trading_result["period"]))
						symbol_conf[symbol]["indicators"]["stoch_rsi"]["period"] = int(trading_result["period"])

					if symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_k"] != trading_result["fast_k_period"]:
						logger.info("Change stoch_rsi_fast_k from %s to %s", str(symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_k"]),str(trading_result["fast_k_period"]))
						symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_k"] = int(trading_result["fast_k_period"])

					if symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_d"] != trading_result["fast_d_period"]:
						logger.info("Change stoch_rsi_fast_d from %s to %s", str(symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_d"]),str(trading_result["fast_d_period"]))
						symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_d"] = int(trading_result["fast_d_period"])
					#selling indicators
					if symbol_conf[symbol]["indicators"]["selling"]["rsi"] != trading_result["selling_rsi"]:
						logger.info("Change selling_rsi from %s to %s", str(symbol_conf[symbol]["indicators"]["selling"]["rsi"]),str(trading_result["selling_rsi"]))
						symbol_conf[symbol]["indicators"]["selling"]["rsi"] = int(trading_result["selling_rsi"])

					if symbol_conf[symbol]["indicators"]["selling"]["rsi_bullish"] != trading_result["selling_rsi_bullish"]:
						logger.info("Change selling_rsi_bullish from %s to %s", str(symbol_conf[symbol]["indicators"]["selling"]["rsi_bullish"]),str(trading_result["selling_rsi_bullish"]))
						symbol_conf[symbol]["indicators"]["selling"]["rsi_bullish"] = int(trading_result["selling_rsi_bullish"])

					if symbol_conf[symbol]["indicators"]["selling"]["fast_k"] != trading_result["selling_stoch_rsi"]:
						logger.info("Change selling_stoch_rsi from %s to %s", str(symbol_conf[symbol]["indicators"]["selling"]["fast_k"]),str(trading_result["selling_stoch_rsi"]))
						symbol_conf[symbol]["indicators"]["selling"]["rsi"] = int(trading_result["selling_rsi"])

					#buying indicators
					if symbol_conf[symbol]["indicators"]["buying"]["rsi"] != trading_result["buying_rsi"]:
						logger.info("Change buying_rsi from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["rsi"]),str(trading_result["buying_rsi"]))
						symbol_conf[symbol]["indicators"]["buying"]["rsi"] = int(trading_result["buying_rsi"])

					if symbol_conf[symbol]["indicators"]["buying"]["rsi_bullish"] != trading_result["buying_rsi_bullish"]:
						logger.info("Change buying_rsi_bullish from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["rsi_bullish"]),str(trading_result["buying_rsi_bullish"]))
						symbol_conf[symbol]["indicators"]["buying"]["rsi_bullish"] = int(trading_result["buying_rsi_bullish"])

					if symbol_conf[symbol]["indicators"]["buying"]["fast_k"] != trading_result["buying_stoch_rsi"]:
						logger.info("Change buying_stoch_rsi from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["fast_k"]),str(trading_result["buying_stoch_rsi"]))
						symbol_conf[symbol]["indicators"]["buying"]["fast_k"] = int(trading_result["buying_stoch_rsi"])


					if symbol_conf[symbol]["indicators"]["buying"]["confirmed_bullish"] != trading_result["buying_confirmed_pullish"]:
						logger.info("Change buying_confirmed_pullish from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["confirmed_bullish"]),str(trading_result["buying_confirmed_pullish"]))
						symbol_conf[symbol]["indicators"]["buying"]["confirmed_bullish"] = int(trading_result["buying_confirmed_pullish"])

					if symbol_conf[symbol]["indicators"]["buying"]["rsi_midpoint"] != trading_result["buying_rsi_midpoint"]:
						logger.info("Change buying_rsi_midpoint from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["rsi_midpoint"]),str(trading_result["buying_rsi_midpoint"]))
						symbol_conf[symbol]["indicators"]["buying"]["rsi_midpoint"] = int(trading_result["buying_rsi_midpoint"])


					if symbol_conf[symbol]["indicators"]["buying"]["macdhist"] != trading_result["buying_macdhist"]:
						logger.info("Change buying_macdhist from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["macdhist"]),str(trading_result["buying_macdhist"]))
						symbol_conf[symbol]["indicators"]["buying"]["macdhist"] = int(trading_result["buying_macdhist"])
				else:
					indicators={"selling":{"rsi":int(trading_result["selling_rsi"]),"rsi_bullish":int(trading_result["selling_rsi_bullish"]), "fast_k":int(trading_result["selling_stoch_rsi"])},\
						"buying":{"rsi":int(trading_result["buying_rsi"]),"rsi_bullish":int(trading_result["buying_rsi_bullish"]), "fast_k":int(trading_result["buying_stoch_rsi"]),\
						"confirmed_bullish":int(trading_result["buying_confirmed_pullish"]),"rsi_midpoint":int(trading_result["buying_rsi_midpoint"]),\
						"macdhist":int(trading_result["buying_macdhist"])},\
						"stoch_rsi":{"period":int(trading_result["period"]),"fast_k":int(trading_result["fast_k_period"]),"fast_d":int(trading_result["fast_d_period"])}}
					symbol_conf[symbol]["indicators"]=indicators

    #Automatically update configuration file
	conf["symbol"]=symbol_conf
	with open('conf/conf_recommender.yml', 'w') as outfile:
		yaml.dump(conf, outfile, default_flow_style=False)				
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
		logger.info("Terminating process...")
		sys.exit(0)
