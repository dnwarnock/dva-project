import sys
import random
import numpy as np
import pandas as pd


def generate_test_scores():
    """
    A funnction to generate random pairs and similarity scores
    This is used to generate a file to enable front-end testing at scale
    while the actual scoring runs.
    """
    records = []
    df = pd.read_csv("data/combined_feature_matrix.csv")
    for i in range(df.shape[0]):
        if i % 100 == 0:
            print("{}% comppete. processing property {} of {}".format((i * 100.0)/df.shape[0], i, df.shape[0]))
        prop1 = df.iloc[i]['prop_id']
        sim_score = random.random()
        for j in range(20):
            rand_idx = int(random.random() * df.shape[0])
            prop2 = df.iloc[rand_idx]['prop_id']
            sim_score *= .9
            sim_rank = j + 1
            records.append({
                    'search_prop': prop1,
                    'sim_prop': prop2,
                    'sim_score': sim_score,
                    'sim_rank': sim_rank
                })
    test_df = pd.DataFrame(records)
    test_df.to_csv("data/test_similarities.csv", index=False)


def create_feature_input():
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

    # pre-partition by zip for fast lookup instead of repeated filter
    zip_map = {}
    for zipcode in features['situs_zip'].unique():
        try:
            zipcode = str(zipcode).replace('.0', '')
        except:
            import ipdb; ipdb.set_trace()
        zip_map[zipcode] = df[df['situs_zip'] == zipcode]

    return features, zip_map


def hamming(a, b):
    assert len(a) == len(b)
    hamming_ct = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            hamming_ct += 1
    return hamming_ct


def generate_scores(prop_record, zip2zip, zip_map):
    """
    This function finds similar properties
    """
    this_zip = prop_record['zip']
    candidate_zips = [this_zip] + zip2zip.get('this_zip')
    possible_matches = pd.concat([zip_map.get(z) for z in candidate_zips])

    prop_record = pd.DataFrame(np.repeat(prop_record, possible_matches.shape[0], axis=0))

    possible_matches['comp_hamming'] =

    possible_matches['hamming_dist'] =


    # norm(hamming) + norm(eucliedean)

if __name__ == '__main__':
    mode = sys.argv[1]

    if mode == 'test':
        generate_test_scores()
    elif mode == 'all':
        pass
    else:
        raise Exception("unexpected argument {}. values are `test` and `all`".format(mode))
