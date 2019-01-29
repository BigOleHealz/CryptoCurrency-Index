#!/usr/bin/env python3
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly import tools
from constants import style_dicts as styles, value_dicts as vals


def refactor_to_ohlc(df,  currency_type, candlestick_window=50):
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

def rsi(prices, n=35):
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

def get_fig(ticker, df, currency_type, requested_mas, candlestick, 
			short_window=25, long_window=70):
	
	trace_rsi = go.Scatter(
				x=df['TimeStampID'],
				y=rsi(df['Price_{}'.format(currency_type)]),
				mode='lines',
				line={
					'color': styles.colors['rsi'],
					'width': styles.graph_layout['line_width']['rsi']
					},
				name='RSi',
				yaxis='y',
				)

	if candlestick:
		dff = refactor_to_ohlc(df, currency_type)
		trace_price = go.Candlestick(x=dff['TimeStamp'],
                open=dff['Open'],
                high=dff['High'],
                low=dff['Low'],
                close=dff['Close'],
                name='OHLC',
                increasing={
                	'line': {
                		'color': '#FFFF00'
            			},
            		'fillcolor': '#3D00FF'
            		},
            	decreasing={
                	'line': {
                		'color': '#3D00FF'
            			},
            		'fillcolor': '#3D00FF'
            		},
			)

	else:
		trace_price = go.Scatter(
				x=df['TimeStampID'],
				y=df['Price_{}'.format(currency_type)],
				mode='lines',
				line={
					'color': styles.colors['current_price_line'],
					'width': 2.5
					},
				name='Price {}'.format(currency_type),
				yaxis='y2')
	trace_volume = go.Scatter(
				x=df['TimeStampID'],
				y=df['Volume24hr_USD'],
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
	
	fig = tools.make_subplots(rows=4, cols=1, specs=[[{}], [{}], [{}], [{}]], 
                          shared_xaxes=True, shared_yaxes=False,
                          vertical_spacing=0.001)
	fig.append_trace(trace_rsi, 1, 1)
	fig.append_trace(trace_price, 2, 1)
	fig.append_trace(trace_volume, 3, 1)

	if 'sma' in requested_mas:
		df['SMA'] = df['Price_{}'.format(currency_type)].rolling(short_window).mean()
		trace_sma = go.Scatter(
			x=df['TimeStampID'],
			y=df['SMA'],
			mode='lines',
			line={
					'color': styles.colors['sma_line'],
					'width': 1
					},
			name='{}-Day Avg {}'.format(short_window, currency_type))
		fig.append_trace(trace_sma, 2, 1)

	if 'lma' in requested_mas:
		df['LMA'] = df['Price_{}'.format(currency_type)].rolling(long_window).mean()
		trace_lma = go.Scatter(
			x=df['TimeStampID'],
			y=df['LMA'],
			mode='lines',
			line={
					'color': styles.colors['lma_line'],
					'width': 1
					},
			name='{}-Day Avg {}'.format(long_window, currency_type))
		fig.append_trace(trace_lma, 2, 1)

	fig['layout'].update(title='Stacked Subplots with Shared X-Axes',
		autosize=True,
		height=800,
		width=1450,
		paper_bgcolor=styles.base_colors['transparent'],
	    plot_bgcolor=styles.base_colors['transparent'],
	    titlefont={'color': styles.colors['title_font']},
	    legend={'bgcolor': styles.colors['legend_bg']},
	    margin=styles.graph_layout['margins'],
	    grid={'rows': 5},
	    xaxis={'color': styles.base_colors['white'],
	    	'tickangle': styles.graph_layout['tickangle'],
	    	'gridcolor': styles.base_colors['grey'],
	    	'rangeslider': {'visible': True}},
	    yaxis={'domain':[0, 1],
	    	'color': styles.base_colors['white'],
	    	'tickangle': styles.graph_layout['tickangle'],
	    	'domain':[styles.graph_layout['domains']['y2_top'] + \
	    		styles.graph_layout['domains']['padding'], 1]
	    	},
	    yaxis2={
	    	'color': styles.base_colors['white'],
	    	'tickangle': styles.graph_layout['tickangle'],
	    	'domain':[styles.graph_layout['domains']['y2_bottom'], 
	    		styles.graph_layout['domains']['y2_top']], 'anchor': 'y2'},
	    yaxis3={
	    	'color': styles.base_colors['white'],
	    	'tickangle': styles.graph_layout['tickangle'],
	    	'domain':[0, styles.graph_layout['domains']['y2_bottom'] - \
	    		styles.graph_layout['domains']['padding']], 
	    	'anchor': 'y3'}
	    ),



	return fig
