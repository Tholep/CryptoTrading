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
from utilities import *
#from utilities import create_db


#check and setup initial environment
try:
	conf=yaml.load(open("conf/conf_recommender.yml"))
except Exception as e:
	raise e
try:
	if not os.path.exists("logs"):
		os.makedirs("logs")

except Exception as e:
		logger.error("Cannot create neccessary directories for operations",exc_info=True)

#set up logger
logging.config.dictConfig(conf["logging"])
logger = logging.getLogger(__name__)

def virtual_trans(conn,symbol,price,recommendation,dt):

	#get info of virtual wallet
	v_wallet=get_virtual_wallet(conn,symbol)
	if isinstance(v_wallet,tuple):
		logger.info("Check to perform trasaction in Virtual wallet for %s",symbol)
		coin,return_budget,nr_of_coins=v_wallet
		# take action from recommendation . e.g. Sell Bullish --> Sell
		action=recommendation.split(" ")[0]
		if action == "buy":
			if return_budget > 0:
				logger.info("Perform purchase action from virtual wallet for %s",symbol)
				nr_of_coins_purchased = return_budget/price
				return_budget=0
				nr_of_coins +=nr_of_coins_purchased

				#update virtual wallet
				update_virtual_wallet(conn,[float(return_budget),float(nr_of_coins),symbol])
				insert_virtual_wallet_transaction(conn,[symbol,dt,action,float(price),recommendation])
	
		else: #sell
			if nr_of_coins > 0:
				logger.info("Perform selling action from virtual wallet for %s",symbol)
				return_budget +=nr_of_coins*price
				nr_of_coins=0
		
				#update virtual wallet
				update_virtual_wallet(conn,[float(return_budget),float(nr_of_coins),symbol])
				insert_virtual_wallet_transaction(conn,[symbol,dt,action,float(price),recommendation])

def main():

	try:
		telegram=TelegramNotifier(conf["notifier"]["telegram"]["api"],conf["notifier"]["telegram"]["chat_id"])
		logger.debug("Loaded telegram")
	except Exception as e:
		logger.error("Cannot load telegram object",exc_info=True)
			
	symbol_conf=conf["symbol"]
	ex=HistorialData(symbol_conf)
	# connect to database
	conn=connect_db()

	for symbol in symbol_conf.keys():
		normalised_symbol=symbol.split("_")[0] # symbol can be ETH/EUR_1D ETH/EUR_1H --> only get ETH/EUR to get historical data from exchange
		exchange=symbol_conf[symbol]["exchange"]
		time_unit=symbol_conf[symbol]["time_unit"]
		candles=symbol_conf[symbol]["candles"]
		#get historical data from symbol and symbol identified
		logger.debug("Get historical data %s:%s",exchange,symbol)
		try:
			data=ex.get_historical_data(normalised_symbol,exchange,time_unit,candles)
		except Exception as e:
			logger.error("Error in retrieving historical data for %s",symbol,exc_info=True)
			continue
		
		data=to_dataframe(data)
		# Aplly strategy(s) to collected data
		for st in symbol_conf[symbol]["strategies"]:
			klass=globals()[st]
			tatics=klass(data,symbol,symbol_conf[symbol],conf["indicators"])
			result=tatics.launch()
			logger.info("Results for symbol: %s",symbol)
			logger.info("\n%s",result)
			
			# if the symbol is profitable
			if isinstance(result,tuple):
				#insert results to backtest_wallet and backtest_wallet_transaction
				dt=str(datetime.now())
				#columns: symbol,date, return_budget,profit
				backtest_data=[symbol,dt,float(result[-4]),float(result[-3])]
				insert_backtest_wallet(conn,backtest_data)
				for tx in result[-2]:
					#columns: symbol,date,date_of_action,action,price,description
					backtest_trans_data=[symbol,dt,str(tx[2]),tx[0],float(tx[3]),tx[1]]
					insert_backtest_wallet_transaction(conn,backtest_trans_data)
				
				recommendation=result[-1]
				if recommendation!="no":
					message=symbol + ":" + st +"\n"
					message+="Date time: %s" % (str(datetime.now())) + "\n"
					profit=result[-3]
					total_budget=result[-4]
					price=data.iloc[-1]["close"]
					initial_budget=symbol_conf[symbol]["wallet"]
					message+="Initial budget: %s" % (str(initial_budget)) + "\n"
					message+="Total budget: %s" % (str(total_budget)) + "\n"
					message+="Profit: %s%%" % (str(profit)) + "\n"
					message+="Recommendation: %s @ price %s" % (str(recommendation),str(price)) + "\n"

					#insert into recommendation table
					#columns: symbol, date , action, price, description
					recommendation_data=[symbol,dt,recommendation.split(" ")[0],float(price),recommendation]
					insert_recommendation(conn,recommendation_data)

					#Perform virtual transactions
					virtual_trans(conn,symbol,price,recommendation,dt)
					try:
						telegram.notify(message)
					except Exception as e:
						logger.error("Telegram is having error and cannot send message(s)")
				break
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
		logger.info("Terminating process...")
		sys.exit(0)
