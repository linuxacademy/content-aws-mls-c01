import boto3

def lambda_handler(event, context):
    
    rekognition = boto3.client('rekognition')
    
    response = rekognition.recognize_celebrities(
        Image={
            'S3Object': {
                'Bucket': 'ai-tests-ygiuhjknasd',
                'Name': 'famous.jpg'
            }
        }
    )
    
    people = []
    
    for face in response['CelebrityFaces']:

        info = rekognition.get_celebrity_info(
            Id=face['Id']
        )

        people.append([face['Name'], info['Urls']])
    
    return {
        'statusCode': 200,
        'body': people
    }
