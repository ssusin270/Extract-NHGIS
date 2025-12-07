# -*- coding: utf-8 -*-
"""
Read ACS and other NHGIS Aggregate data from iPUMS API

"""

from ipumspy import AggregateDataExtract, NhgisDataset, IpumsApiClient
from pathlib import Path
from zipfile import ZipFile
import pandas as pd


def get_nhgis(year, geog, dataset, api_key, tables, download_dir):
    """
    Download and parse NHGIS aggregate data.
    
    Parameters:
    - year: int, year of the aggregate data
    - geog: str, geographic level (e.g., 'state', 'county')
    - dataset: str, NHGIS dataset name (e.g., '2018_2022_ACS5a')
    - api_key: str, IPUMS API key
    - tables: str, table codes (e.g., "'B01002', 'B03002'")
    - download_dir: str, directory to download files to
    """
    # Check for missing parameters
    params = {
        'year': year,
        'geog': geog,
        'dataset': dataset,
        'api_key': api_key,
        'tables': tables,
        'download_dir': download_dir
    }
    
    missing = [name for name, value in params.items() if value is None]
    
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        
    # Additional validation
    if not tables or len(tables) == 0:
        raise ValueError("tables parameter must be a non-empty list")
    
    if not isinstance(tables, list):
        raise ValueError("tables parameter must be a list")
    
    
    ipums = IpumsApiClient(api_key)
        
    extract = AggregateDataExtract(
       collection="nhgis",
       description=f'ACS {year} 5yr {geog} file',
       datasets=[
          NhgisDataset(name=dataset, 
                       data_tables=tables,
                       geog_levels=[geog])
       ],
    )
    
    # Submit the extract request
    ipums.submit_extract(extract)
    print(f"Extract submitted with id {extract.extract_id}")
    #> Extract submitted with id 1
    
    # Wait for the extract to finish
    ipums.wait_for_extract(extract)
    
    # Download the extract
    DOWNLOAD_DIR = Path(download_dir)
    ipums.download_extract(extract, download_dir=DOWNLOAD_DIR)
    
    # Construct the filename (NHGIS format is typically nhgis####_csv.zip)
    zip_filename = DOWNLOAD_DIR / f"nhgis{extract.extract_id:04d}_csv.zip"
    
    # Unzip files directly to DOWNLOAD_DIR (flatten structure)
    if zip_filename and zip_filename.exists():
        with ZipFile(zip_filename, 'r') as zip_ref:
            for file in zip_ref.namelist():
                # Extract only the filename (no path)
                filename = Path(file).name
                # Skip directories
                if filename:
                    source = zip_ref.open(file)
                    target = open(DOWNLOAD_DIR / filename, "wb")
                    with source, target:
                        target.write(source.read())
                        
                    # Save the CSV filename
                    if filename.endswith('.csv'):
                        csv_file = DOWNLOAD_DIR / filename
                    # Save the codebook filename
                    if filename.endswith('.txt'):
                        codebook_file = DOWNLOAD_DIR / filename
            
        print(f"Extracted {zip_filename} to {DOWNLOAD_DIR}")
    else:
        print("Zip file not found")
        
    
    
    ### Parse Codebook
    def parse_nhgis_codebook(codebook_file):
        """
        Parse NHGIS codebook to map Source codes (e.g., B01002) to NHGIS codes (e.g., AQM5)
        and their variables.
        """
        source_to_nhgis = {}  # B01002 -> AQM5
        nhgis_to_vars = {}    # AQM5 -> {E001: 'Median age: Total', M001: 'Median age: Total (margin)', ...}
        
        with open(codebook_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_source = None
        current_nhgis = None
        
        for line in lines:
            line = line.strip()
            
            # Look for Source code line
            if line.startswith('Source code:'):
                current_source = line.split(':')[1].strip()
            
            # Look for NHGIS code line
            elif line.startswith('NHGIS code:'):
                current_nhgis = line.split(':')[1].strip()
                
                # Map source to NHGIS
                if current_source and current_nhgis:
                    source_to_nhgis[current_source] = current_nhgis
                    # Only initialize if it doesn't exist yet
                    if current_nhgis not in nhgis_to_vars:
                        nhgis_to_vars[current_nhgis] = {}
            
            # Look for variable lines (e.g., "AQM5E001:    Median age: Total")
            elif current_nhgis and ':' in line:
                # Check if line starts with the NHGIS code pattern
                if line.startswith(current_nhgis):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        var_code = parts[0].strip()  # e.g., AQM5E001 or AQM5M001
                        var_desc = parts[1].strip()  # e.g., Median age: Total
                        
                        # Extract the full suffix (E001, M001, etc.) - don't overwrite
                        suffix = var_code.replace(current_nhgis, '')
                        nhgis_to_vars[current_nhgis][suffix] = var_desc
        
        return source_to_nhgis, nhgis_to_vars
    
    source_to_nhgis, nhgis_to_vars = parse_nhgis_codebook(codebook_file)
    
    print("\nSource to NHGIS mapping:")
    print(source_to_nhgis)
    print("\nNHGIS variables:")
    for nhgis_code, vars in nhgis_to_vars.items():
        print(f"{nhgis_code}: {vars}")
                 
    acs = pd.read_csv(csv_file, dtype=str)
       
    return acs, source_to_nhgis, nhgis_to_vars    

def create_nhgis_var(df, var_name, source_code, var_suffix, source_to_nhgis, nhgis_to_vars):
    """
    Create a new variable from NHGIS data, convert to numeric, and add label.
    
    Parameters:
    - df: DataFrame
    - var_name: New variable name (e.g., 'median_age')
    - source_code: ACS table code (e.g., 'B01002')
    - var_suffix: Variable suffix (e.g., 'E001')
    - source_to_nhgis: Mapping dictionary
    - nhgis_to_vars: Variables dictionary
    """
    
    # Get the NHGIS code
    nhgis_code = source_to_nhgis.get(source_code)
    if not nhgis_code:
        print(f"Warning: Could not find source code {source_code}")
        return False
    
    # Construct the full variable name
    full_var = f"{nhgis_code}{var_suffix}"
    
    # Check if column exists
    if full_var not in df.columns:
        print(f"Warning: Could not find column {full_var}")
        return False
    
    # Create the variable
    df[var_name] = pd.to_numeric(df[full_var], errors='coerce')
    
    # Add label if available
    if nhgis_code and var_suffix in nhgis_to_vars.get(nhgis_code, {}):
        label = nhgis_to_vars[nhgis_code][var_suffix]
        df[var_name].attrs['label'] = label
    
    return True
