# bunch of functions to manage reference data

def nodes_uuids(choice = "rm", rm = "https://raw.githubusercontent.com/eamena-project/eamena/master/eamena/pkg/graphs/resource_models/Heritage%20Place.json", concept = "https://raw.githubusercontent.com/eamena-project/eamena/master/eamena/pkg/reference_data/concepts/EAMENA.xml", output_file_path='C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/reference_data/concepts/concepts_readonly.tsv', export=True):
	# Creates pandas dataframes from RM (JSON files) and Concepts (XML files)
	import requests
	import json
	import pandas as pd
	from lxml import etree
	if choice == "rm":
		print("*Read Resource Models")
		response = requests.get(rm)
		rm_data = json.loads(response.text)
		# Collect nodes' names and UUIDs from resource models
		df_nodes = pd.DataFrame(columns=['level3', 'uuid'])
		df_nodes = df_nodes.rename(columns={'level3': 'db.concept.name', 'uuid': 'db.concept.uuid'})
		for i in range(1, len(rm_data['graph'][0]['nodes'])):
			new_row = [rm_data['graph'][0]['nodes'][i]['name'], rm_data['graph'][0]['nodes'][i]['nodeid']]
		if not export:
			df_nodes.loc[i] = new_row
		return(df_nodes)
	if choice == "concept":
		print("*Read Concepts")
		response = requests.get(concept)
		root = etree.fromstring(response.content)
		id_value_pairs_corrected = []
		for concept in root.xpath('//skos:Concept', namespaces=root.nsmap):
			parent = concept.getparent()
			parent_pref_label = parent.find('skos:prefLabel', namespaces=root.nsmap) if parent is not None else None
			parent_content = json.loads(parent_pref_label.text) if parent_pref_label is not None and '{http://www.w3.org/XML/1998/namespace}lang' in parent_pref_label.attrib and parent_pref_label.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == "en-us" else {'id': None, 'value': None}
			for pref_label in concept.findall('skos:prefLabel', namespaces=root.nsmap):
				if '{http://www.w3.org/XML/1998/namespace}lang' in pref_label.attrib and pref_label.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == "en-us":
					content = json.loads(pref_label.text)
					# Include parent id and value along with the child's
					id_value_pairs_corrected.append((parent_content['id'], parent_content['value'], content['id'], content['value']))
		df = pd.DataFrame(id_value_pairs_corrected, columns=['parent_uuid', 'parent_concept', 'uuid', 'concept'])
		if export:
			df.to_csv(output_file_path, sep='\t', index=False)
			print("The TSV of Concepts has been created.")
		else:
			return df


