# Overview
This directory contains the work done to extract the features and calculate the similarity between properties.

The high-level process is as follows:
###Part 1:
1. Pull TCAD, Zillow, and Geocoding data down from S3.
2. Consolidate each data source into a matrix at property-level granualrity with the desired features from each.
3. Merge the matricies for a master feature matrix and save

###Part 2:
1. Feed the features matrix along with the list of adjacent zip code to the scoring engine.
2. If zillow features are available for a property use them in the calculation, otherwise only use TCAD features
3. Dump part files with the similarity results
4. Combine part files for overall tables

###Part 3:
1. Concatenate all TCAD years so we can provide historical data in the application

# Prerequisites
1. Have installed and configured the [awscli](https://aws.amazon.com/cli/)

# Models & Metrics
We build 2 types of models with 3 similarity metrics each.

The "fallback" model is one that is just based on TCAD data, while the "primary" model uses both TCAD and Zillow data. This is done because while we could scrape some Zillow data, Zillow had formidable obstacles to scraping at scale, even when distributing across 20 machines and using proxy ips and requesting properties at a slow rate. Thus, we use the "primary" model when zillow data is available for a property and the "fallback" data when it is not. Zillow also simply doesn't have data for some properties contained in the TCA data.

Three similarity metrics are used for each:
1. Euclidean distance w/ hamming preprocessing for categorical features
2. Manhattan distnace w/ hamming preprocessing for categorical features
3. Locality Sensitve Hashing (LSH)

Hamming preprocessing for categorical features refers to taking all discrete features, making them booleans and combining them into a bit array. We then calculate the hamming distance between any property pair and feed the resulting hamming distance along with other continuous features to the euclidean and manhattan calculations, respectively.

# Features
| Feature Name | Source | Type | Description|
|--------------|--------|------|------------|
|Lot size      | TCAD | Continuous | The size of the land for the property in square feet |
|Building size | TCAD | Continuous | The size of the building on the property in square feet |
|Year built    | TCAD
|is_mobile     | TCAD | Discrete | And indicator whether the home is a mobile home
|beds          | Zillow | Continuous | The number of bedrooms in the home |
|baths         | Zillow | Continuous | The number of bathrooms in the home |
| distance between | GoogleMaps | Continuous | Calculate based on coordinates at run time |


* there are duplicates in the files eric produced



PROP.TXT
- prop_id
- prop_type_cd
- geo_id
- py_addr_ml_deliverable

LAND_DET.TXT
- prop_id
- land_type_desc
- size_square_feet
- mkt_ls_class
- ag_apply
- land_homesite_pct

IMT_DET.TXT
- Imprv_det_type_desc (key features)
- yr_built (min for whole property)
- imprv_det_area (if type_desc contains floor then sum is liveable area)

STATE_CD.TXT


if contains floor sum imp area to get


physical distance * euclidean distance * manhattan distance




