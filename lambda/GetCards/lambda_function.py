import json
import boto3
from datetime import datetime

client = boto3.client('dynamodb')

def lambda_handler(event, context):

    username = event['requestContext']['authorizer']['claims']['cognito:username']

    last_session = get_last_session(username)
    
    try:
        data = client.query(
            TableName = 'Cards', 
            KeyConditionExpression= '#Username = :username', 
            ExpressionAttributeValues= {
                ':username': {'S': username}
            },
            ExpressionAttributeNames={
            '#Username': 'Username'
            }
        )
    except ClientError as err:
        return error_response(err.response['Error']['Message'])
    
    for card in data["Items"]:
        for key in card.keys():
             card[key] = deserialize(card[key])
  
    data["Items"].sort(key=lambda card: card["RequestTime"])
    
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(data)
    }

def get_last_session(username):
    last_session = datetime.min
    
    data = client.get_item(TableName = 'SessionStatus', Key = {
        'Username': {'S': username}
    })
        
    if "Item" in data:
        last_session = deserialize(data['Item']['LastSession'])
    else:
        client.put_item(TableName = 'SessionStatus', Item = {
            'Username': { 'S': username},
            'LastSession': {'S': last_session.strftime('%Y-%m-%dT%H:%M:%SZ')},
            'SessionNum': {'N': '1'}    
        })
        
    return last_session
   

def error_response(error_message):
    return {
        'statusCode': 500,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'Error': error_message})
    }

# ran into problems with boto3's TypeDeserializer incorrectly deserializing integers
def deserialize(dict):
    return list(dict.values())[0]