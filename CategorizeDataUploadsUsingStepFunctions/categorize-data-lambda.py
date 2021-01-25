import boto3
import json
import os
import uuid
from datetime import date

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    #Retrieve the state information
    step_state = event['Input']['Payload']

    #Get the S3 information for the audio file and transcript
    s3_bucket = step_state['s3_bucket']
    s3_audio_key = step_state['s3_audio_key']
    s3_transcript_key = step_state['transcript_key']

    base_audio_key = os.path.basename(s3_audio_key)
    base_transcript_key = os.path.basename(s3_transcript_key)

    #Retrieve the transcript from S3
    download_path = f'/tmp/{base_transcript_key}-{uuid.uuid4()}'
    s3_client.download_file(s3_bucket, s3_transcript_key, download_path)
    with open(download_path,'r') as local_transcript:
        transcribe_result = json.loads(local_transcript.read())
    transcripts = transcribe_result['results']['transcripts']

    #Test if the transcript contains any of our special words
    keywords = os.getenv('KEYWORDS').split(',')
    contains_keyword = False
    for transcript_obj in transcripts:
        for keyword in keywords:
            if keyword in transcript_obj['transcript']:
                contains_keyword = True
                break
        if contains_keyword:
            break

    #Set file destination location.
    #By default, they should be placed in the processed/ folder.
    #If any of the keywords were found, move them to the important/ folder instead.
    #Date should be in YYYY/MM/DD format.
    output_date = date.today().strftime('%Y/%m/%d')
    output_folder = 'important' if contains_keyword else 'processed'

    output_loc = f'{output_folder}/{output_date}'

    #Move the audio and transcript. This requires a copy then a delete.
    #s3_client.copy_object
    #s3_client.delete_objects
    s3_client.copy_object(Bucket=s3_bucket,
                Key=f'{output_loc}/{base_audio_key}',
                CopySource={'Bucket': s3_bucket, 'Key': s3_audio_key}
    )
    s3_client.copy_object(Bucket=s3_bucket,
                Key=f'{output_loc}/{base_transcript_key}',
                CopySource={'Bucket': s3_bucket, 'Key': s3_transcript_key}
    )

    deletes = {'Objects': [{'Key': s3_audio_key}, {'Key': s3_transcript_key}]}
    s3_client.delete_objects(Bucket=s3_bucket, Delete=deletes)

    #Add the output folder to the state
    step_state['output_folder'] = output_folder

    return step_state
