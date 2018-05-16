from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

def rsi(period,data):

	hover = HoverTool(
		tooltips=[("Date", '$x'),("Value","$y"),],
		formatters={'$x': 'datetime',})
	rsi = figure(width=600, height=200,x_axis_type="datetime",title="RSI - %d" % (period),tools=[hover])
	rsi.line(data["datetime"],data["rsi"],color="navy")
	rsi.xaxis.axis_label = "Date"
	rsi.yaxis.axis_label = "RSI"
	return rsi

def stoch_rsi(period,fast_k,fast_d,data):
	stoch_rsi = figure(width=600, height=200,x_axis_type="datetime",title="Stochastic RSI - %d-%d-%d" % (period,fast_k,fast_d))
	stoch_rsi.line(data["datetime"],data["fast_k"],color="green",legend="Fast_k")
	stoch_rsi.line(data["datetime"],data["fast_d"],color="red",legend="Fast_d")

	return stoch_rsi
def macd(data):
	"""
	"""
	macd = figure(width=600, height=200,x_axis_type="datetime",title="MACD - 26-12-9")
	macd.line(data["datetime"],data["macd"],color="green",legend="MACD")
	macd.line(data["datetime"],data["macdsignal"],color="red",legend="MACD Signal")

#l=layout([rsi,stoch_rsi],sizing_mode="scale_height")

