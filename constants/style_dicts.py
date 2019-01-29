base_colors = {
'white': '#FFFFFF',
'grey': '#777777',
'black': '#000000',
'transparent': 'rgba(0,0,0,0)',
}

colors = {
	'background': '#070008',
	'title_font': base_colors['white'],

	'rsi': '#00ffff',
	'rsi_highlow': '#00ffe8',

	'current_price_line': '#5998FF',
	'sma_line': '#11FFCC',
	'lma_line': '#FFA500',
	'legend_bg': base_colors['grey'],

	'volume_line': '#59B8BF',
	'volume_fill': 'rgba(25,280,255,0.5)',
}

axis_label_font = {
    'family': 'Arial, sans-serif',
    'size': 18,
    'color': 'lightgrey'
}

tick_font = {
	'family': 'Old Standard TT, serif',
    'size': 14,
    'color': 'lightgrey'
}

graph_layout = {
	'margins': {
		'l': 60, 
		'b': 45, 
		't': 25, 
		'r': 0,
		'pad': 4
	},
	'tickangle': -30,
	'domains': {
		'y2_top': 0.8,
		'y2_bottom': 0.2,
		'padding': 0.03
	},
	'line_width': {
		'rsi': 2,
		'rsi_lowhigh': 1.25,
		'current_price': 2.5,
		'avg_price': 1.25,

		'volume': 1.5
	}
}