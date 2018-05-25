from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.layouts import layout
import pandas as pd
from bokeh.models import Span, CrosshairTool, HoverTool, ResetTool, PanTool, WheelZoomTool, BoxZoomTool	

def rsi(period,data):
	rsi = figure(width=1500, height=150,x_axis_type="datetime")
	rsi.grid.grid_line_alpha=0.1
	rsi.background_fill_color ="black"
	
	rsi.line(data["datetime"],data["rsi"],color="green")
	rsi.yaxis.axis_label = "RSI - %d" % (period)
	return rsi

def stoch_rsi(period,fast_k,fast_d,data):
	stoch_rsi = figure(width=1500, height=150, x_axis_type="datetime")
	stoch_rsi.grid.grid_line_alpha=0.1
	stoch_rsi.background_fill_color ="black"
	
	stoch_rsi.line(data["datetime"],data["fast_k"],color="blue")#fast_k
	stoch_rsi.line(data["datetime"],data["fast_d"],color="red")#fast_d
	stoch_rsi.yaxis.axis_label  = "Stochastic RSI - %d-%d-%d" % (period,fast_k,fast_d)
	return stoch_rsi

def macd(data):
	macd = figure(width=1500, height=150,x_axis_type="datetime")
	macd.grid.grid_line_alpha=0.1
	macd.background_fill_color ="black"
	
	macd.line(data["datetime"],data["macd"],color="blue") #Fast_k
	macd.line(data["datetime"],data["macdsignal"],color="red") #Fast_d
	macd.yaxis.axis_label  = "MACD - 26-12-9"
	return macd

def candlestick(df,name):
	df['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in df['datetime']]
	inc = df.close > df.open
	dec = df.open > df.close
	w = 12*60*60*1000 # half day in ms, creates the candle's dimension
	TOOLS = [CrosshairTool(line_alpha = 0.5), BoxZoomTool(), PanTool(), WheelZoomTool(),ResetTool(), 'hover']
	#Setting up the diagram
	p = figure(width=1500, height=600, x_axis_type="datetime", tools=TOOLS, title = name)
	p.grid.grid_line_alpha=0.1 #adds gridlines(the higher the number the visual the lines)
	p.background_fill_color ="black"
	#Edit the hover tool
	hover = p.select(dict(type=HoverTool))
	tips =[("Date","@tooltip"), ("EUR","$y")]
	hover.tooltips=tips
	hover.mode = 'mouse'
	#Adding the candlesticks
	p.segment(df.datetime, df.high, df.datetime, df.low, source=ColumnDataSource(df), color="#EAECEE") #adds the tails of candlesticks
	p.vbar(df.datetime[inc], w, df.open[inc], df.close[inc], source=ColumnDataSource(df), color="green", name="inc")
	p.vbar(df.datetime[dec], w, df.open[dec], df.close[dec], source=ColumnDataSource(df), color="red", name="dec")
	return p


data = pd.read_csv("C:/Users/Ababalic/Dropbox/Python/Crypto/CryptoTrading-chart/data.csv")
data["datetime"] = pd.to_datetime(data["datetime"])

rsi=rsi(17,data)
stoch_rsi=stoch_rsi(17,3,3,data)
macd=macd(data)
candlestick=candlestick(data,"ETH_EUR")

l=layout([[candlestick], [rsi],[stoch_rsi],[macd]])
output_file("candlestick.html", title="Candlestick diagram")
show(l)