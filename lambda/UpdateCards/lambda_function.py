import json
import boto3
from datetime import datetime

client = boto3.client('dynamodb')

def lambda_handler(event, context):

    username = event['requestContext']['authorizer']['claims']['cognito:username']
    body =  json.loads(event['body'])
    
    for card in body:
        card['ProficiencyLevel'] = int(card['ProficiencyLevel'])
        if card["GotRight"]: 
            card['ProficiencyLevel'] += 1
        else:
            card['ProficiencyLevel'] = 1; 
        client.update_item(
            TableName = 'Cards',
            Key = {
                'CardId': {'S': card["CardId"]},
                'Username': {'S': username}
            },
            UpdateExpression = 'SET ProficiencyLevel = :proficiencyLevel',
            ExpressionAttributeValues={
                ':proficiencyLevel': {'N': str(card["ProficiencyLevel"])}
            }
        );
            
    session_num = 1
    
    session_data = client.get_item(TableName = 'SessionStatus', Key = {
        'Username': {'S': username}
    })
    if "Item" in session_data:
        session_num = int(deserialize(session_data["Item"]["SessionNum"])) + 1
        if session_num >= 64:
            session_num = 1
    
    last_session = datetime.now()
    client.put_item(TableName = 'SessionStatus', Item = {
            'Username': { 'S': username},
            'LastSession': {'S': last_session.strftime('%Y-%m-%dT%H:%M:%SZ')},
            'SessionNum': {'N': str(session_num)}    
        }
    )
    
    return {
        'statusCode': 201,
        'body': json.dumps('Success'),
        'headers': {
            'Access-Control-Allow-Origin': '*',
        }
    }


def deserialize(dict):
    return list(dict.values())[0]