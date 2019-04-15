import styles.value_dicts as vals

tickangle = -30

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

tickfont = {
	'family': 'Old Standard TT, serif',
    'size': 14,
    'color': 'lightgrey'
}

graph_layout = {
	'tickangle': -30,
	'autosize': True,
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
	'paper_bgcolor': base_colors['transparent'],
	'plot_bgcolor': base_colors['transparent'],
	'titlefont': {
		'color': colors['titlefont']
	},
	'legend': {
		'bgcolor': colors['legend_bg'],
		'font': {
			'family': 'verdana',
			'color': base_colors['black']
		}
	},
	'grid': {'rows': 5},
	'xaxis': {
		'title': 'Date',
		'titlefont': tickfont,
		'color': colors['titlefont'],
		'tickangle': tickangle,
		'tickfont': tickfont,
		'gridcolor': base_colors['grey'],
		'rangeslider': {'visible': True},
		'gridcolor': colors['gridcolor'],
	},
	'yaxis': {
		'title': 'Volume',
		'titlefont': tickfont,
		'color': colors['titlefont'],
		'gridcolor': colors['gridcolor'],
		'tickangle': tickangle,
		'tickcolor': colors['background'], 
		'tickfont': tickfont,
		'domain':[0, vals.domains['y2_bottom'] - vals.domains['padding']],
		'anchor': 'y3'
	},

	'yaxis2': {
		'title': 'Price USD',
		'titlefont': tickfont,
		'color': colors['titlefont'],
		'gridcolor': colors['gridcolor'],
		'tickangle': tickangle,
		'tickcolor': colors['background'],
		'tickfont': tickfont,
		'domain': [vals.domains['y2_bottom'], vals.domains['y2_top']], 
		'anchor': 'y2'
	},
	
	'yaxis3': {
		'title': 'RSi',
		'titlefont': tickfont,
		'color': colors['titlefont'],
		'gridcolor': colors['gridcolor'],
		'tickangle': tickangle,
		'tickcolor': colors['background'], 
		'tickfont': tickfont,
		'domain':[vals.domains['y2_top'] + vals.domains['padding'], 1],
		'range': [-5, 105],
		'zeroline': False
	}


}

