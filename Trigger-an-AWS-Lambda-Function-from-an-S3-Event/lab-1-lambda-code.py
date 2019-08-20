import boto3
import uuid
import json

def lambda_handler(event, context):

    print(json.dumps(event))

    record = event['Records'][0]
    
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    
    s3Path = "s3://" + s3bucket + "/" + s3object
    jobName = s3object + '-' + str(uuid.uuid4())

    client = boto3.client('transcribe')

    response = client.start_transcription_job(
        TranscriptionJobName=jobName,
        LanguageCode='en-US',
        MediaFormat='mp4',
        Media={
            'MediaFileUri': s3Path
        }
    )

    print(json.dumps(response, default=str))

    return {
        'TranscriptionJobName': response['TranscriptionJob']['TranscriptionJobName']
    }