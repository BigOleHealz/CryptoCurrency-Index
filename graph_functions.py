#!/usr/bin/env python3
import json, plotly, numpy as np
from big_ol_db import BigOlDB
import plotly.graph_objs as go
import styles.style_dicts as styles

def create_plot(feature, ticker):
	bodb = BigOlDB()
	df = bodb.get_minutely_coin_data(ticker)


	if feature == 'Bar':
		trace_price = go.Bar(
			x=df['TimeStampID'],
			y=df['Price_USD']
		)
	else:
		dff = refactor_to_ohlc(df, currency_type='USD')
		trace_price = go.Candlestick(
			x=dff['TimeStamp'],
			open=dff['Open'],
			high=dff['High'],
			low=dff['Low'],
			close=dff['Close'],
			name='OHLC'
		)

	trace_rsi = go.Scatter(
		x=df['TimeStampID'],
		y=rsi(df['Price_USD']),
		mode='lines',
		line={
			'color': styles.colors['rsi'],
			},
		name='RSi',
		yaxis='y'
	) 

	data = [trace_price, trace_rsi]
	data = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

	layout = styles.graph_layout

	return {'data': data, 'layout': layout}



def rsi(prices, n=135):
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




def refactor_to_ohlc(df, currency_type, candlestick_window=50):
	df['candle_num'] = df.index // candlestick_window
	df['index'] = df.index

	dff = df.groupby('candle_num')['TimeStampID', 'Price_{}'.format(
		currency_type)].max()
	dff.rename(columns={
		'TimeStampID': 'TimeStamp',
		'Price_{}'.format(currency_type): 'High'},
		inplace=True)
	dff['Low'] = df.groupby('candle_num')['Price_{}'.format(currency_type)].min()
	dff['Open'] = df.groupby('candle_num')['Price_{}'.format(currency_type)].first()
	dff['Close'] = df.groupby('candle_num')['Price_{}'.format(currency_type)].last()

	return dff