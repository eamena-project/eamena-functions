# bunch of functions to manage business data


def db_query(GEOJSON_URL = None):
	"""
	Return a JSON file (GeoJSON) from a GeoJSON URL

	Use the Arches REST API with a GeoJSON URL (in Arches: Export > GeoJSON URL) to collect selected Heritage Places in a GeoJSON format

	:param GEOJSON_URL: The GeoJSON URL

	:Example: 
	>> GEOJSON_URL = "https://database.eamena.org/api/search/..."
	>> hps = mds.db_query()
	"""
	import requests

	resp = requests.get(GEOJSON_URL)
	print(resp.status_code) # 504 error on large datasets (> 1,000)
	return(resp.json())

def db_export_geojson(geojson_data, output_file_path = "output.geojson"):
	# Save the GeoJSON data to a file
	import json

	with open(output_file_path, "w") as output_file:
		json.dump(geojson_data, output_file, indent=2)

def hp_list(hps = None):
	"""
	Store the EAMENA ID in a list 

	:param hps: a dict() coming from reading of a JSON (GeoJSON). See the function `db_query()`

	:return: A list of EAMENA IDs

	:Example: 
	>> GEOJSON_URL = "https://database.eamena.org/api/search/..."
	>> hps = mds.db_query(GEOJSON_URL)
	>> selected_hp = mds.hps_list(hps)

	"""
	selected_hp = []
	for i in range(len(hps['features'])):
		selected_hp.append(hps['features'][i]['properties']['EAMENA ID'])
	return(selected_hp)

def gs_with_0_hp(gkey="C:/Rprojects/eamena-arches-dev/data/keys/gsheet-407918-65ebbb9cb656.json", verbose=True):
  """
  Grids with 0 Heritage places. Read an XLSX hosted online and its different sheets. This XLSX gathers the names of Grid Squares (GS) that have been surveyed but have no (zero) HPs

  :param gkey: a key in a JSON file for the Google API platform
  :param verbose: verbose

  :return: Return a dataframe

  :Example:   

  >>> gs_0_hp = gs_with_0_hp()
  >>> gs_0_hp.to_csv('C:/Users/Thomas Huet/Desktop/temp/gs_with_0_hp.csv', index=False)
  """
  import pandas as pd
  import gspread

  gc = gspread.service_account(filename=gkey) # Google Client
  spreadsheet = gc.open("EAMENA Final Grid Squares")
  grid_square_values = []

  # Loop over each worksheet in the Google Sheet
  for worksheet in spreadsheet:
      print("Current Sheet:", worksheet.title)
      records = worksheet.get_all_records()
      for record in records:
          if record['Pins in GE'] == 0:
              grid_square_values.append(record['Grid Square'])
  if verbose:
    print("Grid Square values where 'Pins in GE' is 0:", grid_square_values)
  vals = [0] * len(grid_square_values)

  gs_with_0_hp = pd.DataFrame(
    {'nb_hp': vals,
    'gs': grid_square_values
    })
  return gs_with_0_hp

def hp_by_gs_nb(nb_hp_gs='C:/Users/Thomas Huet/Desktop/temp/nb_hp_by_grids.geojson', gs_with_0_hp='C:/Users/Thomas Huet/Desktop/temp/gs_with_0_hp.csv',  verbose=True):
  """
  Merge the counts of nb of HP by GS recorded in the EAMENA database (first ragument) and the list of GS having 0 HP (second argument). The latter is calculated with the function gs_with_0_hp()

  :param nb_hp_gs: A GeoJSON file
  :param verbose: A CSV
  :param verbose: verbose

  :return: Return a GeoJSON file

  :Example:   

  >>> updated_geo_df = nb_hp_by_gs()
  >>> updated_geo_df.to_file('C:/Users/Thomas Huet/Desktop/temp/nb_hp_by_grids_including_0_hp.geojson', driver='GeoJSON')
   
   """
  import pandas as pd
  import geopandas as gpd

  geo_df = gpd.read_file(nb_hp_gs)
  csv_df = pd.read_csv(gs_with_0_hp)
  # Ensure the 'gs' field is the same type in both DataFrames if necessary
  geo_df['gs'] = geo_df['gs'].astype(str)
  csv_df['gs'] = csv_df['gs'].astype(str)

  # Merge the data - left join to keep all records from geo_df
  updated_geo_df = geo_df.merge(csv_df[['gs', 'nb_hp']], on='gs', how='left', suffixes=('', '_updated'))

  # Update 'nb_hp' with the values from 'nb_hp_updated' where available
  updated_geo_df['nb_hp'] = updated_geo_df['nb_hp_updated'].fillna(updated_geo_df['nb_hp'])

  # Drop the temporary column
  updated_geo_df.drop(columns=['nb_hp_updated'], inplace=True)

  return updated_geo_df
  # Save the updated GeoDataFrame as GeoJSON


def gs_merge_info(geometries = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/data/grids/EAMENA_Grid.geojson", uuids = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/data/grids/data-1688403740400-1.csv"):
	"""
	Work on grids

	:param geometries: geometries of grids
	:param uuids: list of grids UUIDs 
	
	"""
	pass