
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

