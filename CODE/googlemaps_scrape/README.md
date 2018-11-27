# Overview
This module pulls coordinates from google maps for a list of addresses.

# Prerequisites
1. Have installed and configured the [awscli](https://aws.amazon.com/cli/)
2. Have python3 installed (tested with 3.6.5)
3. Have pip3 installed
4. [Get an API Key for Google Maps](https://developers.google.com/maps/documentation/javascript/get-api-key)
5. Set an environment variable named `GOOGLE_MAPS_API_KEY` to your API key. On POSIX-based systems `export GOOGLE_MAPS_API_KEY = {YOUR_API_KEY_HERE}`

# Installation & running
1. `pip3 -r requirements.txt` - install python dependencies
2. `python3 google_maps.py`
