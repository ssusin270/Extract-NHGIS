# Extract-NHGIS

A program to extract [iPUMS NHGIS](https://www.nhgis.org/) aggregate Census data through API calls.

## Overview

I've found extracting multiple years of ACS aggregate data to be tedious, because NHGIS gives arbitrary names to the variables in each data file that aren't consistent across years. This program allows variables to be specified using Census table numbers rather than NHGIS names.

## Usage

### 1. Obtain an API Key

Get an [API key from iPUMS](https://developer.ipums.org/docs/v2/get-started/).

### 2. Download Required Files

Download `extract_nhgis_agg.py` and `mk_nhgis_example.py`. These programs should either be in the same directory, or `extract_nhgis_agg.py` should be in your path.

### 3. Configure Parameters

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

### 4. Extract Variables

Add code to extract particular variables. For example:
```python
create_nhgis_var(acs, 'medage', 'B01002', 'E001', source_to_nhgis, nhgis_to_vars)  # Median age: Total
```

Where:
- `'B01002'` is the table name
- `'E001'` is one item (variable) from the table
- `acs` (a pandas DataFrame), `source_to_nhgis` (a dictionary), and `nhgis_to_vars` (a dictionary) are outputs returned by `get_nhgis()`

### 5. Run the Program

Execute `mk_nhgis_example.py` (or your own program).

### 6. Access the Results

The created variables (e.g., `acs['medage']`) are numeric and have dictionary variable labels attached (e.g., `acs['medage'].attrs['label']`).
