import boto3
import os
import json

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    input = {
        "Bucket" : bucket,
        "Key": key
    }
    
    response = stepfunctions.start_execution(
        stateMachineArn=os.environ['STATEMACHINEARN'],
        input=json.dumps(input, default=str)
    )
    
    return json.dumps(response, default=str)