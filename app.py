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
		logger.info("Loaded telegram")
	except Exception as e:
		logger.error("Cannot load telegram object",exc_info=True)
	

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
			logger.error("Error in retrieving historical data for %s",symbol,exc_info=True)
			continue
		
		data=to_dataframe(data)
		# Aplly strategy(s) to collected data
		logger.info("bruteforce strategies for %s",symbol)
		tatics=strategy(data,symbol_conf[symbol],conf["indicators"])
		results=tatics.strategy_launcher()
		#logger.info(results)
		#temporary test of results
		for st in symbol_conf[symbol]["strategies"]:
			
			trading_result=results[st][0]
			#only process if there are strategies that are profitable
			if trading_result[0]!=None: #if None, only 1 value
			#for trading_result in strategy_result:
				message=symbol + ":" + st +"/n"
				frame=df(trading_result)
				frame.columns=["period","fast_k_period","fast_d_period","selling_rsi","selling_stoch_rsi","buying_rsi","buying_stoch_rsi","buying_confirmed_pullish","buying_rsi_pullish","buying_macdhist","balance","profit","recorded_transaction","recommendation"]
				frame=frame.sort_values("profit")
				logger.info("Results for symbol: %s",symbol)
				logger.info("\n%s",frame.iloc[-1])
				message+=str(frame.iloc[-1])+"\n"
				logger.info("Transaction details:")
				for ts in frame.iloc[-1]["recorded_transaction"]:
					logger.info("%s",ts)
					message+=str(ts)
				try:
					if frame.iloc[-1]["recommendation"]!="no":
						telegram.notify(message)
				except Exception as e:
					logger.error("Telegram is having error and cannot send message(s)",exc_info=True)
				#check configuration and update with new parameters if having
				if "indicators" in symbol_conf[symbol]:
					# stochastic RSI parameters
					if symbol_conf[symbol]["indicators"]["stoch_rsi"]["period"] != frame.iloc[-1]["period"]:
						logger.info("Change stoch_rsi_period from %s to %s", str(symbol_conf[symbol]["indicators"]["stoch_rsi"]["period"]),str(frame.iloc[-1]["period"]))
						symbol_conf[symbol]["indicators"]["stoch_rsi"]["period"] = int(frame.iloc[-1]["period"])

					if symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_k"] != frame.iloc[-1]["fast_k_period"]:
						logger.info("Change stoch_rsi_fast_k from %s to %s", str(symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_k"]),str(frame.iloc[-1]["fast_k_period"]))
						symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_k"] = int(frame.iloc[-1]["fast_k_period"])


					if symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_d"] != frame.iloc[-1]["fast_d_period"]:
						logger.info("Change stoch_rsi_fast_d from %s to %s", str(symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_d"]),str(frame.iloc[-1]["fast_d_period"]))
						symbol_conf[symbol]["indicators"]["stoch_rsi"]["fast_d"] = int(frame.iloc[-1]["fast_d_period"])
					#selling indicators
					if symbol_conf[symbol]["indicators"]["selling"]["rsi"] != frame.iloc[-1]["selling_rsi"]:
						logger.info("Change selling_rsi from %s to %s", str(symbol_conf[symbol]["indicators"]["selling"]["rsi"]),str(frame.iloc[-1]["selling_rsi"]))
						symbol_conf[symbol]["indicators"]["selling"]["rsi"] = int(frame.iloc[-1]["selling_rsi"])

					if symbol_conf[symbol]["indicators"]["selling"]["fast_k"] != frame.iloc[-1]["selling_stoch_rsi"]:
						logger.info("Change selling_stoch_rsi from %s to %s", str(symbol_conf[symbol]["indicators"]["selling"]["fast_k"]),str(frame.iloc[-1]["selling_stoch_rsi"]))
						symbol_conf[symbol]["indicators"]["selling"]["rsi"] = int(frame.iloc[-1]["selling_rsi"])
					
					#buying indicators
					if symbol_conf[symbol]["indicators"]["buying"]["rsi"] != frame.iloc[-1]["buying_rsi"]:
						logger.info("Change buying_rsi from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["rsi"]),str(frame.iloc[-1]["buying_rsi"]))
						symbol_conf[symbol]["indicators"]["buying"]["rsi"] = int(frame.iloc[-1]["buying_rsi"])

					if symbol_conf[symbol]["indicators"]["buying"]["fast_k"] != frame.iloc[-1]["buying_stoch_rsi"]:
						logger.info("Change buying_stoch_rsi from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["fast_k"]),str(frame.iloc[-1]["buying_stoch_rsi"]))
						symbol_conf[symbol]["indicators"]["buying"]["fast_k"] = int(frame.iloc[-1]["buying_stoch_rsi"])


					if symbol_conf[symbol]["indicators"]["buying"]["confirmed_bullish"] != frame.iloc[-1]["buying_confirmed_pullish"]:
						logger.info("Change buying_confirmed_pullish from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["confirmed_bullish"]),str(frame.iloc[-1]["buying_confirmed_pullish"]))
						symbol_conf[symbol]["indicators"]["buying"]["confirmed_bullish"] = int(frame.iloc[-1]["buying_confirmed_pullish"])

					if symbol_conf[symbol]["indicators"]["buying"]["rsi_bullish"] != frame.iloc[-1]["buying_rsi_pullish"]:
						logger.info("Change buying_rsi_pullish from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["rsi_bullish"]),str(frame.iloc[-1]["buying_rsi_pullish"]))
						symbol_conf[symbol]["indicators"]["buying"]["rsi_bullish"] = int(frame.iloc[-1]["buying_rsi_pullish"])


					if symbol_conf[symbol]["indicators"]["buying"]["macdhist"] != frame.iloc[-1]["buying_macdhist"]:
						logger.info("Change buying_macdhist from %s to %s", str(symbol_conf[symbol]["indicators"]["buying"]["macdhist"]),str(frame.iloc[-1]["buying_macdhist"]))
						symbol_conf[symbol]["indicators"]["buying"]["macdhist"] = int(frame.iloc[-1]["buying_macdhist"])
				else:
					indicators={"selling":{"rsi":int(frame.iloc[-1]["selling_rsi"]), "fast_k":int(frame.iloc[-1]["selling_stoch_rsi"])},\
								"buying":{"rsi":int(frame.iloc[-1]["buying_rsi"]), "fast_k":int(frame.iloc[-1]["buying_stoch_rsi"]),\
								"confirmed_bullish":int(frame.iloc[-1]["buying_confirmed_pullish"]),"rsi_bullish":int(frame.iloc[-1]["buying_rsi_pullish"]),\
								"macdhist":int(frame.iloc[-1]["buying_macdhist"])},\
								"stoch_rsi":{"period":int(frame.iloc[-1]["period"]),"fast_k":int(frame.iloc[-1]["fast_k_period"]),"fast_d":int(frame.iloc[-1]["fast_d_period"])}}
					symbol_conf[symbol]["indicators"]=indicators
			else:
				logger.info("There is no profitable strategy found for this symbol")
		#Automatically update configuration file
		conf["symbol"]=symbol_conf
		with open('conf.yml', 'w') as outfile:
			yaml.dump(conf, outfile, default_flow_style=False)


					
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
		logger.info("Terminating process...")
		sys.exit(0)