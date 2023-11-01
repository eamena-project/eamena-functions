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

# argp = argparse.ArgumentParser()
# argp.add_argument('GEOJSON_URL', type=str, help='The GeoJSON URL coming from a Search in the EAMENA database', default='')
# argp.add_argument('VERBOSE', type=bool, help='Verbose, True or False', default=False)
# args = argp.parse_args()

# print(args.GEOJSON_URL)

def db_query(GEOJSON_URL = None):
	"""
	Return a JSON file (GeoJSON) from a GeoJSON URL

	Use the Arches REST API with a GeoJSON URL (in Arches: Export > GeoJSON URL) to collect selected Heritage Places in a GeoJSON format

	:param GEOJSON_URL: The GeoJSON URL

	:Example: 
	>> GEOJSON_URL = "https://database.eamena.org/api/search/..."
	>> hps = erms.db_query()
	"""
	resp = requests.get(GEOJSON_URL)
	return(resp.json())

def hps_list(hps = None):
	"""
	Store the EAMENA ID in a list 

	:param hps: a dict() coming from reading of a JSON (GeoJSON). See the function `db_query()`

	:return: A list of EAMENA IDs

	:Example: 
	>> GEOJSON_URL = "https://database.eamena.org/api/search/..."
	>> hps = erms.db_query(GEOJSON_URL)
	>> selected_hp = erms.hps_list(hps)

	"""
	selected_hp = []
	for i in range(len(hps['features'])):
		selected_hp.append(hps['features'][i]['properties']['EAMENA ID'])
	return(selected_hp)

