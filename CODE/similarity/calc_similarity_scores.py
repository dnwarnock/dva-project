import os
import re
import sys
import csv
import json
import time
import uuid
import boto3
import random
import numpy as np
import pandas as pd
import geopy.distance
from BitVector import BitVector
from sklearn import preprocessing
from LocalitySensitiveHashing import *


def sample_index(sample_name):
    return sample_name

def band_hash_group_index(block_name):
    '''
    The keys of the final output that is stored in the hash self.coalesced_band_hash
    are strings that look like:

         "block3 10110"

    This function returns the block index, which is the integer that follows the
    word "block" in the first substring in the string that you see above.
    '''
    firstitem = block_name.split()[0]
    m = re.search(r'(\d+)$', firstitem)
    return int(m.group(1))


class LSH(LocalitySensitiveHashing):

    def __init__(self, *args, **kwargs ):
        if kwargs and args:
            raise Exception(
                   '''LocalitySensitiveHashing constructor can only be called with keyword arguments for the
                      following keywords: datafile,csv_cleanup_needed,how_many_hashes,r,b,
                      similarity_group_min_size_threshold,debug,
                      similarity_group_merging_dist_threshold,expected_num_of_clusters''')
        allowed_keys = 'datafile','dim','csv_cleanup_needed','how_many_hashes','r','b','similarity_group_min_size_threshold','similarity_group_merging_dist_threshold','expected_num_of_clusters','debug'
        keywords_used = kwargs.keys()
        for keyword in keywords_used:
            if keyword not in allowed_keys:
                raise SyntaxError(keyword + ":  Wrong keyword used --- check spelling")
        datafile=dim=debug=csv_cleanup_needed=how_many_hashes=r=b=similarity_group_min_size_threshold=None
        similarity_group_merging_dist_threshold=expected_num_of_clusters=None
        if kwargs and not args:
            if 'csv_cleanup_needed' in kwargs : csv_cleanup_needed = kwargs.pop('csv_cleanup_needed')
            if 'datafile' in kwargs : datafile = kwargs.pop('datafile')
            if 'dim' in kwargs :  dim = kwargs.pop('dim')
            if 'r' in kwargs  :  r = kwargs.pop('r')
            if 'b' in kwargs  :  b = kwargs.pop('b')
            if 'similarity_group_min_size_threshold' in kwargs  :
                similarity_group_min_size_threshold = kwargs.pop('similarity_group_min_size_threshold')
            if 'similarity_group_merging_dist_threshold' in kwargs  :
                similarity_group_merging_dist_threshold = kwargs.pop('similarity_group_merging_dist_threshold')
            if 'expected_num_of_clusters' in kwargs  :
                expected_num_of_clusters = kwargs.pop('expected_num_of_clusters')
            if 'debug' in kwargs  :  debug = kwargs.pop('debug')
        self.datafile = datafile
        self._csv_cleanup_needed = csv_cleanup_needed
        self.similarity_group_min_size_threshold = similarity_group_min_size_threshold
        self.similarity_group_merging_dist_threshold = similarity_group_merging_dist_threshold
        self.expected_num_of_clusters = expected_num_of_clusters
        if dim:
            self.dim = dim
        else:
            raise Exception("You must supply a value for 'dim' which stand for data dimensionality")
        self.r = r                               # Number of rows in each band (each row is for one hash func)
        self.b = b                               # Number of bands.
        self.how_many_hashes =  r * b
        self._debug = debug
        self._data_dict = {}                     # sample_name =>  vector_of_floats extracted from CSV stored here
        self.how_many_data_samples = 0
        self.hash_store = {}                     # hyperplane =>  {'plus' => set(), 'minus'=> set()}
        self.htable_rows  = {}
        self.index_to_hplane_mapping = {}
        self.band_hash = {}                      # BitVector column =>  bucket for samples  (for the AND action)
        self.band_hash_mean_values = {}          # Store the mean of the bucket contents in band_hash dictionary
        self.similarity_group_mean_values = {}
        self.coalesced_band_hash = {}            # Coalesce those keys of self.band_hash that have data samples in common
        self.similarity_groups = []
        self.coalescence_merged_similarity_groups = []  # Is a list of sets
        self.l2norm_merged_similarity_groups = []  # Is a list of sets
        self.merged_similarity_groups = None
        self.pruned_similarity_groups = []
        self.evaluation_classes = {}             # Used for evaluation of clustering quality if data in particular format


    def get_data_from_csv(self):
        """monkey patch to deal with pandas"""
        data_dict = {}
        feature_names = self.datafile.columns.tolist()
        feature_names.remove('prop_id')
        for i in range(self.datafile.shape[0]):
            data_dict[self.datafile.iloc[i]['prop_id']] = self.datafile.iloc[i][feature_names].tolist()
        self.how_many_data_samples = i + 1
        self._data_dict = data_dict

    def lsh_basic_for_nearest_neighbors(self, properties):
        """patch to loop instead of interactive"""
        for (i,_) in enumerate(sorted(self.hash_store)):
            self.htable_rows[i] = BitVector(size = len(self._data_dict))
        for (i,hplane) in enumerate(sorted(self.hash_store)):
            self.index_to_hplane_mapping[i] = hplane
            for (j,sample) in enumerate(sorted(self._data_dict, key=lambda x: sample_index(x))):
                if sample in self.hash_store[hplane]['plus']:
                    self.htable_rows[i][j] =  1
                elif sample in self.hash_store[hplane]['minus']:
                    self.htable_rows[i][j] =  0
                else:
                    raise Exception("An untenable condition encountered")
        # for (i,_) in enumerate(sorted(self.hash_store)):
        #     if i % self.r == 0: print()
        #     print( str(self.htable_rows[i]) )
        for (k,sample) in enumerate(sorted(self._data_dict, key=lambda x: sample_index(x))):
            for band_index in range(self.b):
                bits_in_column_k = BitVector(bitlist = [self.htable_rows[i][k] for i in
                                                     range(band_index*self.r, (band_index+1)*self.r)])
                key_index = "band" + str(band_index) + " " + str(bits_in_column_k)
                if key_index not in self.band_hash:
                    self.band_hash[key_index] = set()
                    self.band_hash[key_index].add(sample)
                else:
                    self.band_hash[key_index].add(sample)
        if self._debug:
            print( "\n\nPre-Coalescence results:" )
            for key in sorted(self.band_hash, key=lambda x: band_hash_group_index(x)):
                print()
                print( "%s    =>   %s" % (key, str(self.band_hash[key])) )
        similarity_neighborhoods = {sample_name : set() for sample_name in
                                         sorted(self._data_dict.keys(), key=lambda x: sample_index(x))}
        for key in sorted(self.band_hash, key=lambda x: band_hash_group_index(x)):
            for sample_name in self.band_hash[key]:
                similarity_neighborhoods[sample_name].update( set(self.band_hash[key]) - set([sample_name]) )
        similar_results = []

        loop_ct = 0
        for prop in properties:
            loop_ct += 1
            print("finding lsh neighbors for property {}".format(prop))
            if loop_ct % 100 == 0:
                print("{}% complete".format((loop_ct*100.0)/len(properties)))
            other_props = similarity_neighborhoods[prop]
            ct = 0
            for oprop in other_props:
                ct += 1
                similar_results.append([prop, oprop, 1, ct, 'lsh'])

        df = pd.DataFrame(similar_results)
        df.columns = ['search_prop', 'sim_prop', 'sim_score', 'sim_rank', 'sim_metric']
        return df


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

