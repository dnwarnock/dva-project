#!/bin/sh

sudo apt-get update

wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/
rm gecko*.gz

sudo apt-get -y install firefox

sudo apt -y install python3-pip

aws s3 cp s3://dva-gatech-atx/proxies.csv .
aws s3 cp s3://dva-gatech-atx/requirements.txt .
aws s3 cp s3://dva-gatech-atx/selenium_scrape.py .

pip3 install -r requirements.txt

mkdir pics
