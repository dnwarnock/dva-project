"""
This script assumes that it is invoked from it's home directory.
It takes one command line argument with possible values `tcad`, `zillow`,
    `googlemaps`, `feature_matrix`, `all`.
As a result, it will pull the relevant files from S3 for each process,
and then created the desired output.
See `README.md` for more detail.
"""

import os
import re
import sys
import json
import boto3
import numpy as np
import pandas as pd
from functools import reduce
from collections import defaultdict


def dedupe(df, pk):
    orig_cols = list(df.columns)
    df['row_num'] = df.groupby(pk).cumcount()+1
    return df[df['row_num'] == 1][orig_cols]

def collect_adj_zips():
    s3 = boto3.resource('s3', region_name = 'us-west-2')
    bucket = s3.Bucket('dva-gatech-atx')
    bucket.download_file('adjacent_zips.csv', 'data/adjacent_zips.csv')

    # kind of hacky, but this file was made manually, so want to reformat
    zip_pairs = []
    with open("data/adjacent_zips.csv", 'r') as f:
        for row in f:
            row = row.replace("\n", "")
            zip_pairs.append(row.split(","))

    zip_map = defaultdict(set)
    for pair in zip_pairs:
        zip_map[int(pair[0])].add(int(pair[1]))
        zip_map[int(pair[1])].add(int(pair[0]))

    # sets are json serializeable
    for k, v in zip_map.items():
        zip_map[k] = list(v)

    with open("data/adjacent_zips.json", 'w') as f:
        json.dump(zip_map, f)

def collect_tcad():
    """Pulls required tcad files from S3 and stores them locally"""
    s3 = boto3.resource('s3', region_name = 'us-west-2')
    bucket = s3.Bucket('dva-gatech-atx')
    if not os.path.isdir('data/tcad'):
        os.mkdir('data/tcad')

    # pull header file
    bucket.download_file('tcad/headers.json', 'data/tcad/headers.json')

    files = ['STATE_CD.TXT', 'PROP.TXT', 'LAND_DET.TXT', 'IMP_DET.TXT', 'MOBILE_HOME_INFO.TXT']
    years = ['2015', '2016', '2017', '2018']
    for year in years:
        if not os.path.isdir('data/tcad/{}'.format(year)):
            os.mkdir('data/tcad/{}'.format(year))
        for file in files:
            if os.path.isfile('data/tcad/{}/{}'.format(year, file)):
                print("file {} is already stored locally, skipping".format(file))
            else:
                print("downloading file {} for year {}".format(file, year))
                bucket.download_file('tcad/{}/{}'.format(year, file), 'data/tcad/{}/{}'.format(year, file))

def collect_zillow():
    """Pulls required zillow files from S3 and stores them locally"""
    s3 = boto3.resource('s3', region_name = 'us-west-2')
    bucket = s3.Bucket('dva-gatech-atx')
    if not os.path.isdir('data/zillow'):
        os.mkdir('data/zillow')

    filenames = []
    for file in bucket.objects.all():
        if('output' in file.key):
            filenames.append(file.key)
    loop_ct = 0
    for file in filenames:
        loop_ct += 1
        if loop_ct % 100 == 0:
            print('extracted {} files, {}% complete'.format(loop_ct, float(loop_ct)*100/len(filenames)))
        file_name = file.split('/')[-1]
        if os.path.isfile("data/zillow/{}".format(file_name)):
            print("zillow file {} is already downloaded locally, skipping".format(file_name))
        else:
            print("downloading zillow file {}".format(file_name))
            bucket.download_file(file, "data/zillow/{}".format(file_name))

def collect_googlemaps():
    """Pulls required google maps files from S3 and stores them locally"""
    # data already aggregated by other process
    s3 = boto3.resource('s3', region_name = 'us-west-2')
    bucket = s3.Bucket('dva-gatech-atx')
    file_name = 'GeoData.csv'
    if not os.path.isdir('data/googlemaps'):
        os.mkdir('data/googlemaps')
    if os.path.isfile('data/googlemaps/{}'.format(file_name)):
        print("google maps file is already stored locally, skipping")
    else:
        bucket.download_file('googlemaps/{}'.format(file_name), 'data/googlemaps/{}'.format(file_name))

def aggregate_improvements(df):
    df['Imprv_det_type_desc'] = df['Imprv_det_type_desc'].str.upper()  # standardize case
    df['has_outdoor_space'] = (df['Imprv_det_type_desc'].str.contains('DECK', na=False) | df['Imprv_det_type_desc'].str.contains('PORCH', na=False) | df['Imprv_det_type_desc'].str.contains('TERRACE', na=False)).astype(int)
    df['has_garage'] = df['Imprv_det_type_desc'].str.contains('GARAGE').astype(int)
    df['has_pool'] = df['Imprv_det_type_desc'].str.contains('POOL').astype(int)
    df['has_cenral_air'] = df['Imprv_det_type_desc'].str.contains('HVAC').astype(int)
    df['has_fireplace'] = df['Imprv_det_type_desc'].str.contains('FIREPLACE').astype(int)
    df['floor_type'] = df['Imprv_det_type_desc'].str.contains('FLOOR').astype(int)
    df['building_sqft'] = df['floor_type'] * df['imprv_det_area']

    new_df = df.groupby('prop_id').agg({
                                        'yr_built': 'min',
                                        'building_sqft': 'sum',
                                        'has_outdoor_space': 'max',
                                        'has_garage': 'max',
                                        'has_pool': 'max',
                                        'has_cenral_air': 'max',
                                        'has_fireplace': 'max'
                                        }).reset_index()

    return new_df

