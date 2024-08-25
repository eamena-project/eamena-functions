
#%% test

def summed_values(data = None, fieldname = None):
    """
    Creates a dataframe summing the number of occurences for a given field
    
    ::param data: dictionary of Heritage Places (JSON)
    """
    import pandas as pd
    from collections import Counter

    l = list()
    for i in range(len(data['features'])):
        l.append(data['features'][i]['properties'][fieldname])
    split_names = [name.strip() for item in l if item is not None for name in item.split(',')]
    name_counts = Counter(split_names)
    df = pd.DataFrame.from_dict(name_counts, orient='index').reset_index()
    df = df.rename(columns={'index': 'name', 0: 'n_hp'})
    df = df.sort_values('n_hp', ascending=False)
    return df

def zenodo_contributors(data = None, fieldname = "Assessment Investigator - Actor", 
                        contributors_layout_HP = {"name": None, "type": "DataCollector"}, contributors_layout_GS = [{'name': "University of Oxford", "type": "DataManager"},{'name': "University of Southampton", "type": "DataManager"}]):
    """
    Creates dictionary of contributors, filling a dictionary layout (`contributors_layout_*`). Contributors are sorted according to the total number of their name occurences in the selected `fieldname`.
    
    :param data: dictionary of Heritage Places (JSON)
    """
    if fieldname in list(data['features'][0]['properties'].keys()):
    # HPs
        df = summed_values(data, fieldname)
        CONTRIBUTORS = list()
        for name in df['name']:
            contibut = contributors_layout_HP.copy()
            contibut['name'] = name
            # TODO: "affiliation" and "orcid"
            contibut = {key: value for key, value in contibut.items() if value is not None and value != 'null'}
            CONTRIBUTORS.append(contibut)
    else:
    # not HPs (GS, ...)
        CONTRIBUTORS = contributors_layout_GS
    return CONTRIBUTORS

def zenodo_keywords(data = None, constant = ['EAMENA', 'MaREA', 'Cultural Heritage'], additional = None, fields = ["Country Type", "Cultural Period Type"]):
    """
    Creates a list of keywords with a constant basis (`constant`) and parsed supplementary `fields` (for space-time keywords)
    
    :param data: dictionary of Heritage Places (JSON)
    :param additional: additional keyworks provided by the user
    """
    KEYWORDS = list()
    KEYWORDS = KEYWORDS + constant + additional
    if all(elem in list(data['features'][0]['properties'].keys()) for elem in fields):
    # HPs
        for fieldname in fields:
            df = summed_values(data, fieldname)
            KEYWORDS = KEYWORDS + df['name'].tolist()
        try:
            KEYWORDS.remove('Unknown')
        except ValueError:
            pass
    return KEYWORDS

def zenodo_dates(data = None, fields = ["Assessment Activity Date"]):
    """
    Get the min and the max of dates recorded in `fields`    

    :param data: dictionary of Heritage Places (JSON)
    """
    from datetime import datetime

    if all(elem in list(data['features'][0]['properties'].keys()) for elem in fields):
    # HPs
        ldates = list()
        for fieldname in fields:
            df = summed_values(data, fieldname)
            ldates = ldates + df['name'].tolist() 
        if 'None' in ldates:
            ldates.remove('None')
        # ldates.remove('None')
        # date_strings = [x for x in date_strings if x is not 'None']
        date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in ldates]
        min_date = min(date_objects)
        max_date = max(date_objects)
        min_date_str = min_date.strftime('%Y-%m-%d')
        max_date_str = max_date.strftime('%Y-%m-%d')
        DATES = [{'type': 'created', 'start': min_date_str, 'end': max_date_str}]
        return DATES
    else:
    # not HPs (GS, ...)
        DATES = [{'type': 'created', 'start': '2021-01-01', 'end': '2021-01-02'}]
        return DATES

