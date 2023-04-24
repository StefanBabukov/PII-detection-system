import boto3
import time
import os

# Create an S3 client
s3 = boto3.client('s3')

# local path of the audio files to be uploaded
audio_files_path = './audio_files'

# Set the S3 bucket name
bucket_name = '1919196-s3'

while True:
    try:
        current_audio_file = os.listdir(audio_files_path)[0]
        audio_file_path = os.path.join(audio_files_path, current_audio_file)
        s3.upload_file(audio_file_path, bucket_name, f'transcribe/{current_audio_file}')
        print(f'Uploaded {current_audio_file} to S3 bucket {bucket_name}')

        # Delete the file after uploading
        os.remove(audio_file_path)
        print(f'Deleted {current_audio_file} from local folder')
    except IndexError as e:
        print('No new file in audio files folder.')

    # Wait for 30 seconds before checking the folder again
    time.sleep(30)