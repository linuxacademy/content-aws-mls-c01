import boto3

transcribe_client = boto3.client('transcribe')

def lambda_handler(event, context):
    #Retrieve the state information
    step_state = event['Input']['Payload']
    transcriptionJobName = step_state['TranscriptionJobName']

    #Check the Transcribe status
    response = transcribe_client.get_transcription_job(
        TranscriptionJobName=transcriptionJobName
    )

    #Add the Transcribe job status back to the state
    step_state['TranscriptionJobStatus'] = response['TranscriptionJob']['TranscriptionJobStatus']

    return step_state
