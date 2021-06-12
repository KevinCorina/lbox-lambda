import json
import boto3
from datetime import datetime
import dateutil.parser

client = boto3.client('dynamodb')

def lambda_handler(event, context):

    username = event['requestContext']['authorizer']['claims']['cognito:username']
    last_session = datetime.min
    session_num = 1
    session_data = client.get_item(TableName = 'SessionStatus', Key = {
        'Username': {'S': username}
    })
        
    if "Item" in session_data:
        last_session = dateutil.parser.parse(deserialize(session_data['Item']['LastSession']))
        last_session = last_session.replace(tzinfo=None)
        
        if ((datetime.now() - last_session).total_seconds() < 60*60*6):
            for key in session_data["Item"].keys():
                session_data["Item"][key] = deserialize(session_data["Item"][key])
  
            session_data['CanQuiz'] = False
            
            return {
                'statusCode': 200,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(session_data)
            }
            
        session_num = int(deserialize(session_data["Item"]["SessionNum"]))
        
    else:
        client.put_item(TableName = 'SessionStatus', Item = {
            'Username': { 'S': username},
            'LastSession': {'S': last_session.strftime('%Y-%m-%dT%H:%M:%SZ')},
            'SessionNum': {'N': '1'}    
        })
        
    
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
        
        
        for card in data["Items"]:
            for key in card.keys():
                card[key] = deserialize(card[key])
        
        data['Items'].sort(key=lambda card: card["RequestTime"])
        data['Item'] = {'LastSession': last_session.strftime('%Y-%m-%dT%H:%M:%SZ')}
        data['CanQuiz'] = True
        levels = [1, 2, 3, 4, 5, 6, 7];
        levels = list(filter(lambda val: session_num % val == 0, levels))
        data['Levels'] = levels
        data["Items"] = list(filter(lambda card: int(card["ProficiencyLevel"]) in levels, data["Items"]))
        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(data)
        }
            
    except ClientError as err:
        return error_response(err.response['Error']['Message'])
    
  


def error_response(error_message):
    return {
        'statusCode': 500,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'Error': error_message})
    }

# ran into problems with boto3's TypeDeserializer incorrectly deserializing integers
def deserialize(dict):
    return list(dict.values())[0]