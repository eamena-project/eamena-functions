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

def nb_hp_by_gs(nb_hp_gs='C:/Users/Thomas Huet/Desktop/temp/nb_hp_by_grids.geojson', gs_with_0_hp='C:/Users/Thomas Huet/Desktop/temp/gs_with_0_hp.csv',  verbose=True):
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


def grid_merge_info(geometries = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/data/grids/EAMENA_Grid.geojson", uuids = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/data/grids/data-1688403740400-1.csv"):
	"""
	Work on grids

	:param geometries: geometries of grids
	:param uuids: list of grids UUIDs 
	
	"""
	pass


