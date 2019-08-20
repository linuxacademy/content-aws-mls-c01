import boto3

transcribe = boto3.client('transcribe')

def lambda_handler(event, context):
    
    payload = event['Input']['Payload']
    transcriptionJobName = payload['TranscriptionJobName']
    
    response = transcribe.get_transcription_job(
        TranscriptionJobName=transcriptionJobName
    )
    
    transcriptionJob = response['TranscriptionJob']
    
    transcriptFileUri = "none"
    if 'Transcript' in transcriptionJob:
        if 'TranscriptFileUri' in transcriptionJob['Transcript']:
            transcriptFileUri = transcriptionJob['Transcript']['TranscriptFileUri']
    
    return {
        'TranscriptFileUri': transcriptFileUri,
        'TranscriptionJobName': transcriptionJobName,
        'TranscriptionJobStatus': response['TranscriptionJob']['TranscriptionJobStatus']
    }