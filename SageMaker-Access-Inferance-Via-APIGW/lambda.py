import json, boto3
import base64, binascii
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    
    client = boto3.client('sagemaker-runtime')
    
    body = base64.b64decode(event['body'])
    
    try:
        response = client.invoke_endpoint(
            EndpointName='pinehead',
            Body=body,
            ContentType='application/x-image'
        )
        
        # The 'Body' of the response is a StreamingBody() so we need to 'read' it,
        # and decode it, to get the float values.
        payload = response['Body']
        output = payload.read()
        string = output.decode("utf-8")
        string = string[1:-1]
        values = string.split(",")
        
        # Then we can compare to see which float is the greatest:
        if (float(values[0]) > float(values[1])):
            ret = "Not Pinehead"
        else:
            ret = "Pinehead"
        
    except ClientError as e:
        ret = ("Error: %s" % e)
        
    return {
        'statusCode': 200,
        'body': json.dumps(ret, default=str)
    }