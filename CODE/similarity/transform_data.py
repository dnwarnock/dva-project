import numpy as np
import pandas as pd
import pickle
import boto3
import json
import sys
import os

from tqdm import tqdm


s3 = boto3.resource('s3', region_name = 'us-west-2')
bucket = s3.Bucket('dva-gatech-atx')


def flatten(file_path, index, columns, values, dtype=None):
  df = pd.read_csv(file_path, dtype=dtype)
  df.rename(columns={'search_prop': '_id', 'prop_id': '_id', 'prop_val_yr': 'year', 'appraised_val': 'appraisal'}, inplace=True)
  df = df.drop_duplicates(subset=[index, columns])
  df = df.pivot(index=index, columns=columns, values=values)
  return pd.DataFrame.from_records(df.to_records())

def main(historical_file, similarities_file, features_file, output_file):
  historical = flatten(historical_file, '_id', 'year', 'appraisal')
  historical.rename(columns={"2015": 'appraisal_2015', "2016": 'appraisal_2016', "2017": 'appraisal_2017'}, inplace=True)
  similarities = flatten(similarities_file, '_id', 'sim_rank', 'sim_prop')
  features = pd.read_csv(features_file)
  features.rename(columns={'search_prop': '_id', 'prop_id': '_id', 'prop_val_yr': 'year', 'appraised_val': 'appraisal'}, inplace=True)
  features = features.drop_duplicates(subset=['_id'], keep='first')
  merge = pd.merge(features, historical, on='_id', how='left', validate='one_to_one')

  merge = merge.drop_duplicates(subset=['_id'], keep='first')

  output = []

  str_keys = {'address', 'City', 'State', 'imprv_state_cd', 'land_state_cd', 'state_cd', 'ptd_state_cd_description', 'hood_cd', 'situs_num'}

  for index, row in tqdm(merge.iterrows(), total=merge.shape[0]):
    item = merge.iloc[index].to_dict()
    for key, value in item.items():
      if(key in str_keys):
        item[key] = str(value).upper()
      elif(key == 'Lat' or key == 'Long'):
        try:
          item[key] = float(value)
        except:
          item[key] = 30.2672
      else:
        try:
          item[key] = int(value)
        except:
          try:
            item[key] = float(value)
          except:
            item[key] = str(value)

    item['address'] = item['address'].upper()

    try:
      similar = similarities.loc[similarities['_id'] == row['_id']].to_dict(orient='records')[0]
      similar.pop('_id')
      item['similar'] = [ int(val) for val in similar.values()]
    except:
      item['similar'] = []
    output.append(item)


  with open(output_file, 'w') as fp:
    json.dump(output, fp)

  bucket.upload_file(output_file, 'prepared_data/{}'.format(output_file))
  os.remove(output_file)


def get_base_files():
    bucket.download_file('prepared_data/history_file.csv', 'history_file.csv')
    bucket.download_file('prepared_data/combined_feature_matrix.csv', 'combined_feature_matrix.csv')

def get_sim_files(metric_list):
  for metric in metric_list:
    bucket.download_file('prepared_data/{}_similarities.csv'.format(metric), '{}_similarities.csv'.format(metric))

def clean_up(metric_list):
  os.remove('history_file.csv')
  os.remove('combined_feature_matrix.csv')

  for metric in metric_list:
    os.remove('{}_similarities.csv'.format(metric))

if __name__ == '__main__':
  if sys.argv[1] == 'euclidean':
    get_base_files()
    get_sim_files(['euclid'])
    main('history_file.csv', 'euclid_similarities.csv', 'combined_feature_matrix.csv', 'application_data_euclidean.json')
    clean_up(['euclid'])
  elif sys.argv[1] == 'manhattan':
    get_base_files()
    get_sim_files(['manhattan'])
    main('history_file.csv', 'manhattan_similarities.csv', 'combined_feature_matrix.csv', 'application_data_manhattan.json')
    clean_up(['manhattan'])
  elif sys.argv[1] == 'lsh':
    get_base_files()
    get_sim_files(['lsh'])
    main('history_file.csv', 'lsh_similarities.csv', 'combined_feature_matrix.csv', 'application_data_lsh.json')
    clean_up(['lsh'])
  elif sys.argv[1] == 'all':
    get_base_files()
    get_sim_files(['euclid', 'manhattan', 'lsh'])
    main('history_file.csv', 'euclid_similarities.csv', 'combined_feature_matrix.csv', 'application_data_euclidean.json')
    main('history_file.csv', 'manhattan_similarities.csv', 'combined_feature_matrix.csv', 'application_data_manhattan.json')
    main('history_file.csv', 'lsh_similarities.csv', 'combined_feature_matrix.csv', 'application_data_lsh.json')
    clean_up(['euclid', 'manhattan', 'lsh'])

  else:
    raise Exception("Expected argument `euclidean`, `manhattan`, `lsh`, or `all`. Got {}".format(sys.argv[1]))