def zenodo_related_identifiers(site = 'https://zenodo.org/oai2d', set = 'user-eamena', metadataPrefix = 'oai_dc', reference_data_list = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/data/lod/zenodo/reference_data_list.tsv"):
    """
    Parse the 'EAMENA database' community in Zenodo ('user-eamena') to check if there are already uploaded datasets. Handle differently the reference data (collections, RMs, ...) and the datasets (Sistan part 1, etc.), or business data. Reference data are 'isDescribedBy' related identifiers, whereas the datasets are 'isContinuedBy' related resources.

    :param reference_data_list: the list of reference data already existing in the 'eamena' Zenodo community. These objects will not be added as 'isContinuedBy' in the metadata key 'related_identifiers' but as 'isDescribedBy'
    """
    import pandas as pd
    from sickle import Sickle

    # reference_data_list = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/data/lod/zenodo/reference_data_list.tsv"
    reference_data = pd.read_csv (reference_data_list, sep = '\t')
    l_isDescribedBy = reference_data['url'].tolist()

    sickle = Sickle(site)
    records = sickle.ListRecords(metadataPrefix=metadataPrefix, set=set)
    # record = records.next()
    # return record.metadata['identifier'][0]# record = records.next()
    l = list()
    for record in records:
        l.append(record.metadata['identifier'][0])
    # rm the reference data
    l_isContinuedBy = [x for x in l if x not in l_isDescribedBy]
    ## create the record
    # business data
    l_isContinuedBy_out = list()
    for busdata in l_isContinuedBy:
        l_isContinuedBy_out.append({'relation': 'isContinuedBy',
                                    'identifier': busdata})
    # reference data
    l_isDescribedBy_out = list()   
    for refdata in l_isDescribedBy:
        l_isDescribedBy_out.append({'relation': 'isDescribedBy',
                                    'identifier': refdata})
    # merge lists
    l_related_identifiers = l_isContinuedBy + l_isDescribedBy_out
    return(l_related_identifiers)

def zenodo_statistics(data = None):
    """
    Calculate basic statistics on HPs. Return a list with: the total number of Heritage Places; the number of Heritage Places layered by number of geometries (some have 1, 2, 3, ...); the total number of geometries; etc.

    :param data: dictionary of Heritage Places (JSON)
    """
    from collections import Counter

    l = list()
    LIST_HPS = list()
    for i in range(len(data['features'])):
        ea_id = data['features'][i]['properties']['EAMENA ID']
        l.append(ea_id)
    my_dict = {i:l.count(i) for i in l}
    value_counts = Counter(my_dict.values())
    HPS_GEOM_NB = dict(value_counts)
    HPS_NB = sum(HPS_GEOM_NB.values())   
    LIST_HPS.append(HPS_NB)
    LIST_HPS.append(HPS_GEOM_NB)
    HPS_GEOM_NB_TOTAL = {key: key * value for key, value in HPS_GEOM_NB.items()}
    HPS_GEOM_NB_TOTAL = sum(HPS_GEOM_NB_TOTAL.values())
    LIST_HPS.append(HPS_GEOM_NB_TOTAL)
    return(LIST_HPS)


# #%% test
# import requests

# GEOJSON_URL = "https://database.eamena.org/api/search/export_results?paging-filter=1&tiles=true&format=geojson&reportlink=false&precision=6&language=*&total=1641&resource-type-filter=%5B%7B%22graphid%22%3A%2234cfe98e-c2c0-11ea-9026-02e7594ce0a0%22%2C%22name%22%3A%22Heritage%20Place%22%2C%22inverted%22%3Afalse%7D%5D&map-filter=%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22Grid%20ID%22%3A%22E60N30-24%22%2C%22buffer%22%3A%7B%22width%22%3A%220%22%2C%22unit%22%3A%22m%22%7D%2C%22inverted%22%3Afalse%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B60.5%2C31.25%5D%2C%5B60.5%2C31.5%5D%2C%5B60.75%2C31.5%5D%2C%5B61%2C31.5%5D%2C%5B61.25%2C31.5%5D%2C%5B61.5%2C31.5%5D%2C%5B61.75%2C31.5%5D%2C%5B62%2C31.5%5D%2C%5B62%2C31.25%5D%2C%5B62.25%2C31.25%5D%2C%5B62.25%2C31%5D%2C%5B62.25%2C30.75%5D%2C%5B62%2C30.75%5D%2C%5B62%2C30.5%5D%2C%5B61.75%2C30.5%5D%2C%5B61.5%2C30.5%5D%2C%5B61.5%2C30.25%5D%2C%5B61.25%2C30.25%5D%2C%5B61%2C30.25%5D%2C%5B60.75%2C30.25%5D%2C%5B60.75%2C30.5%5D%2C%5B60.75%2C30.75%5D%2C%5B61%2C30.75%5D%2C%5B61%2C31%5D%2C%5B60.75%2C31%5D%2C%5B60.75%2C31.25%5D%2C%5B60.5%2C31.25%5D%5D%5D%7D%7D%5D%7D"
# resp = requests.get(GEOJSON_URL)
# data = resp.json()

# #%% test




# # %%

# zenodo_statistics(data)

# # zenodo_contributors(data)
# # zenodo_keywords(data)
# # zenodo_dates(data)
# # # %%

# # %%

# %%

# zenodo_related_identifiers()
# %%

def zenodo_read(file_url = "https://zenodo.org/records/10375902/files/sistan_part1_hps.zip?download=1", file_extension='.geojson', output_directory='extracted_files', verbose=True):
    """
    Read Zenodo files (GeoJSON files, zipped or not), returns a geopandas dataframe.

    :param file_url: the Zenodo URL of the download
    :param file_extension: the file extension of the file to download (default: '.geojson')
    :param output_directory: the output directory 

    >>> geojson_data = zenodo_read(file_url = "https://zenodo.org/records/10375902/files/sistan_part1_hps.zip?download=1")
    >>> geojson_data = zenodo_read(file_url="https://zenodo.org/records/13329575/files/EAMENA_Grid_contour.geojson?download=1")
    """
    import os
    import wget
    import zipfile
    import geopandas as gpd

    output_file = wget.download(file_url)
    if verbose:
        print(f"Downloaded file: {output_file}")
    if zipfile.is_zipfile(output_file):
        if verbose:
            print(f"Try to read a ZIP file")
        # Path to the downloaded ZIP file
        zip_file_path = output_file # 'downloaded_file.zip'  # Replace with the actual path to your ZIP file

        # Directory to extract the GeoJSON file
        # output_directory = 'extracted_files'
        # TODO: replace this by a temp file
        os.makedirs(output_directory, exist_ok=True)

        # Open the ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zf:
            # List the contents of the ZIP file
            zip_contents = zf.namelist()
            
            # Find the GeoJSON file
            geojson_file = next((f for f in zip_contents if f.lower().endswith(file_extension)), None)
            
            if geojson_file:
                # Extract only the GeoJSON file to the output directory
                zf.extract(geojson_file, output_directory)
                geojson_data = os.path.join(output_directory, geojson_file)
                if verbose:
                    print(f"Extracted GeoJSON file to: {geojson_data}")
            else:
                if verbose:
                    print("No GeoJSON file found in the ZIP archive.")
            # Load the GeoJSON file
    if not zipfile.is_zipfile(output_file):
        if verbose:
            print(f"Try to read a GeoJSON file")
        # TODO: test if GeoJSON
        geojson_data = output_file
    gdf = gpd.read_file(geojson_data)
    return gdf
    # Extract the first feature as a GeoDataFrame
    # first_feature_gdf = gdf.iloc[[0]]  # iloc[0] gets the first feature; using [[0]] preserves it as a GeoDataFrame

def zenodo_read_metadata(zenodo_oai = 'https://zenodo.org/oai2d', metadataPrefix='oai_dc', zenodo_community='user-eamena', verbose=True):
    """
    Read Zenodo metadata from a community, returns a geopandas dataframe.

    :param zenodo_oai: the URL of the Zenodo OAI API
    :param metadataPrefix: the Zenodo metadata prefix
    :param zenodo_community: the Zenodo community

    >>> zenodo_read_metadata()
    """
    import sickle
    from sickle import Sickle
    import pandas as pd

    sickle = Sickle(zenodo_oai)
    records = sickle.ListRecords(metadataPrefix=metadataPrefix, set=zenodo_community)

    data = []
    for record in records:
        metadata = record.metadata
        title = metadata.get('title', ['No Title'])[0]
        # collectors = metadata.get('creator', ['Unknown'])
        collectors = metadata.get('contributor')
        # badges = metadata.get('badge', ['No Badges'])
        doi = metadata.get('identifier')

        data.append({
            'Title': title,
            'Data Collector': collectors,
            'Doi': doi[0]
        })
        # Safety break to avoid too long loops during testing
        # Remove or modify this based on actual needs
        if len(data) > 20:
            break
    df = pd.DataFrame(data)
    df.sort_values(by='Title', ascending=False)
    return df

def zenodo_folium(gdf = None, zoom_start=12):
    """
    Plot a geopandas on a folium map.

    :param gdf: a geopandas dataframe, maybe heritated form the zenodo_read() function
    :param zoom_start: starting zoom. Default 12. 
    """
    import folium

    # Get the centroid and center the map
    centroid = gdf.geometry.centroid.iloc[0]
    map_center = [centroid.y, centroid.x]
    my_map = folium.Map(location=map_center, zoom_start=zoom_start)

    folium.GeoJson(gdf.__geo_interface__).add_to(my_map)
    return my_map

def zenodo_folium_by_HP(gdf = None, id_field = 'EAMENA ID', zoom_start=12):
    """
    Create an interactive folium map for a Jupyter NB, allowing a user to select an HP and having a zoom in (NOT WORKING)

    :param gdf: a geopandas dataframe, maybe heritated form the zenodo_read() function
    :param id_field: the selection will be on this field.
    :param zoom_start: starting zoom. Default 12. 
    """
    import ipywidgets as widgets
    from IPython.display import display
    import folium

    # Create a list of unique EAMENA IDs
    eamena_ids = gdf[id_field].unique()

    # Create a dropdown widget
    dropdown = widgets.Dropdown(
        options=eamena_ids,
        description=f'{id_field}:',
        value=eamena_ids[0],  # Default selection is the first option
        style={'description_width': 'initial'}
    )

    # Function to update the map based on the selected ID
    def update_map(eamena_id):
        # Filter GeoDataFrame for the selected EAMENA ID
        selected_feature_gdf = gdf[gdf[id_field] == eamena_id]

        # Get the centroid of the selected feature
        centroid = selected_feature_gdf.geometry.centroid.iloc[0]
        map_center = [centroid.y, centroid.x]

        # Create a folium map centered at the centroid of the selected feature
        my_map = folium.Map(location=map_center, zoom_start=zoom_start)

        # Add the selected feature to the map using GeoJSON
        folium.GeoJson(selected_feature_gdf.__geo_interface__).add_to(my_map)

        display(my_map)

    # Observe changes in the dropdown selection and update the map
    def on_dropdown_change(change):
        if change['type'] == 'change' and change['name'] == 'value':
            update_map(change['new'])

    dropdown.observe(on_dropdown_change)

    # Display the dropdown and an initial map
    display(dropdown)
    update_map(eamena_ids[100])  # Initial map with the first ID