def aggregate_land(df):
    df['is_commercial'] = df['land_type_desc'].str.contains('Commercial').astype(int)
    df['is_ag'] = (df['ag_apply'] == 'T').astype(int)
    df['land_sqft'] = df['size_square_feet']
    new_df = df.groupby('prop_id').agg({
            'land_sqft': 'sum',
            'is_commercial': 'max',
            'is_ag': 'max'
        }).reset_index()
    return new_df

def make_prop_cd(prop, cd):
    joined_df = prop.merge(cd, left_on='imprv_state_cd', right_on='state_cd', how='left')
    joined_df['is_deliverable'] = (joined_df['py_addr_ml_deliverable'] == 'Y').astype(int)
    del joined_df['py_addr_ml_deliverable']
    joined_df['is_residential'] = (joined_df['prop_type_cd'] == 'R').astype(int)
    del joined_df['prop_type_cd']
    joined_df['is_unit'] = 1 - (joined_df['situs_unit'].isnull()).astype(int)
    del joined_df['situs_unit']

    # make dummies for property type
    for elem in joined_df['ptd_state_cd_description'].unique():
        joined_df[str(elem).lower().replace(' ', '_')] = (joined_df['ptd_state_cd_description'] == elem).astype(int)

    return joined_df


def make_tcad_features():
    """Makes a feature matrix for tcad data"""
    with open("data/tcad/headers.json", "r") as f:
        header_map = json.load(f)

    year = '2018'  # only use 2018 for features
    prop_df = pd.read_fwf(
                        "data/tcad/{}/PROP.TXT".format(year),
                        names=header_map["PROP.TXT"]["names"],
                        widths=header_map["PROP.TXT"]["lengths"]
                    )
    imp_df = pd.read_fwf(
                        "data/tcad/{}/IMP_DET.TXT".format(year),
                        names=header_map["IMP_DET.TXT"]["names"],
                        widths=header_map["IMP_DET.TXT"]["lengths"]
                    )
    land_df = pd.read_fwf(
                        "data/tcad/{}/LAND_DET.TXT".format(year),
                        names=header_map["LAND_DET.TXT"]["names"],
                        widths=header_map["LAND_DET.TXT"]["lengths"]
                    )
    state_df = pd.read_fwf(
                        "data/tcad/{}/STATE_CD.TXT".format(year),
                        names=header_map["STATE_CD.TXT"]["names"],
                        widths=header_map["STATE_CD.TXT"]["lengths"]
                    )

    mobile_df = pd.read_fwf(
                        "data/tcad/{}/MOBILE_HOME_INFO.TXT".format(year),
                        names=header_map["MOBILE_HOME_INFO.TXT"]["names"],
                        widths=header_map["MOBILE_HOME_INFO.TXT"]["lengths"]
                    )

    prop_fields = ["prop_id", "prop_type_cd", "geo_id", "py_addr_ml_deliverable", "hood_cd",
                    "appraised_val", "ten_percent_cap", "assessed_val", "market_value",
                    "situs_num", "situs_unit", "situs_zip", "imprv_state_cd", "land_state_cd"]
    imp_fields = ["prop_id", "Imprv_det_type_desc", "yr_built", "imprv_det_area"]
    land_fields = ["prop_id", "land_type_desc", "size_square_feet", "mkt_ls_class", "ag_apply",
                    "land_homesite_pct"]
    mobile_fields = ["prop_id"]
    state_fields = ["state_cd", "ptd_state_cd_description"]

    prop_df = make_prop_cd(prop_df[prop_fields], state_df[state_fields])
    imp_df = aggregate_improvements(imp_df[imp_fields])
    land_df = aggregate_land(land_df[land_fields])
    mobile_df = mobile_df[mobile_fields]
    mobile_df['is_mobile'] = 1

    dfs = [prop_df, imp_df, land_df, mobile_df]
    combined_df = reduce(lambda left,right: pd.merge(left, right, on='prop_id', how='left'), dfs)

    # join dfs & write out
    combined_df.to_csv("data/tcad/tcad_features.csv", index=False)

def make_tcad_historical():
    """Makes long version of tcad files so we can see appraised values over time"""
    with open("data/tcad/headers.json", "r") as f:
        header_map = json.load(f)

    years = ["2015", "2016", "2017", "2018"]
    dataframes = []
    for year in years:
        df = pd.read_fwf(
                        "data/tcad/{}/PROP.TXT".format(year),
                        names=header_map["PROP.TXT"]["names"],
                        widths=header_map["PROP.TXT"]["lengths"]
                    )
        df = df[["prop_id", "prop_val_yr", "appraised_val"]]
        dataframes.append(df)

    combined_df = pd.concat(dataframes)
    combined_df.to_csv("data/tcad/history_file.csv", index=False)

