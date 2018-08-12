// Load the AWS SDK for Node.js
const AWS = require('aws-sdk'); 
// Set the region 
AWS.config.update({region: 'us-west-2'});
    
// Create the DynamoDB service object
var dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {

    var userID = "None";
    if (event.pathParameters !== null && event.pathParameters !== undefined) {
        if (event.pathParameters.userID !== undefined && 
            event.pathParameters.userID !== null && 
            event.pathParameters.userID !== "") {
            userID = event.pathParameters.userID;
        }
    }
    
        if (event.queryStringParameters !== null && event.queryStringParameters !== undefined) {
        if (event.queryStringParameters.userID !== undefined && 
            event.queryStringParameters.userID !== null && 
            event.queryStringParameters.userID !== "") {
            userID = event.queryStringParameters.userID;
        }
    }
    var paramsUser = {};
    paramsUser.TableName = process.env.TABLE_U;
   
    
    var params = {
        TableName:process.env.TABLE_F,
        KeyConditionExpression:"#userID = :userIDvalue",
        Limit:3,
        ExpressionAttributeNames: {
            "#userID":"userID",
            
        },
        ExpressionAttributeValues: {
            ":userIDvalue":userID,
         
        }
        
    };
    
    var finalSet = [];
    var userSet = [];
    do{
        var result =  await dynamodb.query(params).promise();
 
        if (result.Items.length) {

            for (var i=0; i< result.Items.length; i++) {

                var key = { "userID": result.Items[i].friendID  };
                paramsUser.Key = key;
                var userData = await dynamodb.get(paramsUser).promise();
                userSet.push(userData);
            };
            finalSet.push.apply(finalSet, userSet);
            userSet = [];
        }
        if(typeof result.LastEvaluatedKey != 'undefined') {
            params.ExclusiveStartKey = result.LastEvaluatedKey;
        }
        
    }while (typeof result.LastEvaluatedKey != 'undefined');
   
    var response = {
      "statusCode": 200,
      "headers": {
        "Access-Control-Allow-Origin" : "*",
        "Access-Control-Allow-Credentials" : true
      },
       "body": JSON.stringify(finalSet)
    }
    return response;
};

