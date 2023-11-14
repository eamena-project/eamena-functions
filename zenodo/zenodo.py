

def field_values(fieldname = None):
    l = list()
    for i in range(len(data['features'])):
        l.append(data['features'][i]['properties'][fieldname])
    return(l)

def summed_values(l = None):
    import pandas as pd
    from collections import Counter

    split_names = [name.strip() for item in l if item is not None for name in item.split(',')]
    name_counts = Counter(split_names)
    df = pd.DataFrame.from_dict(name_counts, orient='index').reset_index()
    df = df.rename(columns={'index': 'name', 0: 'n_hp'})
    df = df.sort_values('n_hp', ascending=False)
    return df

def zenodo_contributors(contributors_layout = {"name": None, "affiliation": None, "orcid": None}):
    l = field_values("Assessment Investigator - Actor")
    df = summed_values(l)
    CONTRIBUTORS = list()
    for name in df['name']:
        contributors_layout['name'] = name
        # TODO: "affiliation" and "orcid"
        CONTRIBUTORS.append(contributors_layout.copy())
    return CONTRIBUTORS

def zenodo_keywords(constant = ['EAMENA', 'MaREA'], others = ["Country Type", "Cultural Period Type"]):
    KEYWORDS = list()
    KEYWORDS = KEYWORDS + constant
    for i in others:
        l = field_values(i)
        df = summed_values(l)
        KEYWORDS = KEYWORDS + df['name'].tolist()
    KEYWORDS.remove('Unknown')
    return KEYWORDS

def zenodo_dates(fields = ["Assessment Activity Date"]):
    from datetime import datetime

    ldates = list()
    for i in fields:
        l = field_values("Assessment Activity Date")
        df = summed_values(l)
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