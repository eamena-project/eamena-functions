# bunch of functions to manage business data

def filter_business_data(input_file_path = "C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_BU_Append_Aug24_v5_rvTH.csv", uuid = 'ResourceID', r2r_fields = ['Assessment Investigator - Actor', 'Information Resource Used'], r2r_map_po = "C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/mapping_pers.csv", r2r_map_ir = "C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/mapping_ir.csv", verbose=True):
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
	# rbu append
	if verbose:
			print("BU append: ")
	df_bu_append = df_unfiltered.drop(columns=r2r_fields)
	# will create a dictionary with as many df that there's duplicates ResourceID (it seems there's an issue with Cultural Periods in a BU append when the latter has duplicated ResourceID)
	max_duplicates = df_bu_append['ResourceID'].value_counts().max()
	dfs_bu_append = []
	for i in range(max_duplicates):
			# Take one of each duplicate at each iteration and drop them from the DataFrame
			df_temp = df_bu_append.drop_duplicates(subset='ResourceID', keep='first')
			dfs_bu_append.append(df_temp)
			# Drop the used entries for the next iteration
			df_bu_append = df_bu_append.drop(df_temp.index)
	if verbose:
		print("  done")
	# TODO trim lead/trail spaces
	# r2r
	if verbose:
				print("Resource to Resource: ")
	r2r_fields.insert(0, uuid) # the first column, UUID, has to be removed
	df_filtered_r2r = df_unfiltered[r2r_fields]
	if 'Assessment Investigator - Actor' in df_filtered_r2r.columns:
		if verbose:
				print("  - 'Assessment Investigator - Actor'")
		# rm empty row
		df_filtered_r2r_po = df_filtered_r2r.dropna(subset=['Assessment Investigator - Actor']) # useful?
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
		if verbose:
			print("  done")
	if 'Information Resource Used' in df_filtered_r2r.columns:
		if verbose:
			print("  - 'Information Resource Used'")
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
		if verbose:
			print("  done")

	return dfs_bu_append, df_r2r_po, df_r2r_ir

# dfs_bu_append, df_r2r_po, df_r2r_ir = filter_business_data(input_file_path = "C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_BU_Append_Aug24_v5 (1).csv")
# # df_bu_append.to_csv("C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_bu_append_new.csv", index=False)
# df_r2r_po.to_csv("C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_data_append_r2r_po_1.csv", index=False)
# df_r2r_ir.to_csv("C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_data_append_r2r_ir_1.csv", index=False)

# for i, df_bu_append in enumerate(dfs_bu_append, 1):
# 		# print(f"DataFrame {i}:\n{df_bu_append.head(3)}\n")
# 		name_out = f"C:/Rprojects/eamena-arches-dev/dbs/database.eamena/data/bulk_data/db_data/Fazzan_data_append_bu_{i}.csv"
# 		df_bu_append.to_csv(name_out, index=False)


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

#%%

# import pandas as pd
# from io import StringIO

# # Use StringIO to simulate reading from a file
# # df = pd.read_csv(StringIO(data))

# # Dictionary to hold the dataframes
# dfs = {}

# # Split the dataframe based on 'ResourceID'
# for idx, group in df_bu_append.groupby('ResourceID'):
# 		dfs[idx] = group

# Now `dfs` dictionary contains separate dataframes for each unique 'ResourceID'
# You can access each dataframe using its 'ResourceID' as the key, like dfs['59e0f074-cbdc-4c7a-8c06-c791b6d898b3']
#%%

# df_bu_append['ResourceID'].value_counts().max()

# data = """
# ResourceID,Investigator Role Type
# 59e0f074-cbdc-4c7a-8c06-c791b6d898b3,EAMENA Project Staff
# 59e0f074-cbdc-4c7a-8c06-c791b6d898b3,Academic Researcher
# 59e0f074-cbdc-4c7a-8c06-c791b6d898b3,Site Manager
# 12345678-cbdc-4c7a-8c06-c791b6d898b3,Field Technician
# 12345678-cbdc-4c7a-8c06-c791b6d898b3,Site Manager
# 38e0f999-cbdc-4c7a-8c06-c791b6d898b3,EAMENA Project Staff
# """

