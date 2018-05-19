import pandas
import logging
import time
from analyzer import indicators
logger = logging.getLogger(__name__)
class strategy(object):
	"""docstring for strategy"""
	def __init__(self, data, symbol_conf,indicators_conf):
		
		"""
		Initialize strategy class
		Args:
			data: is the Pandas dataframe containging historical data
			symbol_conf: is configuration detaisl of a specific symbol
		"""
		self.data_standard=data
		self.technical_data=indicators()
		self.symbol_conf=symbol_conf
		self.indicators_conf=indicators_conf
		self.fast_k=self.indicators_conf["stoch_rsi"]["fast_k"]
		self.fast_d=self.indicators_conf["stoch_rsi"]["fast_d"]
		self.rsi_period_range=self.indicators_conf["stoch_rsi"]["period_range"]
		self.rsi_period=self.indicators_conf["stoch_rsi"]["period"]
		self.selling_rsi=self.indicators_conf["selling"]["rsi"]
		self.selling_stoch_rsi=self.indicators_conf["selling"]["fast_k"]
		self.buying_rsi=self.indicators_conf["buying"]["rsi"]
		self.buying_stoch_rsi=self.indicators_conf["buying"]["fast_k"]
		self.buying_confirmed_bullish=self.indicators_conf["buying"]["confirmed_bullish"]
		self.buying_rsi_bullish=self.indicators_conf["buying"]["rsi_bullish"]
		self.buying_macdhist=self.indicators_conf["buying"]["macdhist"]

		#calculate estimated running time for this search. Each round takes roughly about 0.4s
		if self.rsi_period_range:
			time_period_range=(self.rsi_period_range[1]-self.rsi_period_range[0]) if (self.rsi_period_range[1]-self.rsi_period_range[0])>0  else 1
		else:
			time_period_range=1
		time_selling_rsi=(self.selling_rsi[1]-self.selling_rsi[0])/self.selling_rsi[2] +1 if (self.selling_rsi[1]-self.selling_rsi[0])>0 else 1

		time_selling_stoch_rsi=(self.selling_stoch_rsi[1]-self.selling_stoch_rsi[0])/self.selling_stoch_rsi[2] +1 if (self.selling_stoch_rsi[1]-self.selling_stoch_rsi[0])>0 else 1

		time_buying_rsi=(self.buying_rsi[1]-self.buying_rsi[0])/self.buying_rsi[2] +1 if (self.buying_rsi[1]-self.buying_rsi[0])>0 else 1

		time_buying_stoch_rsi=(self.buying_stoch_rsi[1]-self.buying_stoch_rsi[0])/self.buying_stoch_rsi[2] +1 if  (self.buying_stoch_rsi[1]-self.buying_stoch_rsi[0])>0 else 1

		time_buying_confirmed_bullish=(self.buying_confirmed_bullish[1]-self.buying_confirmed_bullish[0])/self.buying_confirmed_bullish[2] +1 if (self.buying_confirmed_bullish[1]-self.buying_confirmed_bullish[0])>0 else 1

		time_buying_rsi_bullish=(self.buying_rsi_bullish[1]-self.buying_rsi_bullish[0])/self.buying_rsi_bullish[2] +1 if (self.buying_rsi_bullish[1]-self.buying_rsi_bullish[0])>0 else 1

		time_buying_macdhist=(self.buying_macdhist[1]-self.buying_macdhist[0])/self.buying_macdhist[2] +1 if (self.buying_macdhist[1]-self.buying_macdhist[0])>0 else 1

		#estimate running time in seconds
		self.estimated_run= time_period_range*time_selling_rsi*time_selling_stoch_rsi*time_buying_rsi*time_buying_stoch_rsi*time_buying_confirmed_bullish*time_buying_rsi_bullish*time_buying_macdhist
		logger.info("Estimated number of brute forces are %s, in about %s minutes",str(self.estimated_run),str(self.estimated_run*0.4/60))

	def strategy_launcher(self):
		results={}
		for st in self.symbol_conf["strategies"]:
			logger.info("Start strategy %s",st)
			results[st]=getattr(self,st)()
			# try:
			# 	results[st]=getattr(self,st)()
			# except:
			# 	logger.error("Strategy: %s does not exist",st)
		return results
	def macd_rsi_stochrsi_strategy(self):
		"""Using rsi and stochrsi for selling and buying decision
		Results: return a tuple of (balance (number), buying (list),selling (list))
		"""
		results=[]

		if self.rsi_period_range:
			for period in range (self.rsi_period_range[0],self.rsi_period_range[1]+1):
				rsi_stoch_rsi=self.technical_data.stochastic_rsi_cal(self.data_standard,period,self.fast_k,self.fast_d)
				macd=self.technical_data.macd_cal(self.data_standard)
				analytical_data=pandas.concat([self.data_standard,rsi_stoch_rsi,macd],axis=1)
				analytical_data.dropna(how='all', inplace=True)
				results.append(self.rsi_stochrsi_strategy_bruteforce(period,self.fast_k,self.fast_d,analytical_data))
		else:
			rsi_stoch_rsi=self.technical_data.stochastic_rsi_cal(self.data_standard,self.rsi_period,self.fast_k,self.fast_d)
			macd=self.technical_data.macd_cal(self.data_standard)
			analytical_data=pandas.concat([self.data_standard,rsi_stoch_rsi,macd],axis=1)
			analytical_data.dropna(how='all', inplace=True)
			results.append(self.rsi_stochrsi_strategy_bruteforce(self.rsi_period,self.fast_k,self.fast_d,analytical_data))
		return results

	def rsi_stochrsi_strategy_bruteforce(self,period,fast_k_period,fast_d_period,data):
	
		results=[]
		
		#starting the bruteforce to find best combination
		for i_selling_rsi in range(self.selling_rsi[0],self.selling_rsi[1]+1,self.selling_rsi[2]):
			for i_selling_stoch_rsi in range(self.selling_stoch_rsi[0],self.selling_stoch_rsi[1]+1,self.selling_stoch_rsi[2]):
				for i_buying_rsi in range(self.buying_rsi[0],self.buying_rsi[1]+1,self.buying_rsi[2]):
					for i_buying_stoch_rsi in range(self.buying_stoch_rsi[0],self.buying_stoch_rsi[1]+1,self.buying_stoch_rsi[2]):
						for i_buying_confirmed_bullish in range(self.buying_confirmed_bullish[0],self.buying_confirmed_bullish[1]+1,self.buying_confirmed_bullish[2]):
							for i_buying_rsi_bullish in range(self.buying_rsi_bullish[0],self.buying_rsi_bullish[1]+1,self.buying_rsi_bullish[2]):
								for i_buying_macdhist in range(self.buying_macdhist[0],self.buying_macdhist[1]+1,self.buying_macdhist[2]):
									result=self.rsi_stochrsi_strategy_trading(period,fast_k_period,fast_d_period,data,i_selling_rsi,i_selling_stoch_rsi,i_buying_rsi,i_buying_stoch_rsi,i_buying_confirmed_bullish,i_buying_rsi_bullish,i_buying_macdhist)
									if result:
										results.append(result)
		return results

	def rsi_stochrsi_strategy_trading(self,period,fast_k_period,fast_d_period,data,selling_rsi,selling_stoch_rsi,buying_rsi,busying_stoch_rsi,buying_confirmed_bullish,buying_rsi_bullish,buying_macdhist):
		start_time=time.time()
		balance=self.symbol_conf["wallet"]
		crypto=0
		data_length=len(data)
		#Record sell and buy transactions
		recorded_transaction=[]
		data=self.is_bullish(buying_confirmed_bullish,buying_rsi_bullish,data)
		#provide recommendation according to the defined strategy
		recommendation=""
		
		for row in range(data_length):		
			"""Buy decision
			(1) in bullish market, try to join at the bottom based on RSI and stochatic RSI
			(2) in bullish market (defined by the last 15 days, RSI above 50)
			"""
			rsi=data.iloc[row]["rsi"]
			fast_k=data.iloc[row]["fast_k"]
			fast_d=data.iloc[row]["fast_d"]
			close_price=data.iloc[row]["close"]
			date=data.index[row]
			is_bullish=data.iloc[row]["is_bullish"]
			macdhist=data.iloc[row]["macdhist"]
			#macd_up= (data.iloc[row]["macdhist"] >=data.iloc[row-1]["macdhist"]) and (data.iloc[row]["macdhist"] >=data.iloc[row-2]["macdhist"]) and (data.iloc[row]["macdhist"] >=data.iloc[row-3]["macdhist"])
			
