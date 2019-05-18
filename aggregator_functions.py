import pandas as pd
import numpy as np
import plotly.graph_objs as go
from pandas.io.json import json_normalize
import dash_core_components as dcc
from plotly import tools
from big_ol_db import BigOlDB
from constants import style_dicts as styles, value_dicts as vals


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

	def make_stacked_plot(self, df):

		import pdb; pdb.set_trace()  # breakpoint 35961c32 //

		recent_price_dict = {ticker : df[ticker].iloc[-1] for ticker in df.columns}
		recent_price_dict_sorted = sorted(recent_price_dict.items(), key=lambda x: x[1], reverse=True)

		new_df = pd.DataFrame()
		for i, ticker in enumerate([elem[0] for elem in recent_price_dict_sorted]):
			if ticker == recent_price_dict_sorted[0][0]:
				new_df[ticker] = df[ticker]
			else:
				new_df[ticker] = df[ticker] + new_df[recent_price_dict_sorted[i-1][0]]

		return new_df

	def get_fig(self, ticker):
		
		fig = tools.make_subplots(rows=4, cols=1, specs=[[{}], [{}], [{}], [{}]], 
							  shared_xaxes=True, shared_yaxes=False,
							  vertical_spacing=0.001)

		# So that it doesn't recalculate redundant values
		if ticker != self.ticker:
			self.ticker = ticker
			quotes = self.bodb.get_minutely_sector_data(ticker)

			self.df = quotes

		components_df = json_normalize(self.df["MarketCap_Weighted"])

		new_df = self.make_stacked_plot(components_df)

		for ticker in new_df.columns:

			trace_price = go.Scatter(
					x=self.df['TimeStampID'],
					y=new_df[ticker],
					mode='lines',
					# stackgroup='one',
					fill='tonexty',
					line={
						# 'color': styles.colors['current_price_line'],
						'width': 2.5
						},
					name=ticker,
					yaxis='y2')

			fig.append_trace(trace_price, 2, 1)

		# trace_rsi = go.Scatter(
		# 			x=self.df['TimeStampID'],
		# 			y=self.rsi(self.df['Price_{}'.format(currency_type)]),
		# 			mode='lines',
		# 			line={
		# 				'color': styles.colors['rsi'],
		# 				'width': styles.graph_layout['line_width']['rsi']
		# 				},
		# 			name='RSi',
		# 			yaxis='y',
		# 			)

		# if candlestick:
		# 	dff = self.refactor_to_ohlc(self.df, currency_type)
		# 	trace_price = go.Candlestick(
		# 			x=dff['TimeStamp'],
		# 			open=dff['Open'],
		# 			high=dff['High'],
		# 			low=dff['Low'],
		# 			close=dff['Close'],
		# 			name='OHLC',
		# 			increasing={
		# 				'line': {
		# 					'color': styles.colors['candlestick']['increasing']
		# 					},
		# 				'fillcolor': styles.colors['candlestick']['increasing']
		# 				},
		# 			decreasing={
		# 				'line': {
		# 					'color': styles.colors['candlestick']['decreasing']
		# 					},
		# 				'fillcolor': styles.colors['candlestick']['decreasing']
		# 				},
		# 			)

		# else:
		# 	trace_price = traces

		# trace_volume = go.Scatter(
		# 			x=self.df['TimeStampID'],
		# 			y=self.df['Volume24hr_USD'],
		# 			mode='lines',
		# 			name='24hr Volume - USD',
		# 			fill='tozeroy',
		# 			line={
		# 				'color': styles.colors['volume_line'],
		# 				'width': 1
		# 				},
		# 			fillcolor=styles.colors['volume_fill'], #'rgba(26,150,65,0.5)'
		# 			yaxis='y1'
					# )

		# fig.append_trace(trace_rsi, 3, 1)
		# fig.append_trace(traces, 2, 1)
		# fig.append_trace(trace_volume, 1, 1)

		# if 'sma' in requested_mas:
		# 	self.df['SMA'] = self.df['Price_{}'.format(currency_type)].rolling(short_window).mean()
		# 	trace_sma = go.Scatter(
		# 		x=self.df['TimeStampID'],
		# 		y=self.df['SMA'],
		# 		mode='lines',
		# 		line={
		# 				'color': styles.colors['sma_line'],
		# 				'width': 1
		# 				},
		# 		name='{}-Day Avg {}'.format(short_window, currency_type))
		# 	fig.append_trace(trace_sma, 2, 1)

		# if 'lma' in requested_mas:
		# 	self.df['LMA'] = self.df['Price_{}'.format(currency_type)].rolling(long_window).mean()
		# 	trace_lma = go.Scatter(
		# 		x=self.df['TimeStampID'],
		# 		y=self.df['LMA'],
		# 		mode='lines',
		# 		line={
		# 				'color': styles.colors['lma_line'],
		# 				'width': 1
		# 				},
		# 		name='{}-Day Avg {}'.format(long_window, currency_type))
		# 	fig.append_trace(trace_lma, 2, 1)

		return fig
