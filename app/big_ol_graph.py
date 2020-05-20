#!/usr/bin/env python3
from big_ol_db import BigOlDB
import matplotlib.pyplot as plt, matplotlib.ticker as mticker, matplotlib.dates as mdates, time, datetime, numpy as np, matplotlib, MySQLdb
from mpl_finance import candlestick_ohlc as candlestick

matplotlib.rcParams.update({'font.size': 9})

ticker = 'XPL'
sma_short = 55
sma_long = 200

# Connect to DB
file = open("C://Users/mth47/workspace/CoinIndexCap_Credentials.txt", "r")
username, password, dbname, endpoint = file.read().splitlines()
db = MySQLdb.connect(endpoint, username, password, dbname)
cursor = db.cursor()

def setFrameColors(plot):
	plot.set_facecolor('#070008')
	plot.spines['bottom'].set_color('#5998ff')
	plot.spines['top'].set_color('#5998ff')
	plot.spines['left'].set_color('#5998ff')
	plot.spines['right'].set_color('#5998ff')
	plot.yaxis.label.set_color('w')

def movingAverage(values, window):

	arr = []

	for i in range(window, len(values)):
		arr.append(np.mean(values[i-window:i]))
	# weights = np.repeat(1.0, window)/window
	# smas = np.convolve(values, weights, 'valid')
	return arr

def ExpMovingAverage(values, window):
	weights = np.exp(np.linspace(-1., 0., window))
	weights /= weights.sum()
	a = np.convolve(values, weights, mode='full')[:len(values)]
	a[:window] = a[window]

	return a

def computeMACD(x, slow = 26, fast=12):
	'''
	macd line = 12ema - 26ema
	signal line = 9ema of the macd line
	histogram = macd line - signal line
	'''
	emaslow = ExpMovingAverage(x, slow)
	emafast = ExpMovingAverage(x, fast)

	print(len(emaslow), len(emafast))
	diff = [emafast[i] - emaslow[i] for i in range(len(emafast))]

	return emaslow, emafast, diff

def rsiFunc(prices, n=35):
	deltas = np.diff(prices)
	seed = deltas[:n+1]
	up = seed[seed>=0].sum() / n
	down = -seed[seed < 0].sum() / n
	rs = up / down
	rsi = np.zeros_like(prices)
	rsi[:n] = 100.0 - (100.0 / (1.0 + rs))

	for i in range(n, len(prices)):
		delta = deltas[i-1]
		if delta > 0:
			upval = delta
			downval = 0.0

		else:
			upval = 0.0
			downval = -delta

		up = (up * (n-1) + upval) / n
		down = (down * (n-1) + downval) / n
		rs = up/down
		rsi[i] = 100.0 - 100.0/(1.0 + rs)

	return rsi

def graphData(ticker, MA1, MA2):
	timestamps, prices_usd, prices_btc, mktcap_usd, mktcap_btc = BigOlDB().getMinutelySectorData(ticker)

	f, (ax0, ax1, ax2) = plt.subplots(3, sharex=True, gridspec_kw = {'height_ratios':[1, 6, 1]}, facecolor='#070008')
	
	av1 = movingAverage(prices_usd, MA1)
	av2 = movingAverage(prices_usd, MA2)

	span = len(timestamps[MA2-1:])
	label1, label2 = str(MA1) + ' SMA', str(MA2) + ' SMA'

	# RSi Stuff
	rsiCol = '#00ffe8'
	setFrameColors(ax0)
	rsi = rsiFunc(prices_usd)
	ax0.plot(timestamps[-span:], rsi[-span:], rsiCol, linewidth=1.5)
	ax0.set_ylim(15, 85)
	ax0.axhline(70, color = rsiCol, linewidth=0.75)
	ax0.axhline(30, color = rsiCol, linewidth=0.75)
	ax0.fill_between(timestamps[-span:], rsi[-span:], 70, where=(rsi[-span:] >= 70), facecolor=rsiCol, edgecolor=rsiCol)
	ax0.fill_between(timestamps[-span:], rsi[-span:], 30, where=(rsi[-span:] <= 30), facecolor=rsiCol, edgecolor=rsiCol)
	ax0.tick_params(axis='x', colors='w')
	ax0.tick_params(axis='y', colors='w')
	ax0.set_yticks([30, 70])
	plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='lower'))

	# ax1.plot(timestamps, prices_usd)
	ax1.plot(timestamps, prices_usd, linewidth=1.5)
	# ax1.set(ylabel = 'Coin Price')
	ax1.label_outer()

	setFrameColors(ax1)
	ax1.set_facecolor('#070008')
	ax1.tick_params(axis='y', colors='w')
	ax1.grid(True, color='w', linestyle='dotted', alpha=0.6)
	ax1.label_outer()
	ax1.set_xlim(left=timestamps[-span])
	ax1.set(ylabel = 'Price USD')

	ax1.plot(timestamps[-span:], av1[-span:], '#11ffcc', label=label1, linewidth=1, alpha=0.7)
	ax1.plot(timestamps[-span+1:], av2[-span:], '#FFA500', label=label2, linewidth=1, alpha=0.7)
	ax1.legend(loc=9, ncol=2, fancybox=True, prop={'size':10}).get_frame().set_alpha(0.4)
	ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
	ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) #Set date format as YYYY-mm-dd

	ax12 = ax1.twinx()
	ax12.set(ylabel='Price BTC')
	ax12.tick_params(axis='y', colors='w')

	emaslow, emafast, macd = computeMACD(prices_usd)
	ema9 = ExpMovingAverage(macd, 9)
	ax2.plot(timestamps, macd[-len(timestamps):])
	ax2.plot(timestamps, ema9[-len(timestamps):])

	ax2.fill_between(timestamps, macd[-len(timestamps):])

	ax2.tick_params(axis='x', colors='w')
	ax2.set_xlim(left=timestamps[-span])
	setFrameColors(ax2)
	ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
	ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S')) #Set date format as YYYY-mm-dd

	plt.subplots_adjust(left=0.09, bottom=0.14, right=0.94, top=0.92, wspace=0.2, hspace=0.0)
	plt.suptitle(ticker + ' Price', color='w')

	for label in ax2.xaxis.get_ticklabels():
		label.set_rotation(45)

	f.tight_layout()
	plt.show()

graphData(ticker, sma_short, sma_long)
