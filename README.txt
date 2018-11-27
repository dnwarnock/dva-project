# Overview
This project contains all of the code necessary to repeat Team 33's housing similarity analysis and application done for Data & Visual Analytics in Fall 2018. The code is broken apart in 4 modules `googlemaps_scrape`, `zillow_scrape`, `similarity`, and `app`, each of which are discussed in more detail below. A more detailed README is also provided within each sub directory. This document is intended to provide a high-level overview of the modules and the basic necessities to get them to run.

Additional resources not checked in such as the data acquired from the Travis County Appraisal District (TCAD) are available in a public bucket in S3 (s3://dva-gatech-atx/), which is available in the `us-west-2` region. These resources should be available through 2018, but might be removed at some point in the future to minimize personal hosting costs.

# googlemaps_scrape
## Description
This module contains a script that is used to pull coordinates of addresses from the TCAD data and store the results in S3. Note that google maps API is free up to a limited number of API requests. For more information, read here: https://cloud.google.com/maps-platform/pricing/.

## Installation
1. Have installed and configured the [awscli](https://aws.amazon.com/cli/)
2. Have python3 installed (tested with 3.6.5)
3. Have pip3 installed
4. [Get an API Key for Google Maps](https://developers.google.com/maps/documentation/javascript/get-api-key)
5. Set an environment variable named `GOOGLE_MAPS_API_KEY` to your API key. On POSIX-based systems `export GOOGLE_MAPS_API_KEY = {YOUR_API_KEY_HERE}`

## Execution
1. `pip3 -r requirements.txt` - install python dependencies
2. `python3 google_maps.py`

# zillow_scrape
## Description
This module was used to scrape data from zillow.com property listings. This uses a list of addresses pulled from the TCAD data to search for the appropriate Zillow.com listing and pull additional features not in the TCAD data such as the number of bedrooms and bathrooms. We use selenium since much of Zillow's pages are rendered via javascript client-side.

## Installation
1. Have installed and configured the awscli (https://aws.amazon.com/cli/)
2. Have python3 installed (tested with 3.6.5) (https://www.python.org/downloads/release/python-365/)
3. Have pip3 installed
    * Mac: brew install python3
    * Linux (Ubuntu): sudo apt install python3-pip
4. Have the latest version of Firefox installed (https://www.mozilla.org/en-US/firefox/new/)
5. Have the latest version of geckodriver installed (https://github.com/mozilla/geckodriver/releases)

## Execution
1. `pip3 -r requirements.txt` - install python dependencies
2. `python3 selenium_scrape.py {address_file} {s3_path} {processed_adr_file}` where
    * `address_file` is path to a local file produced by `make_zillow_inputs.py`
    * `s3_path` is the output path in s3 where you'd like part files to be uploaded
    * `processed_adr_file` is the path to a local csv used to tracking which properties have already been scraped in case you need to restart.

Note: you can run `python3 dump_proxies.py` to create a new `proxies.csv` file if these are no longer working. Additionally, the input files should be staged in S3, but if you'd like to point to a new bucket or repopulate, you may do so by running `python3 make_zillow_inputs.py`

A more detailed readme about this module is available at `./zillow_scrape/README.md`

# similarity
## Description
This module was used to combine data from our various raw sources (TCAD, GoogleMaps, and Zillow) and create a feature matrix that can be used for property similarity scoring, actually performing the scoring for euclidean, manhattan, and locality sensitive hashing (LSH), and outputting the results in a format that can be loaded into the application database.

## Installation
1. Have installed and configured the awscli (https://aws.amazon.com/cli/)
2. Have python3 installed (tested with 3.6.5) (https://www.python.org/downloads/release/python-365/)
3. Have pip3 installed
    * Mac: brew install python3
    * Linux (Ubuntu): sudo apt install python3-pip

## Execution
1. `pip3 -r requirements.txt` - install python dependencies
2. `python3 prepare_data.py all` - pull input data and prepare feature matrices
3. `python3 calc_similarity_scores.py euclidean_manhattan` - calc euclidean and manhattan distances
4. `python3 calc_similarity_scores.py lsh` - calc lsh neighbors
5. `python3 combine_scores.py all` - union part files and upload to s3
6. `python3 transform_data.py all` - jsonify and rename for input to application db

A more detailed readme about this module is available at `./similarity/README.md`

# app
## Description
This module contains the code for the actual web application used to present the results to end users. This application primarily relies on 3 technologies, MongoDB, Node.js, and Vue.js. It allows users to search for a property and automatically lists similar properties, along with exportable summary statistics. It is broken into two subdirectories `frontend`, which contains the client-side javascript, html, etc., and `backend` which contains the node application and mongo database.

## Installation
1. Must use linux or OSX
2. install docker (https://docs.docker.com/docker-for-mac/install/)
3. install docker-compose (https://docs.docker.com/compose/install/)
4. Build the backend with `cd backend && docker build -t dva-backend:local . && cd ..`
5. Build the frontend with `cd frontend && docker build -t dva-frontend:local . && cd ..`
6. Get an API Key for Google Maps (https://developers.google.com/maps/documentation/javascript/get-api-key)
7. Copy and paste your API Key on to line 12 of `frontend/src/main.js` in the value slot for the `key`
8. Place your seed json files in the root directory of the project with the name `application_data.json`
9. run `mkdir backend/mongo` in the root directory of the project
10. seed mongo by running `setup.sh`

## Execution
1. Start the application by running `docker-compose up` from the root directory of the project
2. Visit `http://0.0.0.0:8080/` in a web browsers (preferably firefox or chrome)
3. Type an address into the search bar and click on the address that matches the one you are interested in
4. A table will be populated with similar properties that could be used in an appraisal dispute
5. These properties will also be dotted on the map visible to the left of the table
6. Clicking the export button will allow users to download their search results as a csv

A more detailed readme about this module is available at `./app/README.md`