def create_zip_map(features):
    """pre-partition by zip for fast lookup instead of repeated filter"""
    zip_map = {}
    for zipcode in features['situs_zip'].unique():
        try:
            zipcode = str(zipcode).replace('.0', '')
        except:
            pass
        zip_map[zipcode] = features[features['situs_zip'] == zipcode]

    return zip_map

def hamming(a, b, base_hood, cand_hood):
    a = str(a)
    b = str(b)
    assert len(a) == len(b)
    hamming_ct = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            hamming_ct += 1
    if base_hood != cand_hood:
        hamming_ct += 1
    return hamming_ct

def physical_dist(lat1, long1, lat2, long2):
    try:
        return geopy.distance.vincenty((lat1, long1), (lat2, long2,)).km
    except:
        return np.nan

def get_zip_to_zip():
    with open("data/adjacent_zips.json", "r") as f:
        data = json.load(f)
    return data

def clean_zips(df):
    df["situs_zip"] = df["situs_zip"].apply(lambda x: x.split('-')[0].replace(".0", ""))
    return df

def get_input_features():
    dtype_map = {
        'prop_id': np.object,
        'Address': np.object,
        'City': np.object,
        'State': np.object,
        'Lat': np.object,
        'Long': np.object,
        'geo_id': np.object,
        'hamming': np.object
    }
    features = clean_zips(pd.read_csv("data/input_feature_matrix.csv", dtype=dtype_map))
    return features

