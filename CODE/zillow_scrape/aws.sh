#!/bin/sh

sudo apt-get update

sudo apt -y  install awscli

aws configure
# interactive - provide keys

aws s3 cp s3://dva-gatech-atx/setup.sh .

sh setup.sh
