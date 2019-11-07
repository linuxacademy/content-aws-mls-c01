import boto3

def lambda_handler(event, context):
    
    rekognition = boto3.client('rekognition')
    
    response = rekognition.detect_text(
        Image={
            'S3Object': {
                'Bucket': 'xxxxxxx',
                'Name': 'xxxxxxx'
            }
        }
    )
    
    text = ''
    
    for detection in response['TextDetections']:
        if detection['Type'] == "WORD":
            text = text + ' ' + detection['DetectedText']
    
    return {
        'statusCode': 200,
        'body': text.strip()
    }