def get_processed_addresses(processed_addresses_path):
    if not os.path.isfile(processed_addresses_path):
        return set([])
    else:
        data = []
        with open(processed_addresses_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row[0])
        return set(data)

def flush(euclid_buffer, manhattan_buffer, adr_buffer, processed_file_name):
    e = pd.concat(euclid_buffer)
    m = pd.concat(manhattan_buffer)
    batch_id = str(uuid.uuid4())
    e.to_csv("euclid_{}.csv".format(batch_id), index=False)
    m.to_csv("manhattan_{}.csv".format(batch_id), index=False)

    s3 = boto3.resource('s3', region_name = 'us-west-2')
    bucket = s3.Bucket('dva-gatech-atx')
    bucket.upload_file('euclid_{}.csv'.format(batch_id), 'sim_results/euclid/euclid_{}.csv'.format(batch_id))
    bucket.upload_file('manhattan_{}.csv'.format(batch_id), 'sim_results/manhattan/manhattan_{}.csv'.format(batch_id))

    os.remove('euclid_{}.csv'.format(batch_id))
    os.remove('manhattan_{}.csv'.format(batch_id))

    if processed_file_name:
        with open(processed_file_name, 'a') as f:
            for adr in adr_buffer:
                f.write(str(adr))
                f.write('\n')

    return [], [], []