# # Read data into DataFrame
# df = pd.read_csv(StringIO(data))

# # Find out how many duplicates at most for a single ResourceID
# max_duplicates = df_bu_append['ResourceID'].value_counts().max()

# # Create empty list to store the DataFrames
# dfs = []

# # Create DataFrames such that no ResourceID is duplicated within each DataFrame
# for i in range(max_duplicates):
# 		# Take one of each duplicate at each iteration and drop them from the DataFrame
# 		df_temp = df_bu_append.drop_duplicates(subset='ResourceID', keep='first')
# 		dfs.append(df_temp)
# 		# Drop the used entries for the next iteration
# 		df_bu_append = df_bu_append.drop(df_temp.index)

# # You now have DataFrames in the list `dfs` where each DataFrame has unique 'ResourceID' values
# # Print the DataFrames to verify
# for i, df in enumerate(dfs, 1):
# 		print(f"DataFrame {i}:\n{df}\n")

#%%
def hp_list(hps = None):
	"""
	Store the EAMENA ID in a list 

	:param hps: a dict() coming from reading of a JSON (GeoJSON). See the function `dbs_query()`

	:return: A list of EAMENA IDs

	:Example: 
	>> GEOJSON_URL = "https://database.eamena.org/api/search/..."
	>> hps = mds.dbs_query(GEOJSON_URL)
	>> selected_hp = mds.hps_list(hps)

	"""
	selected_hp = []
	for i in range(len(hps['features'])):
		selected_hp.append(hps['features'][i]['properties']['EAMENA ID'])
	return(selected_hp)

def dbs_query(geojson_url = None, to_df = False, verbose = True):
	"""
	Return a JSON file (GeoJSON) from a GeoJSON URL

	Use the Arches REST API with a GeoJSON URL (in Arches: Export > GeoJSON URL) to collect selected Heritage Places in a GeoJSON format

	:param GEOJSON_URL: The GeoJSON URL
	:param to_df: If True, will export as a dataframe

	:Example: 
	>> hps = dbs_query(geojson_url = "https://database.eamena.org/api/search/export_results?paging...")
	>> hps['features'][0]
	"""
	import requests
	import pandas as pd

	resp = requests.get(geojson_url)
	print(resp.status_code) # 504 error on large datasets (> 1,000)
	res = resp.json()
	if(not to_df):
		if verbose:
			print(f"Export as a dictionnary")
		return(res)
	if(to_df):
		if verbose:
			print(f"Export as a dataframe")
		# Assuming geojson_dict is your GeoJSON-like dictionary
		df = pd.json_normalize(res['features'])
		df[['longitude', 'latitude']] = pd.DataFrame(df['geometry.coordinates'].tolist(), index=df.index)
		df.drop('geometry.coordinates', axis=1, inplace=True)
		return(df)

def dbs_export_geojson(geojson_data, output_file_path = "output.geojson"):
	# Save the GeoJSON data to a file
	import json

	with open(output_file_path, "w") as output_file:
		json.dump(geojson_data, output_file, indent=2)

#%%

def gs_with_0_hp(gkey="C:/Rprojects/eamena-arches-dev/credentials/gsheet-407918-65ebbb9cb656.json", verbose=True):
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

#%%

