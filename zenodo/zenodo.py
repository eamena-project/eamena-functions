
#%% test

def summed_values(data = None, fieldname = None):
    """
    Creates a dataframe summing the number of occurences for a given field
    
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
                        contributors_layout = {"name": None, "type": "DataCollector"}):
    """
    Creates dictionary of contributors, filling a dictionary layout (`contributors_layout`). Contributors are sorted according to the total number of their name occurences in the selected `fieldname`.
    
    :param data: dictionary
    """
    if fieldname in list(data['features'][0]['properties'].keys()):
    # HPs
        df = summed_values(data, fieldname)
        CONTRIBUTORS = list()
        for name in df['name']:
            contibut = contributors_layout.copy()
            contibut['name'] = name
            # TODO: "affiliation" and "orcid"
            contibut = {key: value for key, value in contibut.items() if value is not None and value != 'null'}
            CONTRIBUTORS.append(contibut)
    else:
    # not HPs (GS, ...)
        CONTRIBUTORS = ''
    return CONTRIBUTORS

def zenodo_keywords(data = None, constant = ['EAMENA', 'MaREA', 'Cultural Heritage'], fields = ["Country Type", "Cultural Period Type"]):
    """
    Creates a list of keywords with a constant basis (`constant`) and parsed supplementary `fields` (for space-time keywords)
    
    """
    KEYWORDS = list()
    KEYWORDS = KEYWORDS + constant
    if fields in list(data['features'][0]['properties'].keys()):
    # HPs
        for fieldname in fields:
            df = summed_values(data, fieldname)
            KEYWORDS = KEYWORDS + df['name'].tolist()
        KEYWORDS.remove('Unknown')
    return KEYWORDS

def zenodo_dates(data = None, fields = ["Assessment Activity Date"]):
    """
    Get the min and the max of dates recorded in `fields`    
    """
    from datetime import datetime

    if fields in list(data['features'][0]['properties'].keys()):
    # HPs
        ldates = list()
        for fieldname in fields:
            df = summed_values(data, fieldname)
            ldates = ldates + df['name'].tolist() 
        ldates.remove('None')
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
    Parse the 'EAMENA database' community in Zenodo ('user-eamena') to check if there are already uploaded datasets. Handle differently the refrence data (collections, RMs, ...) and the datasets, or business data. The former are 'isDescribedBy' related identifiers, whereas the latter are 'isContinuedBy' related resources.

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
    # remove the reference data
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

# #%% test
# import requests

# GEOJSON_URL = "https://database.eamena.org/api/search/export_results?paging-filter=1&tiles=true&format=geojson&reportlink=false&precision=6&language=*&total=25&resource-type-filter=%5B%7B%22graphid%22%3A%2277d18973-7428-11ea-b4d0-02e7594ce0a0%22%2C%22name%22%3A%22Grid%20Square%22%2C%22inverted%22%3Afalse%7D%5D&map-filter=%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22id%22%3A1%2C%22buffer%22%3A%7B%22width%22%3A%220%22%2C%22unit%22%3A%22m%22%7D%2C%22inverted%22%3Afalse%7D%2C%22geometry%22%3A%7B%22type%22%3A%22MultiPolygon%22%2C%22coordinates%22%3A%5B%5B%5B%5B61.9185199386503%2C31.434624233128837%5D%2C%5B61.93140337423312%2C31.176955521472394%5D%2C%5B62.17296779141103%2C31.164072085889572%5D%2C%5B62.195513803680974%2C30.829102760736195%5D%2C%5B61.91207822085889%2C30.829102760736195%5D%2C%5B61.92496165644171%2C30.587538343558283%5D%2C%5B61.396740797546%2C30.593980061349694%5D%2C%5B61.40318251533741%2C30.316986196319018%5D%2C%5B60.797661042944775%2C30.320207055214723%5D%2C%5B60.810544478527596%2C30.68094325153374%5D%2C%5B61.07465490797545%2C30.68094325153374%5D%2C%5B61.06821319018404%2C31.083550613496932%5D%2C%5B60.82342791411042%2C31.089992331288343%5D%2C%5B60.80732361963189%2C31.312231595092026%5D%2C%5B60.54643404907974%2C31.318673312883437%5D%2C%5B60.53355061349692%2C31.437845092024542%5D%2C%5B61.9185199386503%2C31.434624233128837%5D%5D%5D%5D%7D%7D%5D%7D"
# resp = requests.get(GEOJSON_URL)
# data = resp.json()
# # %%

# zenodo_contributors(data)
# zenodo_keywords(data)
# zenodo_dates(data)
# # %%
