import boto3
import time
import os

# Create an S3 client
s3 = boto3.client('s3')

# local path of the audio files to be uploaded
audio_files_path = './audio_files'

# Set the S3 bucket name
bucket_name = '1919196-s3'

for audio_file in os.listdir(audio_files_path):
    audio_file_path = os.path.join(audio_files_path, audio_file)
    s3.upload_file(audio_file_path, bucket_name, audio_file)
    print(f'Uploaded {audio_file} to S3 bucket {bucket_name}')
    time.sleep(30)