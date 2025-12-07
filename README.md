# Extract-NHGIS

A program to extract [iPUMS NHGIS](https://www.nhgis.org/) aggregate Census data through API calls.

## Overview

The IPUMS National Historical Geographic Information System (NHGIS) provides a vast collection of U.S. Census Bureau data and its interface is by far the most convenient way to access the data.  However, extracting multiple years of aggregate data can be tedious, because NHGIS variable names often aren't consistent across years. This program allows variables to be specified using Census table numbers rather than NHGIS names.

## Usage

### 1. Obtain an API Key

Get an [API key from iPUMS](https://developer.ipums.org/docs/v2/get-started/).

### 2. Install required 

Install ipumspy and pandas if necessary

### 3. Download Required Files

Download `extract_nhgis_agg.py` and `mk_nhgis_example.py`. These programs should either be in the same directory, or `extract_nhgis_agg.py` should be in your path.

### 4. Configure Parameters

Modify the parameters for your use case, specifying the dataset and the tables to extract, then call the `get_nhgis()` function. For example:
```python
year         = 2023
geog         = 'state'
dataset      = '2018_2022_ACS5a'
api_key      = 'YOUR-API-KEY-HERE'
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
```

### 5. Extract Variables

Add code to extract particular variables. For example:
```python
create_nhgis_var(acs, 'medage', 'B01002', 'E001', source_to_nhgis, nhgis_to_vars)  # Median age: Total
```

Where:
- `'B01002'` is the table name
- `'E001'` is one item (variable) from the table
- `acs` (a pandas DataFrame returned by `get_nhgis()`) is the dataset being created
- `source_to_nhgis` and `nhgis_to_vars` are dictionaries returned by `get_nhgis()`.  They need to be passed to create_nhgis_var() but aren't otherwise necessary.

### 6. Run the Program

Execute `mk_nhgis_example.py` (or your own program).

### 7. Access the Results

The created variables (e.g., `acs['medage']`) are numeric and have dictionary variable labels attached (e.g., `acs['medage'].attrs['label']`).
