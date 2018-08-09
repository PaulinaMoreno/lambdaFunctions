import boto3
import os
import json
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
identity = boto3.client('cognito-idp', region_name='us-west-2')

dynamodb = boto3.resource(
    'dynamodb', region_name='us-west-2'
)

def lambda_handler(event, context):
    if event['pathParameters']:
        user_id = event['pathParameters']['userID']
        friend_id = event['pathParameters']['friendID']
    else:
        user_id = event['queryStringParameters']['userID']
        friend_id = event['queryStringParameters']['friendID']
    # Create relation in Dynamodb Friend Table
    try:
        create_friend_relation(user_id, friend_id)
        
        response_body = {
            'userID': user_id,
            'friendID':friend_id
            
        }
        responseJson = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin" : "*"
        },
        "body": json.dumps(response_body)
         }
        return responseJson
    except ClientError as e:
        print("error lambda_handler")
        print(e)
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            error = {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin" : "*"
                },
                "body":'Friend Relation already exists'
            }
            return error
        else:
            error = {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin" : "*"
                },
                "body":'Unexpected error'   
            }
            return error
        
def create_friend_relation(userID, friendID):
        try:
            table = dynamodb.Table(os.environ['TABLE'])
            now = str(datetime.now())
            statusDate = "FRIENDS"
            response_user_to_friend = table.put_item(
                Item={
                'userID': userID,
                'friendID': friendID,
                'createdOn': now,
                'relationStatus': statusDate
                },
                ConditionExpression="attribute_not_exists(userID) AND attribute_not_exists(friendID)"
            )
            table.put_item(
                Item={
                'userID': friendID,
                'friendID': userID,
                'createdOn': now,
                'relationStatus': statusDate
                },
                ConditionExpression="attribute_not_exists(userID) AND attribute_not_exists(friendID)"
            )
            return response_user_to_friend
        except ClientError as e:
            raise e

