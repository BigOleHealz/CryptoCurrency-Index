#!/usr/bin/env python3
import pandas as pd
import numpy as numpy
import plotly.graph_objs as go
from styles import style_dicts

def movingAverage(values, window):
	arr_avg = values.rolling(window).mean()

	return arr_avg

##### SLOPPY #####
def get_traces(df, currency_type, requested_mas, short_window=25, long_window=70):
	if 'sma' in requested_mas: 
		df['SMA'] = df['Price_{}'.format(currency_type)].rolling(short_window).mean()
	if 'lma' in requested_mas: 
		df['LMA'] = df['Price_{}'.format(currency_type)].rolling(long_window).mean()

	price_min = min(df['Price_USD'])
	price_max = max(df['Price_USD'])

	def scale_volume(dff):
		return 0.95 * price_min + (df['Volume24hr_USD'] * (df['Price_USD'][391] / (5 * df['Volume24hr_USD'][391])))

	data = [go.Scatter(
				x=df['TimeStampID'],
				y=df['Price_{}'.format(currency_type)],
				mode='lines',
				line={
					'color': style_dicts.colors['current_price_line'],
					'width': 2.5
					},
				name='Price {}'.format(currency_type)),
			# go.Scatter(
			# 	x=df['TimeStampID'],
			# 	y=scale_volume(df),
			# 	mode='lines',
			# 	name='24hr Volume - USD',
			# 	fill='tozeroy',
			# 	line={
			# 		'color': style_dicts.colors['volume_line'],
			# 		'width': 1
			# 		},
			# 	fillcolor=style_dicts.colors['volume_fill'] #'rgba(26,150,65,0.5)'
			# 	)
			]

	if 'sma' in requested_mas:
		data.append(go.Scatter(
			x=df['TimeStampID'],
			y=df['SMA'],
			mode='lines',
			line={
					'color': style_dicts.colors['sma_line'],
					'width': 1
					},
			name='{}-Day Avg {}'.format(short_window, currency_type))
		)
	if 'lma' in requested_mas:
		data.append(go.Scatter(
			x=df['TimeStampID'],
			y=df['LMA'],
			mode='lines',
			line={
					'color': style_dicts.colors['lma_line'],
					'width': 1
					},
			name='{}-Day Avg {}'.format(long_window, currency_type))
		)

	return data, price_min, price_max