def erms_template(tsv_file = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/dev/data_quality/erms-template-readonly.tsv"):
	"""
	Dataframe of ERMS individual fields

	Dataframe of ERMS individual fields

	:param tsv_file: the path to the read-only TSV file of ERMS
	:param radio_button: a value coming from a Jupyter NB radio button

	:return: Dataframe of ERMS individual fields
	"""
	df = pd.read_csv(tsv_file, delimiter = '\t')
	df_listed = df[["level1", "level2", "level3", "Enhanced record minimum standard"]]
	# df_listed = df.dropna()
	# if verbose:
	# 	print(df_listed.to_markdown())
	return(df_listed)

def erms_template_levels(tsv_file = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/dev/data_quality/erms-template-readonly.tsv", radio_button = None):
	"""
	Dataframe of ERMS individual or aggregated fields

	Taking a level of aggregation (level1, level2, etc.), group and sum ERMS fields (level3) into broader categories

	:param tsv_file: the path to the read-only TSV file of ERMS
	:param radio_button: a value coming from a Jupyter NB radio button

	:return: Dataframe of ERMS individual or aggregated fields
	"""
	mylevel = radio_button.value
	df_listed = erms_template(tsv_file)
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

def hps_dict(selected_hp = None, df_listed = None, mylevel = "level3", verbose = False):
	# Keys are EAMENA IDs and values are HP fields filled or not
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
				a_value = None
			if a_value is not None:
				# row_num = df_res[df_res['field'] == df_field].index.tolist()
				df_res.at[j, 'recorded'] = df_res.loc[j]['recorded'] + 1
		l_erms.append(df_res)
		dict_hps[a_hp] = df_res
	return(dict_hps)

def plot_spidergraphs(dict_hps = None, df_erms = None, mylevel = "level3", ncol = 3, verbose = False):
	ncol = 3
	nrow = math.ceil(len(dict_hps.keys()) / ncol)
	fig = make_subplots(rows=nrow, cols=ncol, specs=[[{'type': 'polar'}]*ncol]*nrow, subplot_titles=tuple(dict_hps.keys()))
	df_erms_1 = df_erms.copy() # to add +1 later
	df_erms_1.loc[df_erms_1['value'] == 0, 'value'] = -1
	current_column, current_row = 1, 1
	for a_hp in dict_hps.keys():
		df = dict_hps[a_hp]
		if verbose:
			print(a_hp)
			print(str(current_row) + " " + str(current_column))
		if mylevel == 'level3':
			fig.add_trace(go.Scatterpolar(
			name =  "  erms",
			r = df_erms_1['value'],
			theta = df_erms_1['field'],
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
			# marker=dict(color = melted_df_color),
			marker_color = "blue",
			hovertemplate="<br>".join([
			"value: %{r}",
			"field: %{theta}"])
			), 
			current_row, current_column)
		else:
			fig.add_trace(go.Scatterpolar(
			name = a_hp,
			r = df['recorded'],
			theta = df['field'],
			mode = 'markers',
			marker_color = "blue",
			hovertemplate="<br>".join([
			"value: %{r}",
			"field: %{theta}"]),
			showlegend=False,
			text="None"), 
			current_row, current_column)
		current_column = current_column + 1
		# end of line..
		if current_column > ncol:
			current_row = current_row + 1
			current_column = 1
	fig.update_layout(
		autosize=False,
		width=(ncol*700) + 200,
		height=(nrow*300) + 100,
	)
	fig.update_layout(
		polar=dict(
			radialaxis=dict(
				# showline=False,
				range=[-1, 1],  # Set the range for the radial axis
				tickvals=[0, 1],  # Specify the tick values
				ticktext=['0', '1'],  # Specify the corresponding labels
			),
			# hide labels
			angularaxis=dict(
				showline=False,          # Set to False to hide the angular axis line
				showticklabels=False,    # Set to False to hide the angular axis labels
			)
		),
		showlegend=True
	)
	fig.show()

def filter_dataframe(selected_value):
	"""
	Filter a dataframe giving a selected alue coming from a radio button

	:param selected_value: value returned by the on_radio_button_change() function, it is a GS ID

	:return: Dataframe of existing HP is a given GS
	"""
	hps_to_keep = list()
	hps_gs = dict()
	hps_gs['features'] = []
	for i in range(len(selected_hp)):
		gs_current = selected_hp['features'][i]['properties']['Grid ID']
		if gs_current == selected_value:
		# if gs_current ==  radio_button_1.value:
			hps_to_keep.append(i)
		feat = [selected_hp['features'][i] for i in hps_to_keep]
	for i in range(len(feat)):
		hps_gs['features'].append(feat[i])
	selected_hp_gs = []
	for i in range(len(hps_gs['features'])):
		selected_hp_gs.append(hps_gs['features'][i]['properties']['EAMENA ID'])
	return(selected_hp_gs)

def filter_hp_by_gs(selected_hp):
	"""
	Filter a dataframe giving a selected value coming from a radio button

	List all GS listed in the HP. Display a radio button to show these HP by GS. Display a radio button for the selection of the GS

	:param selected_hp: a list of HP in a dict shape (GeoJSON)

	:return: Update a copy of the HP list filtered on a given GS
	"""
	l_GridIDs = []
	for i in range(len(selected_hp)):
		l_GridIDs.append(selected_hp['features'][i]['properties']['Grid ID'])
	l_GridIDs = list(set(l_GridIDs))
	l_GridIDs.sort()
	radio_button_1 = widgets.RadioButtons(
		options = l_GridIDs,
		description = 'Select a Grid Square:'
	)
	# Create an output widget to display the filtered DataFrame
	output = widgets.Output()

def on_radio_button_change(change):
	global filtered_df
	selected_value = change.new
	# print(selected_value)
	with output:
		# Clear previous output
		output.clear_output()
		# Call a function. Filter the DataFrame based on the selected value
		filtered_df = filter_dataframe(selected_value)
		print(filtered_df, end="")
		# return(filtered_df)
	# Link the RadioButtons widget to the change event
	radio_button_1.observe(on_radio_button_change, names='value')
	display(radio_button_1, output)

# Not Run
# filtered_data = filter_hp_by_gs(selected_hp)