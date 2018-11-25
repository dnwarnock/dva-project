# Overview
This module is all about scraping Zillow data. Unfortunately we had to use Selenium because Zillow renders lots of Javascript client-side and seemed to block more lightweight browsers like Splash that tried to do this. Due to slow page rendering, and scraping defenses Zillow has in place, we partitioned the data by zip code and ran a scraper for each zip code from different servers and used proxies in an attempt to avoid AWS ip range blacklists. Thus, the setup as described here assumes you are running a single zip code on a AWS EC2 machine, although you should be able to run from arbitrary servers, and could combine across zip codes with minimal modification if desired.

Here is a listing of the contents:
* `adjacent_zips.csv`: A mapping of adjacent zip codes in Austin created manually using [this data source](https://www.zipmap.net/Texas/Travis_County/Austin.htm). Note edges are undirected.
* `dump_proxies.py`: A script to collect proxy servers for scraping to avoid throttling/blocking.
* `proxies.csv`: The results of `dump_proxies.py`
* `make_zillow_inputs.py`: Creates partitions of target properties and stores them in S3 so they can be used by the scraper. Assumes you have data from S3 available here: `s3://dva-gatech-atx/tcad/Cleaned\ data/CENTRAL_ATX_SUBSET.csv`.
* `requirements.txt`: Specifies the required dependencies for python. Usage: `pip install -r requirements.txt`
* `selenium_scrape.py`: The actual script that scrapes Zillow and dumps the results to S3.
* `setup.sh`: The script used to set up everything as required on the remote server.

# Prerequisites
1. Have installed and configured the [awscli](https://aws.amazon.com/cli/)
2. Have python3 installed (tested with 3.6.5)
3. Have pip3 installed
4. Have the latest version of Firefox installed
5. Have the latest version of geckodriver installed

* Assuming you are running on a Linux Ubuntu distribution, you should be able to achieve most of this by running `setup.sh`

# Installation & running
1. `pip3 -r requirements.txt` - install python dependencies
2. `python3 selenium_scrape.py {address_file} {s3_path} {processed_adr_file}` where
    * `address_file` is path to a local file produced by `make_zillow_inputs.py`
    * `s3_path` is the output path in s3 where you'd like part files to be uploaded
    * `processed_adr_file` is the path to a local csv used to tracking which properties have already been scraped in case you need to restart.

Note: you can run `python3 dump_proxies.py` to create a new `proxies.csv` file if these are no longer working. Additionally, the input files should be staged in S3, but if you'd like to point to a new bucket or repopulate, you may do so by running `python3 make_zillow_inputs.py`