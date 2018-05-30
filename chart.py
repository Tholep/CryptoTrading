from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.layouts import layout
from bokeh.models import Span, CrosshairTool, HoverTool, ResetTool, PanTool, WheelZoomTool, BoxZoomTool, ColumnDataSource, BoxAnnotation, LabelSet
import pandas as pd
from pandas import Timestamp
import time
from datetime import datetime as dt 


def candlestick(df,name):
	df['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in df['datetime']]
	inc = df.close > df.open
	dec = df.open > df.close
	w = 12*60*60*1000 # half day in ms, creates the candle's dimension
	TOOLS = [CrosshairTool(line_alpha = 0.5, line_color="white"), PanTool(), WheelZoomTool(),ResetTool()]
	#Setting up the diagram
	p = figure(width=3000, height=600, x_axis_type="datetime", tools=TOOLS, title = name)
	p.grid.grid_line_alpha=0.1 #adds gridlines(the higher the number the visual the lines) 	
	p.background_fill_color ="black"
	#Adding the candlesticks
	p.segment(df.datetime, df.high, df.datetime, df.low, source=ColumnDataSource(df), color="#EAECEE") #adds the tails of candlesticks
	p.vbar(df.datetime[inc], w, df.open[inc], df.close[inc], source=ColumnDataSource(df), color="green", name="inc")
	p.vbar(df.datetime[dec], w, df.open[dec], df.close[dec], source=ColumnDataSource(df), color="red", name="dec")
	return p
def rsi(period,data, bot, top):
	rsi = figure(width=3000, height=150, x_range= candlestick.x_range, x_axis_type="datetime")
	rsi.grid.grid_line_alpha=0.1
	rsi.background_fill_color ="black"
	rsi_box = BoxAnnotation(bottom=bot, top=top, fill_alpha=0.1, fill_color='green')
	rsi.add_layout(rsi_box)
	
	rsi.line(data["datetime"],data["rsi"],color="green")
	rsi.yaxis.axis_label = "RSI - %d" % (period)
	return rsi
def stoch_rsi(period,fast_k,fast_d,data):
	stoch_rsi = figure(width=3000, height=150, x_range= candlestick.x_range, x_axis_type="datetime")
	stoch_rsi.grid.grid_line_alpha=0.1
	stoch_rsi.background_fill_color ="black"
	
	stoch_rsi.line(data["datetime"],data["fast_k"],color="blue")#fast_k
	stoch_rsi.line(data["datetime"],data["fast_d"],color="red")#fast_d
	stoch_rsi.yaxis.axis_label  = "Stochastic RSI - %d-%d-%d" % (period,fast_k,fast_d)
	return stoch_rsi
def macd(data):
	macd = figure(width=3000, height=150, x_range= candlestick.x_range, x_axis_type="datetime")
	macd.grid.grid_line_alpha=0.1
	macd.background_fill_color ="black"

	macd.line(data["datetime"],data["macd"],color="blue") #Fast_k
	macd.line(data["datetime"],data["macdsignal"],color="red") #Fast_d
	macd.yaxis.axis_label  = "MACD - 26-12-9"
	return macd

def read_data(data):
	df = pd.read_csv(data)
	df["datetime"] = pd.to_datetime(df["datetime"])
	return df
def plotting(result):
	plot = pd.read_csv(result).recorded_transaction
	#Take the content of recorded_transaction and turn it from string list to python list
	for i in plot:
		plot = i
	plot = "f= " + plot
	exec(plot) #execute the function in string "f = [(),(),()]"
	#Convert the matrix to dataframe
	f = pd.DataFrame(f, columns=['action', 'datetime', 'price', 'amount_cryp', 'balance'])
	f["datetime"] = pd.to_datetime(f["datetime"])
	#Separate selling records from buying records
	sell= f.loc[f['action']=='selling']
	buy= f.loc[f['action']=='buying']
	return sell, buy
def plot_results():
	# Adding the buy and sell moments on diagram (only plots triangle figures)
	'''candlestick.triangle(x=sell.datetime, y=sell.price, size=10, color="pink")
	candlestick.triangle(x=buy.datetime, y=buy.price, size=10, color="yellow")
	'''
	for i in sell.datetime:
		time_convert_sell = time.mktime(i.timetuple())*1000
		#add the selling vertical lines (Note: for each diagram, recreate the vertical line to plot)
		sell_line = Span(location=time_convert_sell,dimension='height', line_color='red', line_dash='dashed', line_width=1)
		candlestick.add_layout(sell_line)
		sell_line = Span(location=time_convert_sell,dimension='height', line_color='red', line_dash='dashed', line_width=1)
		rsi.add_layout(sell_line)
		sell_line = Span(location=time_convert_sell,dimension='height', line_color='red', line_dash='dashed', line_width=1)
		stoch_rsi.add_layout(sell_line)
		sell_line = Span(location=time_convert_sell,dimension='height', line_color='red', line_dash='dashed', line_width=1)
		macd.add_layout(sell_line)
	for j in buy.datetime:
		time_convert_buy = time.mktime(j.timetuple())*1000
		#add the buying vertical lines (Note: for each diagram, recreate the vertical line to plot)
		buy_line = Span(location=time_convert_buy,dimension='height', line_color='green', line_dash='dashed', line_width=1)
		candlestick.add_layout(buy_line)
		buy_line = Span(location=time_convert_buy,dimension='height', line_color='green', line_dash='dashed', line_width=1)
		rsi.add_layout(buy_line)
		buy_line = Span(location=time_convert_buy,dimension='height', line_color='green', line_dash='dashed', line_width=1)
		stoch_rsi.add_layout(buy_line)
		buy_line = Span(location=time_convert_buy,dimension='height', line_color='green', line_dash='dashed', line_width=1)
		macd.add_layout(buy_line)
	# Add labels
	source = ColumnDataSource(data=dict(datetime_s=sell.datetime.tolist(), price_s=sell.price.tolist(),
		datetime_b=buy.datetime.tolist(), price_b=buy.price.tolist()))
	label_s = LabelSet(x='datetime_s', y='price_s', text='price_s', x_offset=5, y_offset=5, source=source, text_color="white")
	label_b = LabelSet(x='datetime_b', y='price_b', text='price_b', x_offset=5, y_offset=5, source=source, text_color="white")
	candlestick.add_layout(label_s)
	candlestick.add_layout(label_b)


#-----------------------------------------------
data=read_data("C:/Users/Ababalic/Documents/GitHub/CryptoTrading/XRP_EUR.csv")
#-----------------------------------------------
candlestick=candlestick(data,"XRP/EUR")
rsi=rsi(17,data,30,70)
stoch_rsi=stoch_rsi(17,3,3,data)
macd=macd(data)
#-----------------------------------------------
sell, buy = plotting("C:/Users/Ababalic/Documents/GitHub/CryptoTrading/XRP_EUR_result.csv")
plot_results() # Plotting the transaction records on diagrams
#-----------------------------------------------
l=layout([[candlestick], [rsi],[stoch_rsi],[macd]], toolbar_location='above')
output_file("candlestick.html", title="Candlestick diagram")
show(l)