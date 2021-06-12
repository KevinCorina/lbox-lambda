import json
import boto3
import secrets
from datetime import datetime

client = boto3.client('dynamodb')

def lambda_handler(event, context):

    username = event['requestContext']['authorizer']['claims']['cognito:username']
    card_id = secrets.token_urlsafe(16)
    card_data = json.loads(event['body'])["Card"]
    front = card_data['Front']
    back = card_data['Back']
    request_time = datetime.now()
    
    try:
        client.put_item(
            TableName = 'Cards',
            Item={
                'CardId': {'S': card_id},
                'Username': {'S': username},
                'Front': {'S': front},
                'Back': {'S': back},
                'ProficiencyLevel': {'N': '1'},
                'RequestTime': {'S': request_time.strftime('%Y-%m-%dT%H:%M:%SZ') }
            })
    except ClientError as err:
        return error_response(err.response['Error']['Message'])
    
    return {
        'statusCode': 201,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
                'CardId': card_id,
                'Front': front,
                'Back': back,
                'ProficiencyLevel': '1',
            })
        }


def error_response(error_message):
    return {
        'statusCode': 500,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'Error': error_message})
    }
