
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
    
    """
    df = summed_values(data, fieldname)
    CONTRIBUTORS = list()
    for name in df['name']:
        contibut = contributors_layout.copy()
        contibut['name'] = name
        # TODO: "affiliation" and "orcid"
        contibut = {key: value for key, value in contibut.items() if value is not None and value != 'null'}
        CONTRIBUTORS.append(contibut)
    return CONTRIBUTORS

def zenodo_keywords(data = None, constant = ['EAMENA', 'MaREA'], fields = ["Country Type", "Cultural Period Type"]):
    """
    Creates a list of keywords with a constant basis (`constant`) and parsed supplementary `fields` (for space-time keywords)
    
    """
    KEYWORDS = list()
    KEYWORDS = KEYWORDS + constant
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
