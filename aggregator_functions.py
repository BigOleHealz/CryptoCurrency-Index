#!/usr/bin/env python3
import pandas as pd
import numpy as numpy
import plotly.graph_objs as go
from plotly import tools
from styles import style_dicts

def movingAverage(values, window):
	arr_avg = values.rolling(window).mean()

	return arr_avg

##### SLOPPY #####
def get_fig(df, currency_type, requested_mas, short_window=25, long_window=70):

	trace_price = go.Scatter(
				x=df['TimeStampID'],
				y=df['Price_{}'.format(currency_type)],
				mode='lines',
				line={
					'color': style_dicts.colors['current_price_line'],
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
					'color': style_dicts.colors['volume_line'],
					'width': 1
					},
				fillcolor=style_dicts.colors['volume_fill'], #'rgba(26,150,65,0.5)'
				# yaxis='y1'

				)
	
	fig = tools.make_subplots(rows=3, cols=1, specs=[[{}], [{}], [{}]],
                          shared_xaxes=True, shared_yaxes=False,
                          vertical_spacing=0.001)
	fig.append_trace(trace_price, 2, 1)
	fig.append_trace(trace_volume, 3, 1)

	lay = fig['layout']
	leg = lay['legend']

	if 'sma' in requested_mas:
		df['SMA'] = df['Price_{}'.format(currency_type)].rolling(short_window).mean()
		trace_sma = go.Scatter(
			x=df['TimeStampID'],
			y=df['SMA'],
			mode='lines',
			line={
					'color': style_dicts.colors['sma_line'],
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
					'color': style_dicts.colors['lma_line'],
					'width': 1
					},
			name='{}-Day Avg {}'.format(long_window, currency_type))
		fig.append_trace(trace_lma, 2, 1)

	fig['layout'].update(title='Stacked Subplots with Shared X-Axes',
		autosize=True,
		paper_bgcolor=style_dicts.colors['transparent'],
	    plot_bgcolor=style_dicts.colors['transparent'],
	    titlefont={'color': style_dicts.colors['title_font']},
	    legend={'bgcolor': style_dicts.colors['legend_bg']},
	    margin=style_dicts.graph_layout['margins'],
	    grid={'rows': 5},
	    xaxis={'color': style_dicts.base_colors['white'],
	    	'tickangle': style_dicts.graph_layout['tickangle']},
	    yaxis={'domain':[0, 0.3],
	    	'color': style_dicts.base_colors['white'],
	    	'tickangle': style_dicts.graph_layout['tickangle'],
	    	'domain':[0, 0.3]
	    	# 'anchor': 'y2'
	    	},
	    yaxis2={
	    	'color': style_dicts.base_colors['white'],
	    	'tickangle': style_dicts.graph_layout['tickangle'],
	    	'domain':[0, 1], 'anchor': 'y2'},
	    ),



	return fig