if __name__ == '__main__':
    mode = sys.argv[1]

    if mode == 'test':
        generate_test_scores()
    elif mode == 'euclidean_manhattan':
        features = get_input_features()
        base_cont_features = ["yr_built", "building_sqft", "land_sqft"]
        zillow_features = ["baths", "beds", "floorsize", "yearbuilt"]
        scaler = preprocessing.MinMaxScaler()
        features[base_cont_features + zillow_features] = scaler.fit_transform(features[base_cont_features + zillow_features])
        zip_map = create_zip_map(features)
        zip2zip = get_zip_to_zip()

        if len(sys.argv) > 3:
            processed_file_name = sys.argv[3]
            processed_addresses = get_processed_addresses(processed_file_name)
        else:
            processed_file_name = None
            processed_addresses = set([])

        ziperator = sys.argv[2].split(",") if len(sys.argv) > 2 else zip2zip  # option to pass arg
        for zipcode in ziperator:
            zip_features = features[features["situs_zip"] == zipcode].add_prefix("base_")
            possible_zips = [str(x) for x in zip2zip.get(zipcode)] + [zipcode]
            possible_matches = features[features['situs_zip'].isin(possible_zips)].add_prefix("cand_").reset_index()

            adr_buffer = []
            euclid_buffer = []
            manhattan_buffer = []
            for i in range(zip_features.shape[0]):
                start_time = time.time()
                prop = zip_features.iloc[i]
                prop_id = prop['base_prop_id']
                if prop_id in processed_addresses:
                    continue

                if i % 10 == 0 and i > 0:
                    euclid_buffer, manhattan_buffer, adr_buffer = flush(euclid_buffer, manhattan_buffer, adr_buffer, processed_file_name)

                print("processing property id {}".format(prop_id))
                prop_df = pd.concat([prop] * possible_matches.shape[0], axis=1).T.reset_index()
                pair_df = prop_df.merge(possible_matches, left_index=True, right_index=True)
                pair_df = pair_df[pair_df["base_prop_id"] != pair_df["cand_prop_id"]]
                pair_df["hamming_dist"] = pair_df.apply(lambda x: hamming(x["base_hamming"], x["cand_hamming"], x["base_hood_cd"], x["cand_hood_cd"]), axis=1)
                pair_df["physical_dist"] = pair_df.apply(lambda x: physical_dist(x["base_Lat"], x["base_Long"], x["cand_Lat"], x["cand_Long"]), axis=1)
                pair_df[["hamming_dist", "physical_dist"]] = pd.DataFrame(scaler.fit_transform(pair_df[["hamming_dist", "physical_dist"]]))

                feature_names = base_cont_features + zillow_features if prop['base_zillow'] == 1 else base_cont_features
                base_cont_matrix = pair_df[['base_{}'.format(x) for x in feature_names]]
                cand_cont_matrix = pair_df[['cand_{}'.format(x) for x in feature_names]]
                base_cont_matrix.columns = feature_names
                cand_cont_matrix.columns = feature_names
                pair_df["eudclid_diffs"] = np.sum(base_cont_matrix.subtract(cand_cont_matrix, fill_value=0)**2, axis=1)
                pair_df["manhattan_diffs"] = np.sum(base_cont_matrix.subtract(cand_cont_matrix, fill_value=0).abs(), axis=1)
                pair_df["eudclid_dist"] = np.sqrt(pair_df["eudclid_diffs"] + pair_df["hamming_dist"]**2 + pair_df["physical_dist"]**2)
                pair_df["manhattan_dist"] = pair_df["manhattan_diffs"] + pair_df["hamming_dist"] + pair_df["physical_dist"]
                end_time = time.time()
                print(end_time - start_time)

                euclid_df = pair_df[['base_prop_id', 'cand_prop_id', 'eudclid_dist']].sort_values(by='eudclid_dist')
                euclid_df.columns = ['search_prop', 'sim_prop', 'sim_score']
                euclid_df['sim_rank'] = euclid_df.reset_index().index + 1
                euclid_df['metric'] = 'euclidean'
                euclid_df = euclid_df.head(20)
                euclid_buffer.append(euclid_df)

                manhattan_df = pair_df[['base_prop_id', 'cand_prop_id', 'manhattan_dist']].sort_values(by='manhattan_dist')
                manhattan_df.columns = ['search_prop', 'sim_prop', 'sim_score']
                manhattan_df['sim_rank'] = manhattan_df.reset_index().index + 1
                manhattan_df['metric'] = 'manhattan'
                manhattan_df = manhattan_df.head(20)
                manhattan_buffer.append(manhattan_df)
        euclid_buffer, manhattan_buffer, adr_buffer = flush(euclid_buffer, manhattan_buffer, adr_buffer, processed_file_name)
    elif mode == 'lsh':
        # LSH does the encoding for us, so we can pull in raw feature values
        features = pd.read_csv("data/combined_feature_matrix.csv")
        fields_to_include = ["situs_zip", "prop_id", "Lat", "Long", "is_deliverable", "is_residential", "commercial_real_property",
                                "multifamily_residence", "single_family_residence", "rural_land,_non_qualified_open_space_land,_imprvs",
                                "tangible_other_personal,_mobile_homes", "improvements_on_qualified_open_space_land", "residential_inventory",
                                "electric_company_(including_co-op)", "industrial_and_manufacturing_real_property", "vacant_lots_and_land_tracts",
                                "water_systems", "telephone_company_(including_co-op)", "totally_exempt_property", "gas_distribution_system",
                                "qualified_open-space_land", "yr_built", "building_sqft", "has_outdoor_space", "has_garage", "has_pool",
                                "has_cenral_air", "has_fireplace", "land_sqft", "is_commercial", "is_ag", "is_mobile", "beds", "baths",
                                "floorsize", "has_carpet", "has_hardwood", "has_tile"]
        features = features[fields_to_include].fillna(-1)
        features["Lat"].replace(" USA",-1, inplace=True)  # replace stray bad value
        zip2zip = get_zip_to_zip()
        # standardize types for library
        for field in fields_to_include:
            if field not in ('prop_id', 'situs_zip'):
                features[field] = features[field].astype(float)

        ziperator = sys.argv[2].split(",") if len(sys.argv) > 2 else zip2zip  # option to pass arg
        for zipcode in ziperator:
            possible_zips = [str(x) for x in zip2zip.get(zipcode)] + [zipcode]
            possible_matches = features[features['situs_zip'].isin(possible_zips)]
            ids_to_find = list(possible_matches[possible_matches['situs_zip'] == zipcode]["prop_id"].unique())
            input_features = possible_matches
            del input_features['situs_zip']
            lsh = LSH(
               datafile = input_features,
               dim = input_features.shape[1]-1,
               r = 50,
               b = 100,
            )
            print("populating lsh data")
            lsh.get_data_from_csv()
            print("initializing hash store")
            lsh.initialize_hash_store()
            print("hashing all the data")
            lsh.hash_all_data()
            print("finding neighbors")
            lsh_df = lsh.lsh_basic_for_nearest_neighbors(ids_to_find)
            print("saving results")
            lsh_df.to_csv("lsh_results_{}.csv".format(zipcode), index=False)
    else:
        raise Exception("unexpected argument {}. values are `test`, `euclidean_manhattan`, and `lsh`".format(mode))
