import pandas
import logging
import time

from analyzer import indicators
class strategy(object):
	"""docstring for strategy"""
	def __init__(self, data, exchange_conf,indicators_conf):
		
		"""
		Initialize strategy class
		Args:
			data: is the Pandas dataframe containging rsi and stochrsi
			exchange_conf: is configuration detaisl of a specific exchange
		"""
		
		self.data_standard=data
		self.technical_data=indicators()
		self.exchange_conf=exchange_conf
		self.indicators_conf=indicators_conf
	def strategy_launcher(self):
		results={}
		for st in self.exchange_conf["strategies"]:
			results[st]=getattr(self,st)()
			# try:
			# 	results[st]=getattr(self,st)()
			# except:
			# 	logging.error("Strategy: %s does not exist",st)
		return results
	def rsi_stochrsi_strategy(self):
		"""Using rsi and stochrsi for selling and buying decision
		Results: return a tuple of (balance (number), buying (list),selling (list))
		"""
		results=[]
		fastk=self.indicators_conf["stoch_rsi"]["fastk"]
		fastd=self.indicators_conf["stoch_rsi"]["fastd"]
		if self.indicators_conf["stoch_rsi"]["period_range"]:
			for period in range (3,self.indicators_conf["stoch_rsi"]["period_range"]):
				rsi_stoch_rsi=self.technical_data.stochastic_rsi_cal(self.data_standard,period,fastk,fastd)
				analytical_data=pandas.concat([self.data_standard,rsi_stoch_rsi],axis=1)
				analytical_data.dropna(how='all', inplace=True)
				results.append(self.rsi_stochrsi_strategy_procedure(period,fastk,fastd,analytical_data))
		else:
			rsi_stoch_rsi=self.technical_data.stochastic_rsi_cal(self.data_standard,self.indicators_conf["stoch_rsi"]["period"],fastk,fastd)
			macd=self.technical_data.macd_cal(self.data_standard)
			analytical_data=pandas.concat([self.data_standard,rsi_stoch_rsi,macd],axis=1)
			analytical_data.dropna(how='all', inplace=True)
			results.append(self.rsi_stochrsi_strategy_procedure(self.indicators_conf["stoch_rsi"]["period"],fastk,fastd,analytical_data))
		return results

	def rsi_stochrsi_strategy_procedure(self,period,fast_k_period,fast_d_period,data):
		balance=self.exchange_conf["wallet"]
		crypto=0
		data_length=len(data)
		buying=[]
		selling=[]
		for row in range(data_length):
		#for row in data[["close","rsi","fast_k","fast_d"]].itertuples():
			data=self.is_bearish(15,30,data)
			"""Buy decision
			(1) in pullish market, try to join at the bottom based on RSI and stochatic RSI
			(2) in bearish market (defined by the last 15 days, RSI above 50)
			"""
			rsi=data.iloc[row]["rsi"]
			fast_k=data.iloc[row]["fast_k"]
			fast_d=data.iloc[row]["fast_d"]
			close_price=data.iloc[row]["close"]
			date=data.index[row]
			is_bearish_short=data.iloc[row]["is_bearish_short"]
			is_bearish_long=data.iloc[row]["is_bearish_long"]
			macdhist=data.iloc[row]["macdhist"]
			macd_up= (data.iloc[row]["macdhist"] >=data.iloc[row-1]["macdhist"]) and (data.iloc[row]["macdhist"] >=data.iloc[row-2]["macdhist"]) and (data.iloc[row]["macdhist"] >=data.iloc[row-3]["macdhist"])
			
			if (((rsi<30 or (rsi<70 and is_bearish_short and macdhist>=-10 )) and rsi>0) and (fast_k<20 and fast_k>0 and fast_k>fast_d) and balance>0):
				crypto+=(balance/close_price)*0.999 #close price, excluding 0.1% fee
				balance=0 # after buying crypto
				buying.append((date,close_price,crypto,balance)) #time,price, crypto, blance
				logging.info("Purchase at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
		
			#Sell decision
			if ((rsi>80 and fast_k>=90 and crypto>0)):
				balance+=(crypto*close_price)*0.999 #close price, excluding 0.1% fee
				logging.info("Sell at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
				crypto=0
				selling.append((date,close_price,crypto,balance)) #time,price, crypto, blance
				
		#end of for loop

		#end of data and does not meet conditions to sell
		#convert the amount of crypto holding to a tempory value by the close price of the last day
		if balance==0:
			balance=crypto*data.iloc[-1]["close"]

		return (period,fast_k_period,fast_d_period,balance,float(balance/self.exchange_conf["wallet"])*100,buying,selling)

	def is_bearish(self,candles_short,candles_long,data):
		"""in bearish market (defined by the last 15 days, RSI above 50)
		Args:
			data: data with RSI values over the considered time, past 15 days from the date of considering
		Result:
			True if Bearish, False if not
		"""
		data["rsi_bearish"]=data["rsi"]>50
		data["is_bearish_short"]=data["rsi_bearish"].rolling(candles_short).sum()==candles_short
		data["is_bearish_long"]=data["rsi_bearish"].rolling(candles_long).sum()==candles_long
		return data
		# data_length=len(data)
		# data["is_bearish_short"]=False
		# data["is_bearish_long"]=False
		# data["rsi_bearish"]=data["rsi"]>50
		# for row in range(candles_short,data_length):
		# 	data.iloc[row]["is_bearish_short"]=(data.iloc[row-candles_short:row][data["rsi_bearish"]==True]["rsi_bearish"].count()==candles_short)
		# for row in range(candles_long,data_length):
		# 	data.iloc[row]["is_bearish_long"]=(data.iloc[row-candles_long:row][data["rsi_bearish"]==True]["rsi_bearish"].count()==candles_long)

		# return data



		# check_bearish=data[data["is_bearish"]==True]["is_bearish"].count()
		# if check_bearish==16:
		# 	return True
		# else:
		# 	return False



