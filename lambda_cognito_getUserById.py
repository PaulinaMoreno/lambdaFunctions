import boto3
import os
import json
import sys
import datetime
from botocore.exceptions import ClientError
from botocore.errorfactory import BaseClientExceptions
from os.path import dirname, join
from UsersModel import User

identity = boto3.client('cognito-idp', region_name='us-west-2')

def lambda_handler(event, context):
    if event['pathParameters']:
        user_id = event['pathParameters']['userID']
    if event['queryStringParameters']:
        user_id = event['queryStringParameters']['userID']
    else:
        error = {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin" : "*"
            },
                "body": 'Not found'
        }
        return error
        
    # fetch user from the cognito
    try:
        response = get_user_by_id(user_id)
        responseJson = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin" : "*"
         },
        "body": json.dumps(response.serialize())
         }
        return responseJson
    except ClientError as e:
        print("error lambda_handler")
        print(e)
        if 'UserNotFoundException' in str(e.response):
            error = {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin" : "*"
                },
                "body": 'User not found'
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

def get_user_by_id(username):
    try:
        user_cognito = identity.admin_get_user(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username=username
        )
        user_id = user_cognito['Username']
        enabled = user_cognito['Enabled']
        user_create_date = datetime_handler(user_cognito['UserCreateDate'])
        user_status = user_cognito['UserStatus']
        attributes = user_cognito['UserAttributes']

        for att in attributes:
            if att['Name'] == 'email':
                email = att['Value']
            if att['Name'] == 'phone_number':
                phone = att['Value']
        user_found = create_user(
            user_id, email, enabled, user_create_date, user_status, phone)
        return user_found
    except ClientError as e:
        print(e)
        raise e

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def create_user(user_id, email, enabled, user_create_date, user_status, phone):
    user = User()
    user.userID = user_id
    user.email = email
    user.enabled = enabled
    user.userCreateDate = user_create_date
    user.userStatus = user_status
    user.phone = phone
    return user
