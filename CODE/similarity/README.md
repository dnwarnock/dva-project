# Overview
This directory contains the work done to extract the features and calculate the similarity between properties.

The high-level process is as follows:
### Part 1:
1. Pull TCAD, Zillow, and Geocoding data down from S3.
2. Consolidate each data source into a matrix at property-level granularity with the desired features from each.
3. Merge the matrices for a master feature matrix and save

### Part 2:
1. Feed the features matrix along with the list of adjacent zip codes to the scoring engine.
2. If zillow features are available for a property use them in the calculation, otherwise only use TCAD features
3. Dump part files with the similarity results
4. Combine part files for overall tables

### Part 3:
1. Concatenate all TCAD years so we can provide historical data in the application

# Prerequisites
1. Have installed and configured the [awscli](https://aws.amazon.com/cli/)
2. Have python3 installed (tested with 3.6.5)
3. Have pip3 installed

# Models & Metrics
We build 2 types of models with 3 similarity metrics each.

The "fallback" model is one that is just based on TCAD data, while the "primary" model uses both TCAD and Zillow data. This is done because while we could scrape some Zillow data, Zillow had formidable obstacles to scraping at scale, even when distributing across 20 machines and using proxy ips and requesting properties at a slow rate. Thus, we use the "primary" model when zillow data is available for a property and the "fallback" data when it is not. Zillow also simply doesn't have data for some properties contained in the TCA data.

Three similarity metrics are used for each:
1. Euclidean distance w/ hamming preprocessing for categorical features
2. Manhattan distance w/ hamming preprocessing for categorical features
3. Locality Sensitive Hashing (LSH)

Hamming preprocessing for categorical features refers to taking all discrete features, making them booleans and combining them into a bit array. We then calculate the hamming distance between any property pair and feed the resulting hamming distance along with other continuous features to the euclidean and manhattan calculations, respectively.

# Installation & running
1. `pip3 -r requirements.txt` - install python dependencies
2. `python3 prepare_data.py all` - pull input data and prepare feature matrices
3. `python3 calc_similarity_scores.py euclidean_manhattan` - calc euclidean and manhattan distances
4. `python3 calc_similarity_scores.py lsh` - calc lsh neighbors
5. `python3 combine_scores.py all` - union part files and upload to s3
6. `python3 transform_data.py all` - jsonify and rename for input to application db
