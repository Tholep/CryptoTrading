import pandas
from pandas import DataFrame as df
from datetime import datetime
import sqlite3
import logging
logger = logging.getLogger(__name__)
import mysql.connector
import yaml
def to_dataframe(data_array):
	dataframe = df(data_array)
	dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
	dataframe['datetime'] = dataframe.timestamp.apply(
		lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c')))
        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)
        return dataframe

def connect():
	#connect to the server
	try:
		conn = mysql.connector.connect(host="localhost",user="crypto",passwd="Crypto@Trading@Algorithm@3009")
		return conn
	except Exception as e:
		logger.error("Error: Can't connect to DB",exc_info=True)
		exit(1)
def connect_db():
	#connect to the server
	try:
		conn = mysql.connector.connect(host="localhost",user="crypto",passwd="Crypto@Trading@Algorithm@3009",database="crypto")
		return conn
	except Exception as e:
		logger.error("Error: Can't connect to DB",exc_info=True)
		exit(1)

def create_db(conn):
	#conn to the mysql server
	# Create database
	#CREATE USER 'crypto'@'localhost' IDENTIFIED BY 'Crypto@Trading@Algorithm@3009';
	#GRANT ALL PRIVILEGES ON crypto.* TO 'crypto'@'localhost';
	#check if db is existed
	try:
		mycursor = conn.cursor()
		#create a new database if not exist
		mycursor.execute("CREATE DATABASE IF NOT EXISTS crypto;")
		mycursor.close()
	except Exception as e:
		logger.error("Error inserting",exc_info=True)
		exit(1)

def create_tables(conn):
	#conn to database crypto
	try:
		mycursor = conn.cursor()
		#create table backtest_wallet - record result of backtest running daily
		#columns: symbol,date, return_budget,profit
		mycursor.execute("create table backtest_wallet(symbol VARCHAR(20),date DATETIME, return_budget FLOAT, profit FLOAT,PRIMARY KEY(symbol,date))")

		# backtest wallet transaction
		#columns: symbol,date,date_of_action,action,price,description
		mycursor.execute("create table backtest_wallet_transaction (id INT NOT NULL AUTO_INCREMENT,symbol VARCHAR(20),date DATETIME,date_of_action DATETIME,action VARCHAR(20), price FLOAT, description TEXT,PRIMARY KEY (id))")

		#Recommendation
		#columns: symbol, date , action, price, description
		mycursor.execute("create table recommendation(id INT NOT NULL AUTO_INCREMENT,symbol VARCHAR(20),date DATETIME,action VARCHAR(20), price FLOAT, description TEXT,PRIMARY KEY(id))")

		#Virtual_wallet
		#columns: symbol,return_budget,number_of_coins
		mycursor.execute("create table virtual_wallet(symbol VARCHAR(20),return_budget FLOAT, nr_of_coins FLOAT, PRIMARY KEY(symbol))")

		# virtual wallet transaction
		#columns: symbol,date,action,price,description
		mycursor.execute("create table virtual_wallet_transaction (symbol VARCHAR(20),date DATETIME,action VARCHAR(20),\
						 price FLOAT, description TEXT,PRIMARY KEY (symbol,date))")

		mycursor.close()
		conn.commit()
	except Exception as e:
		logger.error("Error creating tables",exc_info=True)
		exit(1)
	
def insert_backtest_wallet(conn,data):
	"""This function to insert data to backtest_wallet table
		Args: 
			- conn: connection to db
			- Data: a listof all values to insert - [value1, value2, value3 etc.]
		Return: None - A record is inserted into databse
	"""
	try:
		mycursor=conn.cursor()
		query="INSERT INTO backtest_wallet (symbol,date,return_budget,profit) VALUES (%s,%s,%s,%s)"
		mycursor.execute(query,data)
		mycursor.close()
		
		#commit changes
		conn.commit()
		return 1
	except Exception as e:
		logger.error("Error inserting to backtest_wallet",exc_info=True)
		return 0
def insert_backtest_wallet_transaction(conn,data):
	"""This function to insert data to backtest_wallet table
		Args: 
			- conn: connection to db
			- Data: a listof all values to insert - [value1, value2, value3 etc.]
		Return: None - A record is inserted into databse
	"""
	try:
		mycursor=conn.cursor()
		query="INSERT INTO backtest_wallet_transaction (symbol,date,date_of_action,action,price,description) VALUES (%s,%s,%s,%s,%s,%s)"
		mycursor.execute(query,data)
		mycursor.close()
		
		#commit changes
		conn.commit()
		return 1
	except Exception as e:
		logger.error("Error inserting to backtest_wallet_transaction",exc_info=True)
		return 0

def insert_recommendation(conn,data):
	"""This function to insert data to backtest_wallet table
	Args: 
		- conn: connection to db
		- Data: a listof all values to insert - [value1, value2, value3 etc.]
	Return: None - A record is inserted into databse
	"""
	try:
		mycursor=conn.cursor()
		query="INSERT INTO recommendation (symbol,date,action,price,description) VALUES (%s,%s,%s,%s,%s)"
		mycursor.execute(query,data)
		mycursor.close()
		#commit changes
		conn.commit()
		return 1
	except Exception as e:
		logger.error("Error inserting to recommendation",exc_info=True)
		return 0

