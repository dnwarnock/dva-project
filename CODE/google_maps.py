import pandas as pd
import googlemaps

from tqdm import tqdm

data_dir = "/Users/dnw000c/Downloads/CENTRAL_ATX_SUBSET_Dylan.csv"

gmaps = googlemaps.Client(key='Your API KEY')
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

df.to_csv(path_or_buf='/Users/dnw000c/Desktop/geocode_output.csv')
