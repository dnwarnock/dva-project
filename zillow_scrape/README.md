# Overview
This project sub dir is all about scraping Zillow data. Unfortunately we had to use Selenium because Zillow renders lots of Javascript server side and seemed to block more lightweight browsers like Splash that tried to do this.

Here is a listing of the contents:
* `data/`: Helper data. Not checked in as things should be available in S3
* `venv/`: Virtual environment for Python 3. Not checked in, just create a new one with `requirements.txt`
* `adjacent_zips.csv`: A mapping of adjacent zip codes in Austin created manually using [this data source](https://www.zipmap.net/Texas/Travis_County/Austin.htm). Note edges are undirected.
* `dump_proxies.py`: A script to collect proxy servers for scraping to avoid throttling/blocking.
* `proxies.csv`: The results of `dump_proxies.py`
* `make_zillow_inputs.py`: Creates partitions of target properties and stores them in S3 so they can be used by the scraper. Assumes you have data from S3 available here: `s3://dva-gatech-atx/tcad/Cleaned\ data/CENTRAL_ATX_SUBSET.csv`.
* `requirements.txt`: Specifies the required dependencies for python. Usage: `pip install -r requirements.txt`
* `selenium_scrape.py`: The actual script that scrapes Zillow and dumps the results to S3.
* `setup.sh`: The script used to set up everything as required on the remote server.
* `etc/`: Misc. stuff. Mainly failed attempts to dockerize things.

# Running details:
Since browsers are memory hungry, we used AWS `r5.4xlarge` instance type and ran a process for each of the 23 targeted zip codes in a screen session on that server.
