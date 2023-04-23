import json
import boto3
import time

transcribe = boto3.client('transcribe')
comprehend = boto3.client('comprehend')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        # Extract relevant details from the SQS message
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        # Start a transcription job
        job_name = f"TranscriptionJob-{int(time.time())}"
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode='en-US',
            MediaFormat='mp3',
            Media={
                'MediaFileUri': f's3://{bucket_name}/{object_key}'
            },
            OutputBucketName=bucket_name
        )

        # Wait for the transcription job to complete
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(10)

        # If the transcription job completed successfully, process the results
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_file_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            transcript_json = s3.get_object(Bucket=bucket_name, Key=transcript_file_uri.split('/')[-1])['Body'].read()
            transcript_text = json.loads(transcript_json)['results']['transcripts'][0]['transcript']

            # Detect PII using the Comprehend service
            pii_response = comprehend.detect_pii_entities(
                Text=transcript_text,
                LanguageCode='en'
            )

            # Extract and return PII entities
            pii_entities = pii_response['Entities']
            print(f"PII entities detected: {pii_entities}")

        else:
            print(f"Transcription job failed: {status['TranscriptionJob']['FailureReason']}")
