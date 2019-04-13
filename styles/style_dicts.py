base_colors = {
'white': '#FFFFFF',
'grey': '#777777',
'black': '#000000',
'lightgrey': 'lightgrey'
}

colors = {
	'background': '#070008',
	'current_price_line': '#5998FF',
	'volume_line': '#59B8BF',
	'volume_fill': 'rgba(25,280,255,0.5)',
	'sma_line': '#11FFCC',
	'lma_line': '#FFA500',
	'titlefont': base_colors['white'],
	'transparent': 'rgba(0,0,0,0)',
	'legend_bg': base_colors['grey'],
	'candlestick': {
		'increasing': '#FFFF00',
		'decreasing': '#3D00FF'
	},
	'rsi': '#00ffe8',
	'gridcolor': base_colors['grey']
	
}

axis_label_font = {
    'family': 'Arial, sans-serif',
    'size': 18,
    'color': 'lightgrey'
}

tickfont = {
	'family': 'Old Standard TT, serif',
    'size': 14,
    'color': base_colors['lightgrey']
}

graph_layout = {
	'margins': {
		'l': 60, 
		'b': 45, 
		't': 25, 
		'r': 0
	},
	'width': 600,
	'xaxis': {
		'title': 'Date',
		'titlefont': {
			'family': 'verdana',
			'size': 12,
			'color': colors['titlefont']
		},
		'color': colors['titlefont'],
		'tickangle': -30,
		'tickfont': tickfont,
		'gridcolor': base_colors['lightgrey'],
		# 'rangeslider': {'visible': False},
	}
}