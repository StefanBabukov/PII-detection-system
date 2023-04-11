#!/bin/bash

# Install Python and pip
sudo yum update
sudo yum install -y python3 python3-pip

pip3 install boto3

#upload audio files application running
python3 upload_to_s3.py