def hp_mds_template(tsv_file = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/dbs/database.eamena/data/reference_data/rm/hp/mds/mds-template-readonly.tsv"):
	"""
	Dataframe of mds individual fields

	:param tsv_file: the path to the read-only TSV file of mds

	:return: Dataframe of mds individual fields
	"""
	import pandas as pd

	df = pd.read_csv(tsv_file, delimiter = '\t', skip_blank_lines = True)
	df_listed = df[["level1", "level2", "level3", "Enhanced record minimum standard",'uuid_sql','color']]
	# df_listed = df.dropna()
	# if verbose:
	# 	print(df_listed.to_markdown())
	return(df_listed)

def hp_mds_template_levels(tsv_file = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/dbs/database.eamena/data/reference_data/rm/hp/mds/mds-template-readonly.tsv", radio_button = None):
	"""
	Dataframe of mds individual or aggregated fields

	Taking a level of aggregation (level1, level2, etc.), group and sum mds fields (level3) into broader categories

	:param tsv_file: the path to the read-only TSV file of mds
	:param radio_button: a value coming from a Jupyter NB radio button

	:return: Dataframe of mds individual or aggregated fields
	"""
	import pandas as pd

	if radio_button != None:
		mylevel = radio_button.value
	else:
		mylevel = 'level3'
	df_listed = hp_mds_template(tsv_file)
	df_mds = df_listed.copy()
	df_mds['Enhanced record minimum standard'] = df_mds['Enhanced record minimum standard'].str.contains(r'Yes', case = False, na = False, regex = True).astype(int)
	df_mds = df_mds[[mylevel, "Enhanced record minimum standard"]]
	df_mds.columns.values[0] = "field"
	df_mds = df_mds.groupby(['field'])['Enhanced record minimum standard'].sum()
	print(f'You selected: {mylevel}')
	df_mds = pd.DataFrame({
		'field': df_mds.index,
		'value' : df_mds.values
					})
	# print(df_mds.to_markdown(index=False))
	return(df_mds)


def hp_mds_field_colors(level = 'level1', cmap = 'Dark2'):
	"""
	Return a dataframe of colors based on one of the levels to color graph nodes

	:param level1: a level. Default 'level1'
	:param cmap: a color ramp

	:return: Dataframe of 'level' colors

	:Example:
	>> df_color = mds_field_colors()
	"""
	import matplotlib.pyplot as plt
	from matplotlib.colors import to_hex
	import pandas as pd
	import numpy as np

	hp_mds_template_df = hp_mds_template()
	hp_mds_template_df = hp_mds_template_df.drop('Enhanced record minimum standard', axis=1)
	level1_cat = hp_mds_template_df[level].unique()
	my_cmap = plt.get_cmap(cmap)
	level1_cmap = my_cmap(np.linspace(0, 1, len(level1_cat)))
	level1_cmap = [to_hex(color) for color in level1_cmap]
	df_color = pd.DataFrame(columns=(level, 'color'))
	df_color[level] = level1_cat
	df_color['color'] = level1_cmap
	df_color = hp_mds_template_df.merge(df_color, on=level, how='left')
	return df_color


def hp_dict(hps = None, selected_hp = None, df_listed = None, mylevel = "level3", verbose = False):
	# Keys are EAMENA IDs and values are HP fields filled or not
	# create a dictionnary with the EAMENA ID as a key, and fields with values to assess which fields have been filled.
	# exemple:
	# dict_hps = mds.hps_dict(hps, selected_hp, df_listed, mylevel = radio_button.value)
	import pandas as pd
	import numpy as np

	level_values = df_listed[mylevel].unique()
	l_mds = []
	dict_hps = {} 
	# len(selected_hp)
	for i in range(len(selected_hp)):
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
					print(" /!\ '" + a_field + "' listed in the mds dataframe is a level1 or level2 value, but is not a field listed in the database")
				a_value = None
			if a_value is not None:
				# row_num = df_res[df_res['field'] == df_field].index.tolist()
				df_res.at[j, 'recorded'] = df_res.loc[j]['recorded'] + 1
		l_mds.append(df_res)
		dict_hps[a_hp] = df_res
	return(dict_hps)

def hp_filter_dataframe(hps, selected_hp, selected_value):
	"""
	Filter a dataframe giving a selected value coming from a radio button

	:param hps: HPs in a dict shape (GeoJSON)
	:param selected_hp: a list of HPs IDs
	:param selected_value: value returned by the on_radio_button_change() function, it is a GS ID

	:return: Dataframe of existing HP is a given GS
	"""
	# nonlocal selected_hp_gs
	# global selected_hp_gs
	hps_to_keep = list()
	hps_gs = dict()
	hps_gs['features'] = []
	for i in range(len(selected_hp)):
		gs_current = hps['features'][i]['properties']['Grid ID']
		if gs_current == selected_value:
		# if gs_current ==  radio_button_1.value:
			hps_to_keep.append(i)
		feat = [hps['features'][i] for i in hps_to_keep]
	for i in range(len(feat)):
		hps_gs['features'].append(feat[i])
	selected_hp_gs = []
	for i in range(len(hps_gs['features'])):
		selected_hp_gs.append(hps_gs['features'][i]['properties']['EAMENA ID'])
	return(selected_hp_gs)

def filter_hp_by_gs(hps, selected_hp):

	# NB: doesnot work when imported into Jupyter NB, so refer to the function in the Jupyter NB

	"""
	Filter a dataframe giving a selected value coming from a radio button

	List all GS listed in the HP. Display a radio button to show these HP by GS. Display a radio button for the selection of the GS

	:param hps: HPs in a dict shape (GeoJSON)
	:param selected_hp: a list of HPs IDs

	:return: Update a copy of the HP list filtered on a given GS

	:Example: 
	>> filter_hp_by_gs(hps, selected_hp) # shows the button
	>> filtered_hp_gs # print the list
	"""
	# global filtered_hp_gs
	l_GridIDs = []
	for i in range(len(selected_hp)):
		l_GridIDs.append(hps['features'][i]['properties']['Grid ID'])
	l_GridIDs = list(set(l_GridIDs))
	l_GridIDs.sort()
	radio_button_1 = widgets.RadioButtons(
		options=l_GridIDs,
		description='Select a Grid Square:'
	)
	output = widgets.Output()

	def on_radio_button_change(change):
		selected_value = change.new
		global filtered_hp_gs
		with output:
			output.clear_output()
			filtered_hp_gs = hp_filter_dataframe(hps, selected_hp, selected_value)
			# Print or display the result
			print(filtered_hp_gs, end="")

	radio_button_1.observe(on_radio_button_change, names='value')
	# in Colab only, no return
	display(radio_button_1, output)

def hp_subset_by_gs(hps, filtered_hp_gs):
	"""
	Select the HP from the original GeoJSON/dict file after that the user has selected some GS 

	:param hps: HPs in a dict shape (GeoJSON). This is the original file
	:param filtered_hp_gs: a list of HPs IDs filtered on GS

	:return: GeoJSON/dict with only HP belonging to selected GS
	"""
	selected_hp_gs = {}
	l_new = []
	for i in range(len(hps['features'])):
	# selected_hp.append(hps['features'][i]['properties']['EAMENA ID'])
		for key, value in hps['features'][i]['properties'].items():
			# print(key)
			# print(value)
			if key == 'EAMENA ID' and value in filtered_hp_gs:
				filtered_foo = {}
				filtered_foo['geometry'] = hps['features'][i]['geometry']
				filtered_foo['properties'] = hps['features'][i]['properties']
				l_new.append(filtered_foo)
	# recreate the structure of the original dataset
	selected_hp_gs['features'] = l_new
	# l_new[0]
	# len(selected_hp_gs['features'])
	return(selected_hp_gs)

def hp_plot_spidergraphs(dict_hps=None, df_mds=None, mylevel="level3", ncol=3, verbose=False):
	# show a spidergraph of MDS for a dictionary of HP
	# a par here is only for Colab?
	# exemple:
	# dict_hps = mds.hps_dict(hps, selected_hp, df_listed, mylevel = radio_button.value)
	# mds.plot_spidergraphs(dict_hps, df_mds, mylevel = radio_button.value)
	#
	# ncol = 3
	import math
	import plotly.graph_objects as go
	from plotly.subplots import make_subplots

	nrow = math.ceil(len(dict_hps.keys()) / ncol)
	fig = make_subplots(rows=nrow, cols=ncol, specs=[[{'type': 'polar'}] * ncol] * nrow, subplot_titles=tuple(dict_hps.keys()))
	df_mds_1 = df_mds.copy()  # to add +1 later
	df_mds_1.loc[df_mds_1['value'] == 0, 'value'] = -1
	current_column, current_row = 1, 1
	for a_hp in dict_hps.keys():
		df = dict_hps[a_hp]
		if verbose:
			print(a_hp)
			print(str(current_row) + " " + str(current_column))
		if mylevel == 'level3':
			# mds
			fig.add_trace(go.Scatterpolar(
				name="  mds",
				r=df_mds_1['value'],
				theta=df_mds_1['field'],
				fill='toself',
				fillcolor='red',
				line_color='red',
				hovertemplate="<br>".join([
					"value: %{r}",
					"field: %{theta}"]),
				showlegend=False),
				current_row, current_column)
			fig.add_trace(go.Scatterpolar(
				r=df_mds_1['value'],
				theta=df_mds_1['field'],
				mode='markers',
				marker_color="red",
				hovertemplate="<br>".join([
					"value: %{r}",
					"field: %{theta}"]),
				name='Markers',  # Provide a name for the marker trace
				showlegend=False,  # Show the legend for the marker trace
			), current_row, current_column)
			fig.add_trace(go.Scatterpolar(
				name=a_hp,
				r=df['recorded'],
				theta=df['field'],
				mode='markers',
				marker_color="blue",
				hovertemplate="<br>".join([
					"value: %{r}",
					"field: %{theta}"])
			),
				current_row, current_column)
		else:
			fig.add_trace(go.Scatterpolar(
				name=a_hp,
				r=df['recorded'],
				theta=df['field'],
				mode='markers',
				marker_color="blue",
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

	# Update polar settings for all subplots
	fig.update_polars(
		radialaxis=dict(
			# showline=False,
			range=[-1, 1],  # Set the range for the radial axis
			tickvals=[0, 1],  # Specify the tick values
			ticktext=['0', '1'],  # Specify the corresponding labels
		),
		angularaxis=dict(
			showline=False,  # Set to False to hide the angular axis line
			showticklabels=False,  # Set to False to hide the angular axis labels
		)
	)
	fig.update_layout(
	  autosize=False,
	  width=(ncol*500),
	  height=(nrow*300),
	)
	fig.show()

def hp_concepts_cases_img(hp_cases_path = 'https://raw.githubusercontent.com/eamena-project/eamena-data/main/reference_data/concepts/hp/cases/'):
	"""
	Photos of iconic cases of threats types (agricole, vandalsim, etc.)

	:param hp_cases_path: the root of the hp cases' path

	:return: Dataframe of cases, with UUID, image paths, etc.

	:Example:
	>> hp_concepts_cases_img()
	"""
	import pandas as pd

	hp_cases_path_img = hp_cases_path + "img/"
	hp_cases_path_list = hp_cases_path + "list.tsv"
	df_list = pd.read_csv(hp_cases_path_list, sep='\t')
	df_list['image_path'] = hp_cases_path_img + df_list['image']
	return(df_list)