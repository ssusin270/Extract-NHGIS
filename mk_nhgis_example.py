# -*- coding: utf-8 -*-
"""
Example program:
    Extracts several variables from NHGIS 2023 ACS 5-year file State-level data
"""

from extract_nhgis_agg import get_nhgis, create_nhgis_var

# set parameters
year         = 2023
geog         = 'state'
dataset      = '2018_2022_ACS5a'
api_key      = 'YOU-API-KEY-HERE'
tables       = ['B01002', 'B03002']
download_dir = 'c:/data/acs/2023a/'


acs, source_to_nhgis, nhgis_to_vars = get_nhgis(
    year=year,
    geog=geog,
    dataset=dataset,
    api_key=api_key,
    tables=tables,
    download_dir=download_dir
)

newcol = len(acs.columns)
acs['statefp'] = acs['STATEA']
acs['countyfp'] = acs['COUNTYA']
acs['tract'] = acs['TRACTA']


create_nhgis_var(acs, 'pop'           , 'B03002',  'E001', source_to_nhgis, nhgis_to_vars)   #Total
create_nhgis_var(acs, 'whitenh'       , 'B03002',  'E003', source_to_nhgis, nhgis_to_vars)   #Not Hispanic or Latino, White alone
create_nhgis_var(acs, 'blacknh'       , 'B03002',  'E004', source_to_nhgis, nhgis_to_vars)   #Not Hispanic or Latino, Black or African American alone
create_nhgis_var(acs, 'hisp'          , 'B03002',  'E012', source_to_nhgis, nhgis_to_vars)   #Hispanic or Latino
create_nhgis_var(acs, 'medage'        , 'B01002',  'E001', source_to_nhgis, nhgis_to_vars)   #Median age: Total

# Variables labels can be accessed as acs['colname'].attrs['label'] 
for V in list(acs.columns[newcol:]):
    print(f"{V:<16} : {acs[V].attrs.get('label', 'No label')}")



for V in ['whitenh', 'blacknh','hisp'] :
    fV = 'f'+V
    acs[fV] = acs[V]/acs['pop']


keepvars = list(acs.columns[newcol:]) 

print("/n", acs[keepvars].info())

outfile      = f'acs{year}_5yr_{geog}.pkl'
acs[keepvars].to_pickle(download_dir + outfile)