def get_baths(bath_str):
    # helper for parsing bathroom string from zillow
    if not bath_str:
        return None

    nums = re.findall('\d', bath_str)
    if len(nums) == 1:
        return float(nums[0])
    elif len(nums) == 2:
        return float(nums[0]) + (float(nums[1]) * 0.5)
    else:
        return None

def make_float(tmp):
    try:
        return float(tmp)
    except:
        return None

def make_int(tmp):
    try:
        return int(tmp)
    except:
        return None

def make_zillow_features():
    combined_data = []
    for root, dirs, files in os.walk("data/zillow/"):
        for file in files:
            if file[-4:] != 'json':
                continue
            print('processing file {}'.format(file))
            with open(root + file, 'r') as f:
                data = json.load(f)
            record = {}
            for prop in data:
                if len(prop) == 2:
                    continue  # skip if just have id and address
                record['prop_id'] = prop.get('id')
                record['address'] = prop.get('address')
                record['zestimate'] = make_float(prop.get('zestimate').replace('$', '').replace(',', '')) if prop.get('zestimate') and prop.get('zestimate') != 'None' else None
                record['type'] = prop.get('type')[0] if prop.get('type') else None
                record['yearbuilt'] = make_int(prop.get('yearbuilt')[0]) if len(prop.get('yearbuilt', [])) else None
                record['floorsize'] = make_float(prop.get('floorsize')[0].replace(' sqft', '').replace(',', '')) if len(prop.get('floorsize', [])) > 0 else None
                # omit lot due to inconsistent units & have from TCAD
                # record['lot_size'] = float(prop.get('lot')[0].replace(' acres', '').replace(',', '')) if len(prop.get('lot', [])) > 0 else None
                record['beds'] = make_float(prop.get('beds')[0]) if len(prop.get('beds', [])) > 0 else None
                record['baths'] = get_baths(prop.get('baths')[0]) if len(prop.get('baths', [])) > 0 else None

                flooring_str = str(prop.get('flooring', '')).lower()
                record['has_hardwood'] = 1 if flooring_str.find('hardwood') != -1 else 0
                record['has_carpet'] = 1 if flooring_str.find('carpet') != -1 else 0
                record['has_tile'] = 1 if flooring_str.find('tile') != -1 else 0
                record['zillow'] = 1

                combined_data.append(record)

    df = pd.DataFrame(combined_data)
    df.to_csv("data/zillow/zillow_features.csv", index=False)

def make_feature_matrix():
    maps = dedupe(pd.read_csv("data/googlemaps/GeoData.csv"), 'prop_id')  # use maps data as "left" table since filtered already
    tcad = dedupe(pd.read_csv("data/tcad/tcad_features.csv"), 'prop_id')
    zillow = dedupe(pd.read_csv("data/zillow/zillow_features.csv"), 'prop_id')

    dfs = [maps, tcad, zillow]
    feature_matrix = reduce(lambda left,right: pd.merge(left, right, on='prop_id', how='left'), dfs)

    feature_matrix[['is_mobile', 'zillow']] = feature_matrix[['is_mobile', 'zillow']].fillna(value=0)

    feature_matrix.to_csv("data/combined_feature_matrix.csv", index=False)

def make_input_feature_matrix():
    """ this function reads the output of make_feature_matrix() prepares it for input to scoring"""
    dtype_map = {
        'prop_id': np.object,
        'Address': np.object,
        'City': np.object,
        'State': np.object,
        'Lat': np.object,
        'Long': np.object,
        'geo_id': np.object
    }
    df = pd.read_csv("data/combined_feature_matrix.csv", dtype=dtype_map)

    cols = list(df.columns)

    # categorical
    categorical_features = []
    for col in cols:
        if col[0:3] == 'is_' or col[0:4] == 'has_':
            categorical_features.append(col)
            df[col] = df[col].fillna(value=0).astype(int).astype(str)

    # continuous
    continuous_features = []
    for col in cols:
        if col[0:3] != 'is_' and col[0:4] != 'has_' and df[col].dtype == 'float64' and col != 'zillow':
            continuous_features.append(col)

    df['hamming'] = df[categorical_features].apply(lambda x: ''.join(x), axis=1)

    base_fields = ['prop_id', 'situs_zip',  'zillow', 'Lat', 'Long', 'hood_cd', 'hamming']

    features = df[base_fields + continuous_features]
    features.to_csv("data/input_feature_matrix.csv", index=False)

if __name__ == '__main__':
    if not os.path.isdir('data'):
        os.mkdir('data')

    function = sys.argv[1]
    if function == 'zips' or function == 'all':
        collect_adj_zips()
    if function == 'tcad' or function == 'all':
        collect_tcad()
        make_tcad_historical()
        make_tcad_features()
    if function == 'zillow' or function == 'all':
        collect_zillow()
        make_zillow_features()
    if function == 'googlemaps' or function == 'all':
        collect_googlemaps()
    if function == 'feature_matrix' or function == 'all':
        make_feature_matrix()
        make_input_feature_matrix()