<<<<<<< HEAD
			if (((rsi<30 or (rsi<70 and is_bearish_short and macdhist>=-10 )) and rsi>0) and (fast_k<20 and fast_k>0 and fast_k>fast_d) and balance>0):
				crypto+=(balance/close_price)*0.999 #close price, excluding 0.1% fee
				balance=0 # after buying crypto
				buying.append((date,close_price,crypto,balance)) #time,price, crypto, blance
				logging.info("Purchase at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
		
=======
			#buying decision
			#
			if (((rsi<buying_rsi or (rsi<70 and is_bullish  and macdhist>=float(buying_macdhist)/100*close_price*-1)) and rsi>0) and (fast_k<busying_stoch_rsi and fast_k>0 and fast_k>fast_d)):
				if balance>0:
					crypto+=(balance/close_price)*0.99 #close price, excluding 0.1% fee
					balance=0 # after buying crypto
					#time,price, crypto, balance
					recorded_transaction.append(("buying",date,close_price,crypto,balance)) 
					logger.debug("Purchase at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
				if row==data_length-1:
					recommendation="buy"
>>>>>>> chart
			#Sell decision
			if ((rsi>selling_rsi and fast_k>=selling_stoch_rsi)):
				if crypto>0:
					balance+=(crypto*close_price)*0.99 #close price, excluding 0.1% fee
					logger.debug("Sell at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
					crypto=0
					#time,price, crypto, balance
					recorded_transaction.append(("selling",date,close_price,crypto,balance)) 
				if row==data_length-1:
					recommendation="sell"
				
		#end of for loop

		#end of data and does not meet conditions to sell
		#convert the amount of crypto holding to a tempory value by the close price of the last day
		balance=balance+crypto*data.iloc[-1]["close"]
		profit=float((balance-self.symbol_conf["wallet"])/self.symbol_conf["wallet"])*100
		logger.debug("Finish around in %s seconds",str(time.time()-start_time))
		if profit>0:
			return (period,fast_k_period,fast_d_period,selling_rsi,selling_stoch_rsi,buying_rsi,busying_stoch_rsi,buying_confirmed_bullish,buying_rsi_bullish,buying_macdhist,balance,profit,recorded_transaction,recommendation)
		else:
			return None

	def is_bullish(self,confirmed_bullish,defined_bullish,data):
		"""in bullish market (defined by the last 15 days, RSI above 50)
		Args:
			confirmed_bullsih: is a period that RSI values over a defined_bullish thresdhold for the considered time.
			defined_bullish: RSI level that bullish market will maintain in
		Result:
			True if bullish, False if not
		"""
		data["rsi_bullish"]=data["rsi"]>defined_bullish
		data["is_bullish"]=data["rsi_bullish"].rolling(confirmed_bullish).sum()==confirmed_bullish
		#data["is_bullish_long"]=data["rsi_bullish"].rolling(candles_long).sum()==candles_long
		return data




