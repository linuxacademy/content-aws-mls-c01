import boto3
import uuid
import json

def lambda_handler(event, context):

    print(json.dumps(event))

    record = event['Records'][0]

    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']

    s3Path = f's3://{s3bucket}/{s3object}'
    jobName = f'{s3object}-{str(uuid.uuid4())}'
    outputKey = f'transcripts/{s3object}-transcript.json'

    client = boto3.client('transcribe')

    response = client.start_transcription_job(
        TranscriptionJobName=jobName,
        LanguageCode='en-US',
        Media={'MediaFileUri': s3Path},
        OutputBucketName=s3bucket,
        OutputKey=outputKey
    )

    print(json.dumps(response, default=str))

    return {
        'TranscriptionJobName': response['TranscriptionJob']['TranscriptionJobName']
    }