def hp_by_gs_nb(nb_hp_gs='C:/Users/Thomas Huet/Desktop/temp/nb_hp_by_grids.geojson', gs_with_0_hp='C:/Users/Thomas Huet/Desktop/temp/gs_with_0_hp.csv',  verbose=True):
	"""
	Merge the counts of nb of HP by GS recorded in the EAMENA database (first argument) and the list of GS having 0 HP (second argument). The former is calculated with the eamenaR function ref_hps(), the latter is calculated with the function gs_with_0_hp()

	:param nb_hp_gs: A GeoJSON file
	:param verbose: A CSV
	:param verbose: verbose

	:return: Return a GeoJSON file

	:Example:   

	>>> updated_geo_df = hp_by_gs_nb()
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

updated_geo_df = hp_by_gs_nb(nb_hp_gs='C:/Rprojects/eamena-data/working_data/hp_by_gs_nb/year_2024/nb_hp_by_grids.geojson', gs_with_0_hp='C:/Rprojects/eamena-data/working_data/hp_by_gs_nb/year_2024/gs_with_0_hp.csv',  verbose=True)
updated_geo_df.to_file('C:/Rprojects/eamena-data/working_data/hp_by_gs_nb/year_2024/nb_hp_by_grids_including_0_hp.geojson', driver='GeoJSON')
#%%

def gs_merge_info(geometries = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/data/grids/EAMENA_Grid.geojson", uuids = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/data/grids/data-1688403740400-1.csv"):
	"""
	Work on grids

	:param geometries: geometries of grids
	:param uuids: list of grids UUIDs 
	
	"""
	pass


def spat_geojson_to_wkt(geojson = None):
	"""
	Convert a GeoJSON coordinates into WKT for a bulk upload (BU)

	
	"""
	# Check if the GeoJSON type is 'Point'
	if geojson['type'] == 'Point':
		# Extract the coordinates and convert them to WKT format
		coordinates = geojson['coordinates']
		wkt = f"POINT ({coordinates[0]} {coordinates[1]})"
		return wkt
	else:
		raise ValueError("The provided GeoJSON type is not a Point.")

def ir_bu_from_hp(geojson_url = "https://database.eamena.org/api/search/export_results?paging-filter=1&tiles=true&format=geojson&reportlink=false&precision=6&total=91&term-filter=%5B%7B%22inverted%22%3Afalse%2C%22type%22%3A%22string%22%2C%22context%22%3A%22%22%2C%22context_label%22%3A%22%22%2C%22id%22%3A%22QRF0%22%2C%22text%22%3A%22QRF0%22%2C%22value%22%3A%22QRF0%22%7D%5D&language=*&resource-type-filter=%5B%7B%22graphid%22%3A%2234cfe98e-c2c0-11ea-9026-02e7594ce0a0%22%2C%22name%22%3A%22Heritage%20Place%22%2C%22inverted%22%3Afalse%7D%5D"
):
	"""
	Creates an Information Resource (IR) bulk upload (BU) from a GeoJSON URL of Heritage Places (HP) grabing different information from the latter (name, geometry) and adding them into a dataframe. Creates a BU for Information Resources, grabbing the exact coordinates of the HP (IR and HP will ovelap), adding the HP COD identifier into the field 'Catalogue ID' of the IR, and filling IR with other constant data (Country, Grid ID, etc.)

	:param geojson_url: A GeoJSON URL coming from the database

	>>> # GeoJSON URL of the 91 HP of the COD project
	>>> df = create_ir_bu_from_hp()
	>>> df.to_csv("C:/Rprojects/eamena-arches-dev/projects/cod/business_data/bu_ir_cod.csv", index=False)
	
	"""
	import uuid
	import requests
	import pandas as pd
	import re

	resp = requests.get(geojson_url)
	data = resp.json()
	# l_geom_place_exp, l_country_type, l_grid_id, l_ir_type = [],[],[],[]
	pattern = r"(COD-\d+)"
	l_reference_id = []
	l_cod_number = []
	l_geom_place_exp = []
	# for i in data['features'][0]['properties'].keys():
	for i in range(len(data['features'])):
		# Reference ID (random UUID)
		random_uuid = uuid.uuid4()
		l_reference_id.append(random_uuid)
		# COD number
		name = data['features'][i]['properties']['Resource Name']
		cod_number = re.search(pattern, name)
		l_cod_number.append(cod_number.group(1))
		# Geometric Place Expression
		geom_place_exp = spat_geojson_to_wkt(data['features'][i]['geometry'])
		l_geom_place_exp.append(geom_place_exp)
	df = pd.DataFrame(
	{'ResourceID': l_reference_id,
	'Catalogue ID': l_cod_number,
	'Geometric Place Expression': l_geom_place_exp,
	'Country Type': ['Egypt'] * len(l_geom_place_exp), 
	# 'Grid ID': ['E31N30-12'] * len(l_geom_place_exp), # It should go into the related resources append
	'Information Resource Type': ['Photograph'] * len(l_geom_place_exp), #l_ir_type
	})
	return df


def ir_add_metadata_XY_to_photo_exif(dirIn_photos = "c:/Rprojects/eamena-arches-dev/projects/cmha/db_data/Wadi Naqqat", hps = "c:/Rprojects/eamena-arches-dev/projects/cmha/data/wadi_naqqat_new_ok.geojson", exiftool_path = "c:/exiftool-13.03_64/exiftool.exe", dirOut_photos = None):
	"""
	Append coordinates to the EXIF metdata of the photograph using exiftools.exe. 

	:param dirIn_photos: path to the input folder. All subfolder will be parsed and their name matched against the names of hertiage places in the `hps` file. For example: folder WN01 in `dirIn_photos` will match the string WN01 in the 'Resource Name' field of hps
	:param hps: A GeoJSON file of HP to grab the coordinates from. 
	:param exiftool_path: path to the exiftool EXE

	>>> ir_add_metadata_XY_to_photo_exif()

	"""
	import os
	from pathlib import Path
	import geopandas as gpd
	import subprocess

	gdf = gpd.read_file(hps)
	directories = [d for d in os.listdir(dirIn_photos) if os.path.isdir(os.path.join(dirIn_photos, d))]

	for a_dir in directories:
		mydir = dirIn_photos + "/" + a_dir
		print(f"read {a_dir}")
		# coordinates of this specific HP
		filtered_gdf = gdf[gdf['Resource Name'].str.contains(a_dir, na=False)]
		coords = [(point.x, point.y) for point in filtered_gdf.geometry]
		gps_latitude = coords[0][1]
		gps_longitude = coords[0][0]
		# create the output dir
		if dirOut_photos is not None:
			path = Path(dirIn_photos) 
			dirRoot = path.parent.absolute()
			print(f"will export the updated photo into: {dirRoot} ")
			# dirOut = dirRoot + "db_data/" + a_dir + "_out"
			dirOut = dirRoot + "db_data/" + a_dir + "_out"
			if not os.path.exists(dirOut):	
				os.makedirs(dirOut)
		# photos
		list_photos = os.listdir(mydir)
		for a_photo in list_photos:
			image_path = mydir + "/" + a_photo
			if dirOut_photos is not None:
				new_image_path = dirOut + "/" + a_photo
			print(f"    - image: {a_photo}")
			command = [
				exiftool_path,
				'-gpslatitude=' + str(gps_latitude),
				'-gpslongitude=' + str(gps_longitude),
				'-overwrite_original',
				image_path
			]
			# command = f"& {exiftool_path} -gpslatitude='{gps_latitude}' -gpslongitude='{gps_longitude}' -overwrite_original '{image_path}'"
			# print(command)
			result = subprocess.run(command, text=True, capture_output=True)
			# Print the output and any error
			print("Output:", result.stdout)
			print("Error:", result.stderr)


def spat_convert_to_degrees(value):
	""" 
	Convert decimal degree to degrees, minutes, seconds tuple, formatted for EXIF. 
	"""
	degrees = int(value)
	minutes = int((value - degrees) * 60)
	seconds = (value - degrees - minutes / 60) * 3600
	degrees = (degrees, 1)
	minutes = (minutes, 1)
	seconds = (int(seconds * 100), 100)  # More accurate second representation as rational
	return degrees, minutes, seconds
	# """Convert decimal degrees to EXIF-compatible format."""
	# from fractions import Fraction
	# degrees = int(value)
	# minutes = int((value - degrees) * 60)
	# seconds = (value - degrees - minutes / 60) * 3600
	# return (Fraction(degrees, 1), Fraction(minutes, 1), Fraction(int(seconds * 100), 100))



def ir_add_metadata_XY_to_photo(image_path, new_image_path, latitude, longitude):
	# TODO: adapt to the dataset structure: find the decimal coordinates in the `records` table
	"""
	
	Append coordinates to the EXIF metdata of the photograph. However adding XY (GPS) coordinates will remove previous IPTC metdata.

	:param image_path: path to the input image (without GPS coordinates) 
	:param new_image_path: path to the output image (with GPS coordinates) 
	:param latitude: latitude in decimal
	:param longitude: longitude in decimal

	>>> image_path = "C:/Rprojects/eamena-arches-dev/projects/cod/www/4171_sl_JDs.jpg"
	>>> new_image_path = 'C:/Rprojects/eamena-arches-dev/projects/cod/www/4171_sl_JDs_with_coords.jpg'
	>>> add_metadata_XY_to_photo(image_path, new_image_path, latitude = 48.848270462241814, longitude = 2.41120456097722) # loc: Paris
	
	"""
	from PIL import Image
	import piexif

	# image_path = 'path/to/your/image.jpg'
	img = Image.open(image_path)
	exif_dict = piexif.load(img.info['exif']) if 'exif' in img.info else {}
	gps_latitude = spat_convert_to_degrees(latitude)
	gps_longitude = spat_convert_to_degrees(abs(longitude))  # Longitude should be positive for EXIF
	# GPS data according to EXIF spec
	gps_ifd = {
		piexif.GPSIFD.GPSLatitudeRef: 'N' if latitude >= 0 else 'S',
		piexif.GPSIFD.GPSLatitude: gps_latitude,
		piexif.GPSIFD.GPSLongitudeRef: 'E' if longitude >= 0 else 'W',
		piexif.GPSIFD.GPSLongitude: gps_longitude,
	}
	exif_dict['GPS'] = gps_ifd
	exif_bytes = piexif.dump(exif_dict)
	# new_image_path = 'path/to/your/new_image.jpg'
	img.save(new_image_path, "jpeg", exif=exif_bytes)
	print("Image + coordinates saved")


def ir_add_metadata_to_photo(root_path = "C:/Rprojects/eamena-arches-dev/projects/cod/", photos_in = "db_data/photos_in", photo_metadata = "business_data/xlsx/photos_NS.xlsx", records_in = "business_data/xlsx/records_NS.xlsx", photo_out = "db_data/photos_out", exif_metadata=False, xmp_metadata=False, iptc_metadata=False, gps_metadata=False, verbose = True):
	"""
	Append metadata into the photograph by reading other XLSX tables

	:param root_path: Root path of the project 
	:param photos_in: Path to the folder where the photographs are stored
	:param photo_metadata: Path to the file describing the photographs
	:param records_in: Path to the file of the records (aka HP), useful to collect data 
	:param photo_out: Path to the folder where the photographs with metdata will be stored
	:param xmp_metadata: Add XMP metadata if True
	
	>>> # add_metadata_to_photo(gps_metadata=True)
	>>> # add_metadata_to_photo(gps_metadata=True, exif_metadata=True)
	>>> photo_missed = ir_add_metadata_to_photo(gps_metadata=True, iptc_metadata=True, verbose=False)
	>>> print("\n- [ ] ".join(photo_missed))

	"""
	import re
	from PIL import Image
	# from PIL import IptcImagePlugin
	from iptcinfo3 import IPTCInfo
	import piexif
	# from libxmp import XMPFiles, consts
	import subprocess
	import os
	import pandas as pd
	import logging

	# avoid the message 'Marker scan hit start of image data' to be printed
	logging.getLogger("iptcinfo").setLevel(logging.ERROR)

	photo_missed = []
	# db_path = root_path + "business_data/xlsx/records_NS.xlsx"
	record_db_path = root_path + records_in
	df_rec_metadata = pd.read_excel(record_db_path)
	# photographs metadata
	photo_db_path = root_path + photo_metadata
	df_im_metadata = pd.read_excel(photo_db_path)
	# repacement to match the photo/folder labels
	df_im_metadata['filename'] = df_im_metadata['filename'].apply(lambda x: re.sub(r'.*?(DSC|IMG)', r'\1', x))
	# list the records = units from the metadata file
	units = list(df_im_metadata['unitnumber'].unique())
	photo_im_path_in = root_path + photos_in
	photo_im_path_out = root_path + photo_out
	# create a mapping table
	split_on = "s_" # all folder names are like: 88s_Ibrahim Mahmud/
	unitnumbers = [item.split(split_on)[0] for item in os.listdir(photo_im_path_in)]
	df_im_map = pd.DataFrame(
							{'unitnumber': unitnumbers, 
							'directory': os.listdir(photo_im_path_in)}
							)
	# loop over the units, match units and folders with photographs
	stop_nb = 0
	# units.reverse()
	# for unit in units[63:]:
	for unit in [65]:
		stop_nb += 1
		if stop_nb > 1:
			print("... Early stop - Done ...")
			return photo_missed
		print(f"*** read unit/record/heritage '{unit}' ***")
		# add 0 or 00 before to get the COD number
		if unit < 10:
			unit_t = "0" + str(unit)
		# elif unit > 9:
		# 	unit_t = "00" + str(unit)
		else:
			unit_t = str(unit)
		selected_unit = df_im_map[df_im_map['unitnumber'] == unit_t]
		if verbose:
			print(f"- directory: \n{selected_unit.to_markdown(index=False)}")
		unit_folder = selected_unit.iloc[0,1]
		photos = os.listdir(photo_im_path_in + '\\' + unit_folder)
		# print(photos)
		if verbose:
			print(f"- photos: \n{photos}")
			print("\n")
		# loop over photo, add metadata, save
		for a_photo in range(len(photos)):
			a_photo_OK = re.sub(r'.*?(DSC|IMG)', r'\1', photos[a_photo])
			# a_photo_OK = str(photos[a_photo])
			if verbose:
				print(f"  + read photo: {photos[a_photo]} (ie {a_photo_OK})")
			# a_photo_metadata = df_im_metadata[df_im_metadata['picture'].str.lower() == a_photo_OK.lower()]
			a_photo_metadata = df_im_metadata[df_im_metadata['filename'].str.lower() == a_photo_OK.lower()]
			# a_photo_metadata = re.sub(r'.*?(DSC|IMG)', r'\1', df_im_metadata[df_im_metadata['picture'].str.lower() == a_photo_OK.lower()]
			if len(a_photo_metadata) > 0:
				if verbose:
					print(f"    = photo metadata:")
					print(a_photo_metadata.to_markdown(index=False))
					print("\n")
				cur_folder = selected_unit['directory'].iloc[0]
				photo_path_in = photo_im_path_in + "\\" + cur_folder + "\\" + photos[a_photo]
				photo_path_out = photo_im_path_out + "\\" + cur_folder + "\\" + photos[a_photo]
				# extract metadata from the table
				im_descr = a_photo_metadata['description'].iloc[0]
				im_artis = a_photo_metadata['takenby'].iloc[0]
				im_date = a_photo_metadata['datetaken'].iloc[0]
				# match the row/record/heritage place
				im_record_id = df_rec_metadata[df_rec_metadata['ID'] == unit]["ID"].iloc[0]
				im_record_attribution = df_rec_metadata[df_rec_metadata['ID'] == unit]["attribution"].iloc[0]
				# im_title = df_rec_metadata['ID'].iloc[0]
				if im_record_id < 10:
					im_record_id_t = "00" + str(im_record_id)
				if im_record_id < 100 and im_record_id > 9:
					im_record_id_t = "0" + str(im_record_id)
				im_title = im_record_attribution + " (COD-" + str(im_record_id_t) + ")"
				im_caption = im_title + ". " + im_descr
				im_coord_N = df_rec_metadata[df_rec_metadata['ID'] == unit]["coordinateN"].iloc[0]
				im_coord_E = df_rec_metadata[df_rec_metadata['ID'] == unit]["coordinateE"].iloc[0]
				im_copyright = "Copyright, Archinos architecture, 2024. All rights reserved."
				im_country = "Egypt"
				if verbose:
					print('       im_descr: ' + im_descr)
					print('       im_artis: ' + im_artis)
					print('       im_title: ' + im_title)
					print('       im_caption: ' + im_caption)
					print('       im_date: ' + im_date)
					print('       im_copyright: ' + im_copyright)
					print('       im_coord_N: ' + str(im_coord_N))
					print('       im_coord_E: ' + str(im_coord_E))
				if verbose:
					print(f"    = write metadata")
					# photo_path_in =  photo_path_out
				# prevent to rm former EXIF metadata
				# create dic
				# Load the image
				img = Image.open(photo_path_in)
				size_img_in = os.path.getsize(photo_path_in)
				size_img_in_MB = round(size_img_in/1000000, 1)
				# test previous metadata
				try:
					exif_dict = piexif.load(img.info['exif'])
				except KeyError:
					if verbose:
						print(f" -- Key Error: new exif_dict is created ")
					exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'Interop': {}, 'thumbnail': None}
				# test if thumbnail has a JPG start
				thumbnail = exif_dict.get("thumbnail")
				if thumbnail == b'':
					print(f"      {photos[a_photo]}'s thumbnail is not in JPEG format or is corrupted, will be recreated")
					exif_dict.pop("thumbnail", None) 
					exif_dict['thumbnail'] = None
				# write
				if exif_metadata:
					if verbose:
						print(f"EXIF metadata (without GPS)---")
					exif_dict['0th'][piexif.ImageIFD.ImageDescription] = im_caption.encode('utf-8')
					exif_dict['0th'][piexif.ImageIFD.Artist] = im_artis.encode('utf-8')
					exif_dict['0th'][piexif.ImageIFD.XPTitle] = im_title.encode('utf-8')
					exif_dict['0th'][piexif.ImageIFD.XPComment] = im_caption.encode('utf-8')
					exif_dict['0th'][piexif.ImageIFD.XPAuthor] = im_artis.encode('utf-8')
					exif_dict['0th'][piexif.ImageIFD.DateTime] = im_date.encode('utf-8')
					exif_dict['0th'][piexif.ImageIFD.Copyright] = im_copyright.encode('utf-8')
					# exif_dict['Exif'][piexif.ImageIFD.Artist] = im_artis.encode('utf-8')
					# exif_dict['Exif'][piexif.ImageIFD.ImageDescription] = im_caption.encode('utf-8')
					# exif_dict['0th'][piexif.ImageIFD.GPSDestCountry] = im_country.encode('utf-8')
					# add_metadata_XY_to_photo(image_path, new_image_path, latitude = im_coord_N, longitude = im_coord_E) # loc: Paris
					# exif_dict['0th'][piexif.IptcIFD.Artist] = im_artis.encode('utf-8')
				if gps_metadata:
					if verbose:
						print(f"GPS metadata ---")
					gps_latitude = spat_convert_to_degrees(im_coord_N)
					gps_longitude = spat_convert_to_degrees(abs(im_coord_E))  # Longitude should be positive for EXIF
					# GPS data according to EXIF spec
					gps_ifd = {
						piexif.GPSIFD.GPSLatitudeRef: 'N' if im_coord_N >= 0 else 'S',
						piexif.GPSIFD.GPSLatitude: gps_latitude,
						piexif.GPSIFD.GPSLongitudeRef: 'E' if im_coord_E >= 0 else 'W',
						piexif.GPSIFD.GPSLongitude: gps_longitude,
					}
					exif_dict['GPS'] = gps_ifd
				# print(exif_dict.keys())
				exif_bytes = piexif.dump(exif_dict)
				# overwrite
				# TODO: save with the highest resolution (if not, 1 MB -> 500 KB)
				original_dpi = img.info.get('dpi')
				out_folder = photo_im_path_out + "\\" + cur_folder
				if not os.path.exists(out_folder):
					os.makedirs(out_folder)
				img.save(photo_path_out, exif=exif_bytes, quality=95, dpi=original_dpi, optimize=True, progressive=True)
				if verbose:
					print(f"    => {photos[a_photo]} has been saved with EXIF metadata")
				img.close()
				size_img_out = os.path.getsize(photo_path_out)
				size_img_out_MB = round(size_img_out/1000000, 1)
				if verbose:
					print(f"    image size (MB): {size_img_in_MB} => {size_img_out_MB}")
				if xmp_metadata:
					if verbose:
						print(f"XMP metadata ---")
					# XMP Handling with exiftool
					xmp_data = {
						"XMP-dc:Title": "Your Title Here",
						"XMP-dc:Description": "A brief description here."
					}
					# Convert XMP data to exiftool command arguments
					xmp_args = []
					for tag, value in xmp_data.items():
						xmp_args.extend(['-' + tag + '=' + value])
					print(photo_path_out)
					cmd_exiftool = ['exiftool'] + xmp_args + ['-overwrite_original', photo_path_out]
					cmd_exiftool = f'C:\exiftool\exiftool {xmp_args} -overwrite_original "{photo_path_out}"'
					print(cmd_exiftool)
					# print("HERE")
					# subprocess.run(r"cd C:/exiftool && dir", shell=True)
					# subprocess.run("cd pwd", shell=True)

					# subprocess.run(cmd_exiftool)

					if verbose:
						print(f"    => {photos[a_photo]} has been saved with XMP metadata")
				if iptc_metadata:
					if verbose:
						# print(photo_path_out)
						print(f"IPTC metadata ---")
					info = IPTCInfo(photo_path_out, force=True)
					info['caption/abstract'] = im_caption.encode('utf-8')
					info['object name'] = im_title.encode('utf-8')
					info['copyright notice'] = im_copyright.encode('utf-8')
					info['credit'] = f'{im_artis} - {im_copyright}'
					# my_artiste = im_artis.encode('utf-8')
					# my_copyright = im_copyright.encode('utf-8')
					# info['credit'] = f'{my_artiste} - {my_copyright}'
					info['country/primary location name'] = "Egypt"
					# exif_dict['0th'][piexif.ImageIFD.Artist] = im_artis.encode('utf-8')
					# exif_dict['0th'][piexif.ImageIFD.XPTitle] = im_title.encode('utf-8')
					# exif_dict['0th'][piexif.ImageIFD.XPComment] = im_caption.encode('utf-8')
					# exif_dict['0th'][piexif.ImageIFD.XPAuthor] = im_artis.encode('utf-8')
					# exif_dict['0th'][piexif.ImageIFD.DateTime] = im_date.encode('utf-8')
					# exif_dict['0th'][piexif.ImageIFD.Copyright] = im_copyright.encode('utf-8')
					info.save_as(photo_path_out)
			else:
				print(f"    /!\ No metadata available for {photos[a_photo]}")
				print(f"        {a_photo_OK} not found in the metadata table {photo_metadata}")
				photo_missed.append(a_photo_OK)
			if not xmp_metadata and not exif_metadata and not gps_metadata:
				if verbose:
						print(f"    CREATE HERE A DF WITH THE IMAGE NAME AS A KEY")
			if verbose:
				print("\n")
			# print(info.keys())
	if verbose:
		print("return the lis of unmatched photos and metdata")
	return photo_missed




# %%



# input_image_path = 'C:\Rprojects\eamena-arches-dev\projects\cod\db_data\photos_in\\02s_MuhTalaatHarb\\aDSC_1607s.JPG'

# import piexif
# from PIL import Image
# import subprocess
# import json

# # Load an image
# img = Image.open(input_image_path)

# # EXIF Handling with piexif
# exif_dict = piexif.load(img.info.get('exif', b''))
# exif_dict['0th'][piexif.ImageIFD.Make] = u'Canon'.encode('utf-8')
# exif_dict['0th'][piexif.ImageIFD.Model] = u'Canon EOS 80D'.encode('utf-8')
# exif_bytes = piexif.dump(exif_dict)

# # Save the image with new EXIF data
# temp_filename = 'C:\Rprojects\eamena-arches-dev\projects\cod\db_data\photos_out\\aDSC_1607s.JPG
# img.save(temp_filename, exif=exif_bytes)

# # XMP Handling with exiftool
# xmp_data = {
#     "XMP-dc:Title": "Your Title Here",
#     "XMP-dc:Description": "A brief description here."
# }

# # Convert XMP data to exiftool command arguments
# xmp_args = []
# for tag, value in xmp_data.items():
#     xmp_args.extend(['-' + tag + '=' + value])

# # Call exiftool to write XMP data
# subprocess.run(['exiftool'] + xmp_args + ['-overwrite_original', temp_filename])

# # Rename temp file if needed
# final_filename = 'final_output_image.jpg'
# subprocess.run(['mv', temp_filename, final_filename])

# print("EXIF and XMP metadata updated successfully.")
