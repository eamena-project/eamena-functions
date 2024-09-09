# bunch of functions to manage business data


#%%
def append_filter_data(input_file_path = "C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_BU_Append_Aug24_v5_rvTH.csv", uuid = 'ResourceID', r2r_fields = ['Assessment Investigator - Actor', 'Information Resource Used'], r2r_map_po = "C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/mapping_pers.csv", r2r_map_ir = "C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/mapping_ir.csv", verbose=True):
  """
  Grab a tabular file having data used to update and append different resources (ex: HP), filter the data that need to be 'pushed' though the BU append procedure, and data that go into the resource 2 resource import. These two procedures (BU append and resource-to-resource) follow different Python processes, respectively 'import_business_data_relations' and 'import_business_data ... -ow append'.

  :param r2r_fields: Resource-to-Resource fields. It is assumed that values form these fields are human-readable values (not UUID), for example the 'Assessment Investigator - Actor' has the value 'Martin Sterry' not his UUID (ecdc771c-ff31-42c7-9ec9-522e6302e6f0). Human-readable values will be match to their UUID using a mapping table. The output of these r2r values will be exported into a CSV file 
  :param uuid: The field having the UUID of the target resource (ie. values will be added to these resources)
  :param r2r_map_po: Path to the Person/Organisation (po) mapping table. The later provides alignment between the human-readable values and their UUID
  :param r2r_map_ir: Path to the Information Resources (ir) mapping table. The later provides alignment between the human-readable values and their UUID

  """
  import pandas as pd
  import numpy as np
    
  df_unfiltered = pd.read_csv(input_file_path)
  r2r_fields.insert(0, uuid)
  # TODO trim lead/trail spaces
  df_filtered_r2r = df_unfiltered[r2r_fields]
  # TODO: all in one loop
  if 'Assessment Investigator - Actor' in df_filtered_r2r.columns:
    if verbose:
         print("Resource to Resource: 'Assessment Investigator - Actor'")
    # rm empty row
    df_filtered_r2r_po = df_filtered_r2r.dropna(subset=['Assessment Investigator - Actor'])
    df_map_r2r_po = pd.read_csv(r2r_map_po)
    df_r2r_po_merged = pd.merge(df_filtered_r2r_po, df_map_r2r_po, on='Assessment Investigator - Actor', how='left')
    nrow = len(df_r2r_po_merged)
    df_r2r_po = pd.DataFrame({
         'resourceinstanceidfrom': df_r2r_po_merged[uuid],
         'resourceinstanceidto': df_r2r_po_merged['uuid_pers'],
         'relationshiptype': np.repeat('http://www.ics.forth.gr/isl/CRMdig/L33_has_maker', nrow),
         'datestarted': np.repeat('', nrow),
         'dateended': np.repeat('', nrow),
         'notes': np.repeat('', nrow)
  })
  if 'Information Resource Used' in df_filtered_r2r.columns:
    if verbose:
         print("Resource to Resource: 'Information Resource Used'")
    # rm empty row
    df_filtered_r2r_ir = df_filtered_r2r.dropna(subset=['Information Resource Used'])
    df_map_r2r_ir = pd.read_csv(r2r_map_ir)
    df_r2r_ir_merged = pd.merge(df_filtered_r2r_ir, df_map_r2r_ir, on='Information Resource Used', how='left')
    nrow = len(df_r2r_ir_merged)
    df_r2r_ir = pd.DataFrame({
         'resourceinstanceidfrom': df_r2r_ir_merged[uuid],
         'resourceinstanceidto': df_r2r_ir_merged['uuid_ir'],
         'relationshiptype': np.repeat('http://www.cidoc-crm.org/cidoc-crm/P129i_is_subject_of', nrow),
         'datestarted': np.repeat('', nrow),
         'dateended': np.repeat('', nrow),
         'notes': np.repeat('', nrow)
  })

  return df_r2r_po, df_r2r_ir

df_r2r_po, df_r2r_ir = append_filter_data()
# df.head()
df_r2r_po.to_csv("C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_r2r_po.csv", index=False)
df_r2r_ir.to_csv("C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_r2r_ir.csv", index=False)

#%%
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