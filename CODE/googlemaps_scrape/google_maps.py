import os
import boto3
import googlemaps
import pandas as pd
from tqdm import tqdm
from subprocess import check_call


s3 = boto3.resource('s3', region_name = 'us-west-2')
bucket = s3.Bucket('dva-gatech-atx')

if not os.path.isdir('data'):
    os.mkdir('data')

if not os.path.isfile('data/CENTRAL_ATX_SUBSET.csv'):
    bucket.download_file('tcad/Cleaned_data/CENTRAL_ATX_SUBSET.csv', 'data/CENTRAL_ATX_SUBSET.csv')

data_dir = "data/CENTRAL_ATX_SUBSET.csv"

gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])
df = pd.read_csv(data_dir , header = 0, dtype = str)
df['lat'] = 0.0
df['lng'] = 0.0

for index, row in tqdm(df.iterrows(), total=df.shape[0]):
  try:
    result = gmaps.geocode(df['prop_address'][index])
    lat = result[0].get('geometry').get('location').get('lat')
    lng = result[0].get('geometry').get('location').get('lng')
    df.at[index, "lat"] = lat
    df.at[index, "lng"] = lng
  except Exception as ex:
    print(ex)

df.to_csv('GeoData.csv')
bucket.upload_file('GeoData.csv', 'googlemaps/GeoData.csv')
