import json
import boto3

client = boto3.client('dynamodb')

def lambda_handler(event, context):
    
    username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
    card_id = event["queryStringParameters"]["CardId"]
    
    try:
        response = client.delete_item(TableName = 'Cards', Key = {
            'CardId': {'S': card_id},
            'Username': {'S': username}
        })
    except ClientError as err:
        return error_response(err.response['Error']['Message'])
    
    return {
        'statusCode': 201,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps("deleted item")
    }

def error_response(error_message):
    return {
        'statusCode': 500,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'Error': error_message})
    }

