import boto3
import os
import json
import sys
import time
from botocore.exceptions import ClientError
from botocore.errorfactory import BaseClientExceptions
from os.path import dirname, join

identity = boto3.client('cognito-idp', region_name='us-west-2')
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')


def lambda_handler(event, context):
    data = {}
    userID = None
    response = ''
    print(event)
    if event['pathParameters']:
        userID = event['pathParameters']['userID']
    if event['queryStringParameters']:
        userID = event['pathParameters']['userID']

    if event['body']:
        body_data = json.loads(event['body'])
        for paramether in body_data['attributes']:
            data[paramether] = body_data['attributes'][paramether]
        UserAttributes = buildUserAtt(data)
        cognito_response = update_user_cognito(userID, UserAttributes)
        if cognito_response['statusCode'] == 200:
            dynamodb_response = update_user_dynamodb(userID, data)
            print(dynamodb_response)
            if dynamodb_response['statusCode'] == 200:
                return cognito_response
            else:
                response = {
                    "statusCode": 500,
                    "headers": {
                            "Access-Control-Allow-Origin" : "*"
                        },
                    "body": 'Internal server error.'
                }
                return response
        else:
            return cognito_response
         
    else:
        response = {
            "statusCode": 404,
            "headers": {
                "Access-Control-Allow-Origin" : "*"
            },
            "body": 'Not found'
            }
        return response


def update_user_cognito(userID, UserAttributes):

    try:
        response = identity.admin_update_user_attributes(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username=userID,
            UserAttributes=UserAttributes
        )

        responseJson = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin" : "*"
            },
            "body": 'User ' + userID + ' update'
            }
        return responseJson
    except ClientError as e:
        if 'UserNotFoundException' in str(e.response):
            error = {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin" : "*"
                },
                "body": 'User not found'
            }
            return error
        else:
            error = {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin" : "*"
                },
                "body": str(e.response['Error']['Message'])
            }
            print(error)
            return error


def buildUserAtt(data):
    user_att = []
    exp = {}
    for key, value in data.items():
        exp['Name'] = '{}'.format(key)
        exp['Value'] = value
        user_att.append(exp)
        exp = {}
    return user_att


def update_user_dynamodb(userID, dataParamethers, ):
    table = dynamodb.Table(os.environ['TABLE'])
    attr_names, update_expression, expression_vals = buildExpression(dataParamethers)
    try:
        ExpressionAttributeValues = attr_names,
        UpdateExpression = update_expression

        result = table.update_item(
            Key={
                'userID': userID
            },
            ExpressionAttributeValues=attr_names,
            UpdateExpression=update_expression,
            ReturnValues='ALL_NEW',
        )
        responseJson = {
            "statusCode": 200,
            "headers": {"Content-Type": 'application/json'},
            "body": 'Update user on dynamodb'
         }
        return responseJson
    except Exception as err:
        responseJson = {
            "statusCode": 400,
            "headers": {"Content-Type": 'application/json'},
            "body": str(err)
         }
        print(err)
        return responseJson


def buildExpression(data):
    vals = {}
    exp = 'SET '
    attr_names = {}
    for key, value in data.items():
        vals[':{}'.format(key)] = value
        attr_names['{}'.format(key)] = key
        exp += '{} = :{},'.format(key, key)
    exp = exp.rstrip(",")
    return vals, exp, attr_names

