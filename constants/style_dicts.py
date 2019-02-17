base_colors = {
	'white': '#FFFFFF',
	'grey': '#777777',
	'black': '#000000',
	'transparent': 'rgba(0,0,0,0)',
	'darkgrey': '#444444',
}

colors = {
	#main theme colors
	'background': '#070008',
	'title_font': base_colors['white'],

	# RSi colors
	'rsi': '#00ffff',
	'rsi_highlow': '#00ffe8',

	# price colors
	'current_price_line': '#5998FF',
	'sma_line': '#11FFCC',
	'lma_line': '#FFA500',
	'legend_bg': base_colors['grey'],

	# volume colors
	'volume_line': '#59B8BF',
	'volume_fill': 'rgba(25,280,255,0.4)',

	# candlestick stuff (obviously)
	'candlestick': {
		'increasing': '#FFFF00',
		'decreasing': '#FF2323'
	},

	#chart colors
	'gridcolor': base_colors['darkgrey'],
	'titlefont': base_colors['grey'],
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
	'tickangle': -30,
	'domains': {
		'y2_top': 0.8,
		'y2_bottom': 0.2,
		'padding': 0.03
	},
	'tickfont': {
		'family': 'verdana',
		'size': 12,
		'color': base_colors['grey'],
	},
	'line_width': {
		'rsi': 2,
		'rsi_lowhigh': 1.25,
		'current_price': 2.5,
		'avg_price': 1.25,

		'volume': 1.5
	}
}

range_selector_buttons = {
	'buttons': [{
			'count': 1,
			'label': '1m',
			'step': 'month',
			'stepmode': 'backward'},
		{
			'count': 3,
			'label': '3m',
			'step': 'month',
			'stepmode': 'backward'},
		{
			'count': 6,
			'label': '6m',
			'step': 'month',
			'stepmode': 'backward'},
		{
			'count': 1,
			'label': 'YTD',
			'step': 'year',
			'stepmode': 'backward'},
		{	
			'count': 1,
			'label': '1y',
			'step': 'year',
			'stepmode': 'backward'},
		{
			'step': 'all'}]
	}