#!/usr/bin/env python3
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import dash_core_components as dcc
from plotly import tools
from big_ol_db import BigOlDB
from styles import style_dicts as styles, value_dicts as vals


class AggregatorFunctions:

	def __init__(self):
		self.ticker = 'BTC'
		self.bodb = BigOlDB()
		self.df = self.bodb.get_minutely_coin_data(self.ticker)


	def refactor_to_ohlc(self, df, currency_type, candlestick_window=50):
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

	def rsi(self, prices, n=135):
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

	def get_fig(self, ticker, currency_type, requested_mas, candlestick, 
				short_window=25, long_window=70):
		
		fig = tools.make_subplots(rows=3, cols=1, specs=[[{}], [{}], [{}]], 
							  shared_xaxes=True, shared_yaxes=False,
							  vertical_spacing=0.001)
		if ticker != self.ticker:
			self.ticker = ticker
			quotes = self.bodb.get_minutely_coin_data(ticker)
			self.df = quotes

		trace_rsi = go.Scatter(
					x=self.df['TimeStampID'],
					y=self.rsi(self.df['Price_{}'.format(currency_type)]),
					mode='lines',
					line={
						'color': styles.colors['rsi'],
						'width': 8
						},
					name='RSi',
					yaxis='y',
					)

		if candlestick:
			dff = self.refactor_to_ohlc(self.df, currency_type)
			trace_price = go.Candlestick(
					x=dff['TimeStamp'],
					open=dff['Open'],
					high=dff['High'],
					low=dff['Low'],
					close=dff['Close'],
					name='OHLC',
					increasing={
						'line': {
							'color': styles.colors['candlestick']['increasing']
							},
						'fillcolor': styles.colors['candlestick']['increasing']
						},
					decreasing={
						'line': {
							'color': styles.colors['candlestick']['decreasing']
							},
						'fillcolor': styles.colors['candlestick']['decreasing']
						},
					)

		else:
			trace_price = go.Scatter(
					x=self.df['TimeStampID'],
					y=self.df['Price_{}'.format(currency_type)],
					mode='lines',
					line={
						'color': styles.colors['current_price_line'],
						'width': 2.5
						},
					name='Price {}'.format(currency_type),
					yaxis='y2')
		trace_volume = go.Scatter(
					x=self.df['TimeStampID'],
					y=self.df['Volume24hr_USD'],
					mode='lines',
					name='24hr Volume - USD',
					fill='tozeroy',
					line={
						'color': styles.colors['volume_line'],
						'width': 1
						},
					fillcolor=styles.colors['volume_fill'], #'rgba(26,150,65,0.5)'
					yaxis='y1'
					)

		fig.append_trace(trace_rsi, 3, 1)
		fig.append_trace(trace_price, 2, 1)
		fig.append_trace(trace_volume, 1, 1)

		if 'sma' in requested_mas:
			self.df['SMA'] = self.df['Price_{}'.format(currency_type)].rolling(short_window).mean()
			trace_sma = go.Scatter(
				x=self.df['TimeStampID'],
				y=self.df['SMA'],
				mode='lines',
				line={
						'color': styles.colors['sma_line'],
						'width': 1
						},
				name='{}-Day Avg {}'.format(short_window, currency_type))
			fig.append_trace(trace_sma, 2, 1)

		if 'lma' in requested_mas:
			self.df['LMA'] = self.df['Price_{}'.format(currency_type)].rolling(long_window).mean()
			trace_lma = go.Scatter(
				x=self.df['TimeStampID'],
				y=self.df['LMA'],
				mode='lines',
				line={
						'color': styles.colors['lma_line'],
						'width': 1
						},
				name='{}-Day Avg {}'.format(long_window, currency_type))
			fig.append_trace(trace_lma, 2, 1)

		return fig
