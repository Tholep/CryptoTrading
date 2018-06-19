import pandas
import logging
import time
from analyzer import indicators
import datetime
import sys
from chart import chart
import multiprocessing as mp
import logging

logger = logging.getLogger(__name__)
class strategy(object):
	"""docstring for strategy"""
	def __init__(self, data, symbol,symbol_conf,indicators_conf):
		
		"""
		Initialize strategy class
		Args:
			data: is the Pandas dataframe containging historical data
			symbol_conf: is configuration detaisl of a specific symbol
		"""
		self.symbol=symbol
		self.data_standard=data
		self.technical_data=indicators()
		self.symbol_conf=symbol_conf
		self.indicators_conf=indicators_conf
		self.fast_k=self.indicators_conf["stoch_rsi"]["fast_k"]
		self.fast_d=self.indicators_conf["stoch_rsi"]["fast_d"]
		self.rsi_period=self.indicators_conf["stoch_rsi"]["period"]
		self.selling_rsi=self.indicators_conf["selling"]["rsi"]
		self.selling_rsi_bullish=self.indicators_conf["selling"]["rsi_bullish"]
		self.selling_stoch_rsi=self.indicators_conf["selling"]["fast_k"]
		self.buying_rsi=self.indicators_conf["buying"]["rsi"]
		self.buying_rsi_bullish=self.indicators_conf["buying"]["rsi_bullish"]
		self.buying_stoch_rsi=self.indicators_conf["buying"]["fast_k"]
		self.buying_confirmed_bullish=self.indicators_conf["buying"]["confirmed_bullish"]
		self.buying_rsi_midpoint=self.indicators_conf["buying"]["rsi_midpoint"]
		self.buying_macdhist=self.indicators_conf["buying"]["macdhist"]

		#calculate estimated running time for this search. Each round takes roughly about 0.4s
		
		time_period=(self.rsi_period[1]-self.rsi_period[0])/self.rsi_period[2] +1 if (self.rsi_period[1]-self.rsi_period[0])>0  else 1
	
		time_selling_rsi=(self.selling_rsi[1]-self.selling_rsi[0])/self.selling_rsi[2] +1 if (self.selling_rsi[1]-self.selling_rsi[0])>0 else 1

		time_selling_rsi_bulish=(self.selling_rsi_bullish[1]-self.selling_rsi_bullish[0])/self.selling_rsi_bullish[2] +1 if (self.selling_rsi_bullish[1]-self.selling_rsi_bullish[0])>0 else 1

		time_selling_stoch_rsi=(self.selling_stoch_rsi[1]-self.selling_stoch_rsi[0])/self.selling_stoch_rsi[2] +1 if (self.selling_stoch_rsi[1]-self.selling_stoch_rsi[0])>0 else 1

		time_buying_rsi=(self.buying_rsi[1]-self.buying_rsi[0])/self.buying_rsi[2] +1 if (self.buying_rsi[1]-self.buying_rsi[0])>0 else 1

		time_buying_rsi_bullish=(self.buying_rsi_bullish[1]-self.buying_rsi_bullish[0])/self.buying_rsi_bullish[2] +1 if (self.buying_rsi_bullish[1]-self.buying_rsi_bullish[0])>0 else 1

		time_buying_stoch_rsi=(self.buying_stoch_rsi[1]-self.buying_stoch_rsi[0])/self.buying_stoch_rsi[2] +1 if  (self.buying_stoch_rsi[1]-self.buying_stoch_rsi[0])>0 else 1

		time_buying_confirmed_bullish=(self.buying_confirmed_bullish[1]-self.buying_confirmed_bullish[0])/self.buying_confirmed_bullish[2] +1 if (self.buying_confirmed_bullish[1]-self.buying_confirmed_bullish[0])>0 else 1

		time_buying_rsi_midpoint=(self.buying_rsi_midpoint[1]-self.buying_rsi_midpoint[0])/self.buying_rsi_midpoint[2] +1 if (self.buying_rsi_midpoint[1]-self.buying_rsi_midpoint[0])>0 else 1

		time_buying_macdhist=(self.buying_macdhist[1]-self.buying_macdhist[0])/self.buying_macdhist[2] +1 if (self.buying_macdhist[1]-self.buying_macdhist[0])>0 else 1

		#estimate running time in seconds
		self.estimated_run_selling= time_period*time_selling_rsi*time_selling_rsi_bulish*time_selling_stoch_rsi
		self.estimated_run_buying=time_period*time_buying_rsi*time_buying_rsi_bullish*time_buying_stoch_rsi*time_buying_confirmed_bullish*time_buying_rsi_midpoint*time_buying_macdhist
		logger.info("Estimated number of bruteforces for selling are %s, in about %s minutes",str(self.estimated_run_selling),str(self.estimated_run_selling*0.4/60))
		logger.info("Estimated number of bruteforces for buying are %s, in about %s minutes",str(self.estimated_run_buying),str(self.estimated_run_buying*0.4/60))

	def strategy_launcher(self):
		results={}
		for st in self.symbol_conf["strategies"]:
			logger.info("Start strategy %s",st)
			try:
				results[st]=getattr(self,st)()
				
			except:
				logger.error("Strategy: %s does not exist or there are problems while executing this strategy",st,exc_info=True)
		return results
	def macd_rsi_stochrsi_strategy(self):
		"""Using rsi and stochrsi for selling and buying decision
		Results: return a tuple of (balance (number), buying (list),selling (list))
		"""
		results=[]
		#Run bruteforce every Friday or the symbol is not tuned yet
		try:
			#Monday is 0 and Sunday is 6
			if (not "indicators" in self.symbol_conf): # (datetime.datetime.today().weekday()==3) or 
				for period in range (self.rsi_period[0],self.rsi_period[1]+1,self.rsi_period[2]):
					rsi_stoch_rsi=self.technical_data.stochastic_rsi_cal(self.data_standard,period,self.fast_k,self.fast_d)
					macd=self.technical_data.macd_cal(self.data_standard)
					analytical_data=pandas.concat([self.data_standard,rsi_stoch_rsi,macd],axis=1)
					analytical_data.dropna(how='all', inplace=True)
					results=self.macd_rsi_stochrsi_strategy_bruteforce(period,self.fast_k,self.fast_d,analytical_data)
			else:
				#runing the tunned parameters
				rsi_stoch_rsi=self.technical_data.stochastic_rsi_cal(self.data_standard,self.symbol_conf["indicators"]["stoch_rsi"]["period"],\
								self.symbol_conf["indicators"]["stoch_rsi"]["fast_k"],self.symbol_conf["indicators"]["stoch_rsi"]["fast_d"])
				rsi_stoch_rsi.to_csv("stoch_rsi.csv")
				self.data_standard.to_csv("standard.csv")
				macd=self.technical_data.macd_cal(self.data_standard)
				analytical_data=pandas.concat([self.data_standard,rsi_stoch_rsi,macd],axis=1)
				analytical_data.dropna(how='all', inplace=True)
				results=self.macd_rsi_stochrsi_strategy_tuned_parameter(self.symbol_conf["indicators"]["stoch_rsi"]["period"],\
							self.symbol_conf["indicators"]["stoch_rsi"]["fast_k"],self.symbol_conf["indicators"]["stoch_rsi"]["fast_d"],\
							analytical_data)
		except Exception,e:
			logger.error("Error when runing a strategy. Current symbol configuration %s",self.symbol_conf,exc_info=True)
			sys.exit(1)

		#Plot figure and return best profitable trading strategy
		
		#convert to a dataframe: import to a series and 
		# frame=pandas.Series(results)
		# frame=pandas.DataFrame(frame)
		# frame.columns=["period","fast_k_period","fast_d_period","selling_rsi","selling_rsi_bullish","selling_stoch_rsi","buying_rsi","buying_rsi_bullish","buying_stoch_rsi","buying_confirmed_pullish","buying_rsi_pullish","buying_macdhist","balance","profit","recorded_transaction","recommendation"]
		#plot tradig chart
		fig = chart(analytical_data.reset_index(),results)
		fig.output_charts(self.symbol,17,30,70,3,3)
		#return the best strategy
		return results
		# #there is no profitable, return an empty serie
		# return pandas.Series()

	def macd_rsi_stochrsi_strategy_tuned_parameter(self,period,fast_k_period,fast_d_period,data):
		"""Applied tuned parameters for the strategy of the current symbol
		"""
		#return results in an array in order to be consistent with the bruteforce method

		logger.info("Running the strategy with tunned parameters")
		i_selling_rsi=self.symbol_conf["indicators"]["selling"]["rsi"]
		i_selling_rsi_bullish=self.symbol_conf["indicators"]["selling"]["rsi_bullish"]
		i_selling_stoch_rsi=self.symbol_conf["indicators"]["selling"]["fast_k"]
		i_buying_rsi=self.symbol_conf["indicators"]["buying"]["rsi"]
		i_buying_rsi_bullish=self.symbol_conf["indicators"]["buying"]["rsi_bullish"]
		i_buying_stoch_rsi=self.symbol_conf["indicators"]["buying"]["fast_k"]
		i_buying_confirmed_bullish=self.symbol_conf["indicators"]["buying"]["confirmed_bullish"]
		i_buying_rsi_midpoint=self.symbol_conf["indicators"]["buying"]["rsi_midpoint"]
		i_buying_macdhist=self.symbol_conf["indicators"]["buying"]["macdhist"]
		return self.macd_rsi_stochrsi_strategy_backtest(period,fast_k_period,fast_d_period,data,i_selling_rsi,i_selling_rsi_bullish,i_selling_stoch_rsi,i_buying_rsi,i_buying_rsi_bullish,i_buying_stoch_rsi,i_buying_confirmed_bullish,i_buying_rsi_midpoint,i_buying_macdhist)

	
	def macd_rsi_stochrsi_strategy_bruteforce(self,period,fast_k_period,fast_d_period,data):		
		#starting the bruteforce to find best combination for buying
		try:
			logger.info("Starting bruteforce parameters for buying")
			jobs=[]
			#create a pool of workers
			pool = mp.Pool(processes=3)
			start_time=time.time()
			#------------------------------------------------------------------------------------------
			for i_buying_rsi in range(self.buying_rsi[0],self.buying_rsi[1]+1,self.buying_rsi[2]):
				for i_buying_rsi_bullish in range(self.buying_rsi_bullish[0],self.buying_rsi_bullish[1]+1,self.buying_rsi_bullish[2]):
					for i_buying_stoch_rsi in range(self.buying_stoch_rsi[0],self.buying_stoch_rsi[1]+1,self.buying_stoch_rsi[2]):
						for i_buying_confirmed_bullish in range(self.buying_confirmed_bullish[0],self.buying_confirmed_bullish[1]+1,self.buying_confirmed_bullish[2]):
							for i_buying_rsi_midpoint in range(self.buying_rsi_midpoint[0],self.buying_rsi_midpoint[1]+1,self.buying_rsi_midpoint[2]):
								for i_buying_macdhist in range(self.buying_macdhist[0],self.buying_macdhist[1]+1,self.buying_macdhist[2]):
									jobs.append(pool.apply_async(self,args=(True,data,None,None,None,i_buying_rsi,i_buying_rsi_bullish,i_buying_stoch_rsi,i_buying_confirmed_bullish,i_buying_rsi_midpoint,i_buying_macdhist)))
			#-------------------------------------------------------------------------------------------
			pool.close()
			pool.join()
			logger.info("All workers have finished")

			#get returned results for works
			results=[]
			for job in jobs:
				results.append(job.get())
		
			buying_df=pandas.DataFrame(results,columns=["total","buying_average","buying_rsi","buying_rsi_bullish","buying_stoch_rsi","buying_confirmed_bullish","buying_rsi_midpoint","buying_macdhist"])
			buying_df=buying_df.sort_values("total",ascending=False)
			#best buying is the lowest buying average in the top 10 highest total
			best_buying=buying_df.iloc[:9].sort_values("buying_average").iloc[0]
			#store best found parameters
			best_buying_rsi=best_buying["buying_rsi"]
			best_buying_rsi_bullish=best_buying["buying_rsi_bullish"]
			best_buying_stoch_rsi=best_buying["buying_stoch_rsi"]
			best_buying_confirmed_bullish=best_buying["buying_confirmed_bullish"]
			best_buying_rsi_midpoint=best_buying["buying_rsi_midpoint"]
			best_buying_macdhist=best_buying["buying_macdhist"]
			logger.info("Total buying bruteforce time is %s minutes",str((time.time()-start_time)/60))
		except Exception as e:
			logger.error("Error when runing bruteforce for buying",exc_info=True)
			sys.exit(1)
		#starting the bruteforce to find best combination for selling
		
		try:
			logger.info("Starting bruteforce parameters for selling")
			jobs=[]
			#create a pool of workers
			pool = mp.Pool(processes=3)
			start_time=time.time()
			for i_selling_rsi in range(self.selling_rsi[0],self.selling_rsi[1]+1,self.selling_rsi[2]):
				for i_selling_rsi_bullish in range(self.selling_rsi_bullish[0],self.selling_rsi_bullish[1]+1,self.selling_rsi_bullish[2]):
					for i_selling_stoch_rsi in range(self.selling_stoch_rsi[0],self.selling_stoch_rsi[1]+1,self.selling_stoch_rsi[2]):
						# self.macd_rsi_stochrsi_strategy_trading_test(False,data,i_selling_rsi,i_selling_rsi_bullish,i_selling_stoch_rsi,\
						# 								None,None,None,best_buying_confirmed_bullish,best_buying_rsi_midpoint,None)
						jobs.append(pool.apply_async(self,args=(False,data,i_selling_rsi,i_selling_rsi_bullish,i_selling_stoch_rsi,\
														None,None,None,best_buying_confirmed_bullish,best_buying_rsi_midpoint,None)))
			pool.close()
			pool.join()
			logger.info("All workers have finished")
			#get returned results for works
			results=[]
			for job in jobs:
				results.append(job.get())
				# print job.successful()
			
			selling_df=pandas.DataFrame(results,columns=["total","selling_average","selling_rsi","selling_rsi_bullish","selling_stoch_rsi"])
			selling_df=selling_df.sort_values("total",ascending=False)
			#best selling is the highest selling average
			best_selling=selling_df.iloc[:9].sort_values("selling_average",ascending=False).iloc[0]
			#store best found parameters
			best_selling_rsi=best_selling["selling_rsi"]
			best_selling_rsi_bullish=best_selling["selling_rsi_bullish"]
			best_selling_stoch_rsi=best_selling["selling_stoch_rsi"]

			logger.info("Total selling bruteforce time is %s minutes",str((time.time()-start_time)/60))
	
		except Exception as e:
			logger.error("Error when runing bruteforce for selling",exc_info=True)
			sys.exit(1)
		#apply found parameters for backtest
		return self.macd_rsi_stochrsi_strategy_backtest(period,fast_k_period,fast_d_period,data,best_selling_rsi,best_selling_rsi_bullish,best_selling_stoch_rsi,best_buying_rsi,best_buying_rsi_bullish,best_buying_stoch_rsi,best_buying_confirmed_bullish,best_buying_rsi_midpoint,best_buying_macdhist)
	
	#to solve the problem of pickling with multiprocessing library
	def __call__(self,is_buy,data,selling_rsi,selling_rsi_bullish,selling_stoch_rsi,buying_rsi,buying_rsi_bullish,buying_stoch_rsi,buying_confirmed_bullish,buying_rsi_midpoint,buying_macdhist):
		return self.macd_rsi_stochrsi_strategy_trading_test(is_buy,data,selling_rsi,selling_rsi_bullish,selling_stoch_rsi,buying_rsi,buying_rsi_bullish,buying_stoch_rsi,buying_confirmed_bullish,buying_rsi_midpoint,buying_macdhist)
	#Since only one function can be returned from __call__, this function is used for both buying and selling to test bruteforced parameters.
	#It may be  not the most efficient approach, maybe for TODO later on.
	def macd_rsi_stochrsi_strategy_trading_test(self,is_buy,data,selling_rsi,selling_rsi_bullish,selling_stoch_rsi,buying_rsi,buying_rsi_bullish,buying_stoch_rsi,buying_confirmed_bullish,buying_rsi_midpoint,buying_macdhist):
		start_time=time.time()
		#define a default value for evaluation
		amount=100
		balance=0
		crypto=0
		data_length=len(data)
		#Record sell or buy transactions
		recorded_transaction=[]
		#defined up and down trend
		data=self.is_bullish(buying_confirmed_bullish,buying_rsi_midpoint,data)
		#provide recommendation according to the defined strategy
		recommendation= "no"
		bullish_macd_confirmation=False
		#--------------------------------------------------------------------
		#buying decision
		if is_buy:
			for row in range(data_length):		
				rsi=data.iloc[row]["rsi"]
				fast_k=data.iloc[row]["fast_k"]
				fast_d=data.iloc[row]["fast_d"]
				close_price=data.iloc[row]["close"]
				date=data.index[row]
				is_bullish=data.iloc[row]["is_bullish"]
				macdhist=data.iloc[row]["macdhist"]
				if (is_bullish==False and bullish_macd_confirmation):
					bullish_macd_confirmation=False
				#General buying condition, only purchase when an uptrend is observed
				if fast_k>0 and rsi>0 and fast_k<buying_stoch_rsi and fast_k>fast_d:
					
					#for bearish market
					if (rsi<buying_rsi and is_bullish==False):
						#close price, excluding 5% fee
						crypto+=(amount/close_price)*0.95
						balance+=amount

					#For bullish market
					if (rsi<buying_rsi_bullish and is_bullish):
						if macdhist>=0:
							crypto+=(amount/close_price)*0.95
							balance+=amount
						else:
							bullish_macd_confirmation=True
				#For bullish market with macd confirmation
				if bullish_macd_confirmation and macdhist>=0:
					bullish_macd_confirmation=False
					crypto+=(amount/close_price)*0.95
					balance+=amount
			#Calculate average buying per coin
			if crypto>0:
				avg_buy=float(balance)/crypto
			else:
				#no crypto buy, assign an big number for not being chosen as a good strategy
				avg_buy=999999
			#may not be the best approach to return parameters. Each test is run paralellelly with other 2 processes; hence, need to store all parameters
			#may be put in TODO for later improvement
			return (balance,avg_buy,buying_rsi,buying_rsi_bullish,buying_stoch_rsi,buying_confirmed_bullish,buying_rsi_midpoint,buying_macdhist)
		#selling decision
		else:
			#--------------------------------------------------------------------
			#Sell decision
			for row in range(data_length):		
				rsi=data.iloc[row]["rsi"]
				fast_k=data.iloc[row]["fast_k"]
				fast_d=data.iloc[row]["fast_d"]
				close_price=data.iloc[row]["close"]
				date=data.index[row]
				is_bullish=data.iloc[row]["is_bullish"]
				macdhist=data.iloc[row]["macdhist"]
				
				if (is_bullish==False and bullish_macd_confirmation):
					bullish_macd_confirmation=False

				if (fast_k>=selling_stoch_rsi):
					#for bearish market
					if (is_bullish==False and rsi>selling_rsi):
						#close price, excluding 5% fee
						balance+=(amount*close_price)*0.95 
						crypto+=amount

					#for bullish market	
					if (is_bullish and rsi>selling_rsi_bullish):
						#close price, excluding 5% fee
						balance+=(amount*close_price)*0.95 
						crypto+=amount
			
			if balance>0:
				avg_sell=float(balance)/crypto
			else:
				#if no sell, assign a small number so that this strategy is not considered a good selling strategy
				avg_sell=-999999
			#may not be the best approach to return parameters. Each test is run paralellelly with other 2 processes; hence, need to store all parameters
			#may be put in TODO for later improvement
			return (balance,avg_sell,selling_rsi,selling_rsi_bullish,selling_stoch_rsi	)
	
	def is_bullish(self,confirmed_bullish,defined_bullish,data):
		"""in bullish market (defined by the last 15 days, RSI above 50)
		Args:
			confirmed_bullsih: is a period that RSI values over a defined_bullish thresdhold for the considered time.
			defined_bullish: RSI level that bullish market will maintain in
		Result:
			True if bullish, False if not
		"""
		data["rsi_midpoint"]=data["rsi"]>defined_bullish
		data["is_bullish"]=data["rsi_midpoint"].rolling(int(confirmed_bullish)).sum()==confirmed_bullish
		#data["is_bullish_long"]=data["rsi_midpoint"].rolling(candles_long).sum()==candles_long
		return data


	def macd_rsi_stochrsi_strategy_backtest(self,period,fast_k_period,fast_d_period,data,selling_rsi,selling_rsi_bullish,selling_stoch_rsi,buying_rsi,buying_rsi_bullish,buying_stoch_rsi,buying_confirmed_bullish,buying_rsi_midpoint,buying_macdhist):
		start_time=time.time()
		balance=self.symbol_conf["wallet"]
		crypto=0
		data_length=len(data)
		#Record sell and buy transactions
		recorded_transaction=[]
		data=self.is_bullish(buying_confirmed_bullish,buying_rsi_midpoint,data)
		#provide recommendation according to the defined strategy
		recommendation= "no"
		bullish_macd_confirmation=False
		for row in range(data_length):		
			rsi=data.iloc[row]["rsi"]
			fast_k=data.iloc[row]["fast_k"]
			fast_d=data.iloc[row]["fast_d"]
			close_price=data.iloc[row]["close"]
			date=data.index[row]
			is_bullish=data.iloc[row]["is_bullish"]
			macdhist=data.iloc[row]["macdhist"]
			
			if (is_bullish==False and bullish_macd_confirmation):
				bullish_macd_confirmation=False
			#buying decision
			if fast_k>0 and rsi>0 and fast_k<buying_stoch_rsi and fast_k>fast_d:
				#for bearish market
				if (rsi<buying_rsi and is_bullish==False):
					
					if balance>0:
						crypto+=(balance/close_price)*0.99 #close price, excluding 0.1% fee
						balance=0# after buying crypto
						#time,price, crypto, balance
						recorded_transaction.append(("buying_bearish",date,close_price,crypto,balance)) 
						logger.debug("Purchase at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
					if row==data_length-1:
						recommendation="buy bearish"
				#For bullish market
				if (rsi<buying_rsi_bullish and is_bullish):
					if macdhist>=0:
						if balance>0:
							crypto+=(balance/close_price)*0.99 #close price, excluding 0.1% fee
							balance=0# after buying crypto
							#time,price, crypto, balance
							recorded_transaction.append(("buying_bullish",date,close_price,crypto,balance)) 
							logger.debug("Purchase at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
							#provide recommendation via telegram
						if row==data_length-1:
							recommendation="buy bullish"
					else:
						bullish_macd_confirmation=True
						recommendation="buy bullish (without confirmation)"
			if bullish_macd_confirmation and macdhist>=0:
				bullish_macd_confirmation=False
				if balance>0:
					crypto+=(balance/close_price)*0.99 #close price, excluding 0.1% fee
					balance=0# after buying crypto
					#time,price, crypto, balance
					recorded_transaction.append(("buying_bullish_confirmed",date,close_price,crypto,balance)) 
					logger.debug("Purchase at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
					#provide recommendation via telegram
				if row==data_length-1:
					recommendation="buy bullish by macd"


			#Sell decision
			if (fast_k>=selling_stoch_rsi):
				if (is_bullish==False and rsi>selling_rsi):
					if crypto>0:
						balance+=(crypto*close_price)*0.99 #close price, excluding 0.1% fee
						logger.debug("Sell at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
						crypto=0
						#time,price, crypto, balance
						recorded_transaction.append(("selling_bearish",date,close_price,crypto,balance)) 
					if row==data_length-1:
						recommendation="sell bearish"
				if (is_bullish and rsi>selling_rsi_bullish):
					if crypto>0:
						balance+=(crypto*close_price)*0.99 #close price, excluding 0.1% fee
						logger.debug("Sell at %s: %s at price %s - current balance: %s",str(date),str(crypto),str(close_price),str(balance))
						crypto=0
						#time,price, crypto, balance
						recorded_transaction.append(("selling_bullish",date,close_price,crypto,balance)) 
					if row==data_length-1:
						recommendation="sell bullish"
				
		#end of for loop

		#end of data and does not meet conditions to sell
		#convert the amount of crypto holding to a tempory value by the close price of the last day
		balance=balance+crypto*data.iloc[-1]["close"]
		profit=float((balance-self.symbol_conf["wallet"])/self.symbol_conf["wallet"])*100
		logger.debug("Finish around in %s seconds",str(time.time()-start_time))
		return (period,fast_k_period,fast_d_period,selling_rsi,selling_rsi_bullish,selling_stoch_rsi,buying_rsi,buying_rsi_bullish,buying_stoch_rsi,buying_confirmed_bullish,buying_rsi_midpoint,buying_macdhist,balance,profit,recorded_transaction,recommendation)


