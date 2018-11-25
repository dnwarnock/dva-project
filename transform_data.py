import numpy as np
import pandas as pd
import json
import pickle
import sys

from tqdm import tqdm

def flatten(file_path, index, columns, values, dtype=None):
  df = pd.read_csv(file_path, dtype=dtype)
  df = df.drop_duplicates(subset=[index, columns])
  df = df.pivot(index=index, columns=columns, values=values)
  return pd.DataFrame.from_records(df.to_records())


if __name__ == '__main__':
  historical_file = sys.argv[1]
  similarities_file = sys.argv[2]
  features_file = sys.argv[3]
  output_file = sys.argv[4]


  historical = flatten(historical_file, '_id', 'year', 'appraisal')
  historical.rename(columns={"2015": 'appraisal_2015', "2016": 'appraisal_2016', "2017": 'appraisal_2017'}, inplace=True)
  similarities = flatten(similarities_file, '_id', 'sim_rank', 'sim_prop')
  features = pd.read_csv(features_file)
  features = features.drop_duplicates(subset=['_id'], keep='first')
  merge = pd.merge(features, historical, on='_id', how='left', validate='one_to_one')

  merge = merge.drop_duplicates(subset=['_id'], keep='first')

  output = []

  str_keys = {'address', 'City', 'State', 'imprv_state_cd', 'land_state_cd', 'state_cd', 'ptd_state_cd_description', 'hood_cd', 'situs_num'}

  for index, row in tqdm(merge.iterrows(), total=merge.shape[0]):
    try:
      item = merge.iloc[index].to_dict()
    except:
      print(index)
      continue
    for key, value in item.items():
      if(key in str_keys):
        item[key] = str(value).upper()
      elif(key == 'Lat' or key == 'Long'):
        item[key] = float(value)
      else:
        try:
          item[key] = int(value)
        except:
          item[key] = float(value)

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
