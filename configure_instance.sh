#!/bin/bash

# Install Python and pip
sudo apt-get update
sudo apt-get install -y python3 python3-pip

pip3 install boto3

#upload audio files application running
python3 upload_audio_files.py