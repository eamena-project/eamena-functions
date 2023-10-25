import argparse
import pandas as pd
import numpy as np
import re
import requests
import json
import ipywidgets as widgets
from IPython.display import display
import matplotlib.pyplot as plt
import plotly.express as px
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

argp = argparse.ArgumentParser()
argp.add_argument('GEOJSON_URL', type=str, help='The GeoJSON URL coming from a Search in the EAMENA database', default='')
argp.add_argument('VERBOSE', type=bool, help='Verbose, True or False', default=False)
args = argp.parse_args()

# print(args.GEOJSON_URL)

def db_query(GEOJSON_URL = None):
	# return a JSON file (GeoJSON)
	resp = requests.get(GEOJSON_URL)
	return(resp.json())

def erms_template(tsv_file = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/dev/data_quality/erms-template-readonly.tsv"):
	df = pd.read_csv(tsv_file, delimiter = '\t')
	df = df[["level1", "level2", "level3", "uuid_sql", "Enhanced record minimum standard"]]
	df_listed = df.dropna()
	# if verbose:
	# 	print(df_listed.to_markdown())
	return(df_listed)

def erms_template_levels(radio_button = None, df_erms = None)
	# it use a value coming from a Jupyter NB radio button
	mylevel = radio_button.value
	df_erms = df_listed.copy()
	df_erms['Enhanced record minimum standard'] = df_erms['Enhanced record minimum standard'].str.contains(r'Yes', case = False, na = False, regex = True).astype(int)
	df_erms = df_erms[[mylevel, "Enhanced record minimum standard"]]
	df_erms.columns.values[0] = "field"
	df_erms = df_erms.groupby(['field'])['Enhanced record minimum standard'].sum()
	print(f'You selected: {mylevel}')
	df_erms = pd.DataFrame({
		'field': df_erms.index,
		'value' : df_erms.values
					})
	# print(df_erms.to_markdown(index=False))
	return(df_erms)

def hps_dict(df_listed = None, mylevel = "level3"):
	# Keys are EAMENA IDs and values are HP fields filled or not
	verbose = True
	level_values = df_listed[mylevel].unique()
	l_erms = []
	dict_hps = {} 
	# len(selected_hp)
	for i in range(5):
		a_hp = selected_hp[i]
		if verbose:
			print("read: " + a_hp)
		# create an empty df
		df_res = pd.DataFrame({'field': level_values, 
							'recorded': np.repeat(0, len(level_values)).tolist()})
		# len(df_res)
		for j in range(len(df_res)):
			a_field = df_res.iloc[j]["field"]
			try:
				a_value = hps['features'][i]['properties'][a_field]
				if verbose:
					print("field: '" + a_field + "' has value :'" + str(a_value) + "'")
			# TODO: change to warning?
			except:
				if verbose:
					print(" /!\ '" + a_field + "' listed in the ERMS dataframe is a level1 or level2 value, but is not a field listed in the database")
			if a_value is not None:
				# row_num = df_res[df_res['field'] == df_field].index.tolist()
				df_res.at[j, 'recorded'] = df_res.loc[j]['recorded'] + 1
		l_erms.append(df_res)
		dict_hps[a_hp] = df_res
	return(dict_hps)

def plot_spidergraphs(dict_hps = None, df_erms = None, mylevel = "level3", ncol = 3):
	# grid dimensions
	nrow = math.ceil(len(dict_hps.keys()) / ncol)
	fig = make_subplots(rows=nrow, cols=ncol, specs=[[{'type': 'polar'}]*ncol]*nrow, subplot_titles=tuple(dict_hps.keys()))
	current_column, current_row = 1, 1
	# dict_hps.keys()
	for a_hp in dict_hps.keys():
		df = dict_hps[a_hp]
		print(a_hp)
		if mylevel == 'level3':
			# overlap two plots
			fig.add_trace(go.Scatterpolar(
				name =  "  erms",
				r = df_erms['value'],
				theta = df_erms['field'],
				fill='toself',
				fillcolor='red',
				line_color='red',
				hovertemplate="<br>".join([
				"value: %{r}",
				"field: %{theta}"]),
				showlegend=False), 
				current_row, current_column)		
			fig.add_trace(go.Scatterpolar(
				name = a_hp,
				r = df['recorded'],
				theta = df['field'],
				mode = 'markers',
				marker_color = "blue",
				hovertemplate="<br>".join([
				"value: %{r}",
				"field: %{theta}"])
				), 
				current_row, current_column)
		else:
			# only the plot of the HP
			fig.add_trace(go.Scatterpolar(
				name = a_hp,
				r = df['recorded'],
				theta = df['field'],
				mode = 'markers',
				marker_color = "blue",
				hovertemplate="<br>".join([
				"value: %{r}",
				"field: %{theta}"]),
				showlegend=False), 
				current_row, current_column)	
		current_column = current_column + 1
		# end of line..
		if current_column == ncol:
			current_row = current_row + 1
			current_column = 1
	fig.show()

hps = db_query(GEOJSON_URL) 
df_listed = erms_template()
# get the level and group data
df_erms = erms_template_levels(radio_button, df_erms)
# create dictionnary of HP
dict_hps = hps_dict(df_listed, mylevel)
plot_spidergraphs(dict_hps, df_erms, mylevel)