def insert_virtual_wallet(conn,data):
	"""This function to insert data to virtual_wallet table
		Args: 
			- conn: connection to db
			- Data: a listof all values to insert - [value1, value2, value3 etc.]
		Return: 1 - A record is inserted into databse
	"""
	try:
		mycursor=conn.cursor()
		query="INSERT INTO virtual_wallet (symbol,return_budget,nr_of_coins) VALUES (%s,%s,%s)"
		mycursor.execute(query,data)
		mycursor.close()
		
		#commit changes
		conn.commit()
		return 1
	except Exception as e:
		logger.error("Error inserting to virtual_wallet",exc_info=True)
		return 0
def initial_virtual_wallet(conn,symbol,initial_budget):
	try:
		mycursor=conn.cursor()
		query="INSERT INTO virtual_wallet (symbol,return_budget,nr_of_coins) VALUES (%s,%s,%s)"
		data=[symbol,initial_budget,0]
		mycursor.execute(query,data)
		mycursor.close()
		
		#commit changes
		conn.commit()
		return 1
	except Exception as e:
		logger.error("Error initializing virtual_wallet: %s" % symbol,exc_info=True)
		return 0
def update_virtual_wallet(conn,data):
	"""This function to update data to virtual_wallet table
		Args: 
			- conn: connection to db
			- Data: a listof all values to insert - [value1, value2, value3 etc.]
		Return: 1 - A record is inserted into databse
	"""
	try:
		mycursor=conn.cursor()
		query="UPDATE virtual_wallet SET return_budget=%s, nr_of_coins=%s where symbol=%s"
		mycursor.execute(query,data)
		mycursor.close()
		
		#commit changes
		conn.commit()
		return 1
	except Exception as e:
		logger.error("Error updating to virtual_wallet",exc_info=True)
		return 0
def get_virtual_wallet(conn,symbol):
	"""This function to get data from virtual_wallet table
		Args: 
			- conn: connection to db
			- Data: a listof all values to insert - [value1, value2, value3 etc.]
		Return: coin,return_budget,nr_of_coins
	"""
	try:
		mycursor=conn.cursor()
		qry_check="""select * from virtual_wallet where symbol=%s"""
		mycursor.execute(qry_check,(symbol,))
		v_wallet=mycursor.fetchall()
		print v_wallet[0], type(v_wallet[0])
		mycursor.close()
		return v_wallet[0]
	except Exception as e:
		logger.error("Error get info from virtual_wallet",exc_info=True)
		return 0
def insert_virtual_wallet_transaction(conn,data):
	"""This function to insert data to backtest_wallet table
		Args: 
			- conn: connection to db
			- Data: a listof all values to insert - [value1, value2, value3 etc.]
		Return: None - A record is inserted into databse
	"""
	try:
		mycursor=conn.cursor()
		query="INSERT INTO virtual_wallet_transaction (symbol,date,action,price,description) VALUES (%s,%s,%s,%s,%s)"
		mycursor.execute(query,data)
		mycursor.close()
		
		#commit changes
		conn.commit()
		return 1
	except Exception as e:
		logger.error("Error inserting to virtual_wallet_transaction",exc_info=True)
		return 0
def initialized_db():
	#setup database
	try:
		initial_conn=connect()
		#create db
		create_db(initial_conn)
		logger.info("Created crypto database successfully")
	except Exception as e:
		logger.error("Failed to create DB")
		exit(1)
	try:
		conn=connect_db()
		#create table
		create_tables(conn)
		logger.info("Created tables successfully")
	except Exception as e:
		logger.error("Failed to create tables")
		exit(1)
	#initialized virtual_wallet
	try:
		conf=yaml.load(open("conf/conf_recommender.yml"))
		for symbol in conf["symbol"].keys():
			initial_virtual_wallet(conn,symbol,conf["symbol"][symbol]["wallet"])
	except Exception as e:
		logger.error("Failed to initialized virtual wallet")
		exit(1)
def check_db():
	try:
		#connect to db
		initial_conn=connect()
	except:
		logger.error("Connection to DB",exc_info=True)
	#create db
	create_db(initial_conn)

	#connect to dabase crypto
	conn=connect_db()

	#create tables
	create_tables(conn)

	conn.commit()
	conn.close()

def test_create_db_table():
	#connect to db
	initial_conn=connect()
	#create db
	create_db(initial_conn)

	#connect to dabase crypto
	conn=connect_db()

	#create tables
	create_tables(conn)

	conn.commit()
	conn.close()

def test_insert():
	from datetime import datetime

	conn=connect_db()
	# insert_backtest_wallet(conn,["ETH/EUR",datetime.now(),10,100,0.39])
	# insert_backtest_wallet_transaction(conn,["ETH/EUR",datetime.now(),datetime.now()-10,"Buy",0.39,"Buy Bearish"])
	#insert_recommendation(conn,["ETH/EUR",datetime.now(),"Sell",0.39,"Sell Bullish"])
	# insert_virtual_wallet(conn,["ETH/EUR",100,1000])
	# insert_virtual_wallet_transaction(conn,["ETH/EUR",datetime.now(),"Sell",0.39,"Sell Bullish"])

	print get_virtual_wallet(conn,"ETH/EUR")