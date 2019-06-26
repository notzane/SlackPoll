import json
from urllib.parse import parse_qs
from botocore.vendored import requests
import os
import boto3 #amazon sdk


def lambda_handler(event, context):
    message_body = parse_qs(event["body"]) #passed in a url format -- convert to python dict

    payload = json.loads(message_body["payload"][0]) #payload is passed a json string
    
    answer = payload["actions"][0]["value"]
    response_url = payload["response_url"]
    channelID = payload["channel"]["id"]
    channel = payload["channel"]["name"]
    userID = payload["user"]["id"]
    user = payload["user"]["name"]
    question = payload["original_message"]["text"][1:-1] #remove * *
    
    #find token
    ssm = boto3.client('ssm')
    token = ssm.get_parameter(Name='bot_access_token')['Parameter']['Value']
    
    current_question = ssm.get_parameter(Name = 'recent_question')['Parameter']['Value']

    api_url = "https://slack.com/api/chat.postEphemeral"
    api_url += "?token=" + token
    api_url += "&user=" + userID
    api_url += "&channel=" + channelID
    
    print(question, current_question) 
    
    if(current_question != question): #no longer current quesiton
        api_url += "&text=" + "_This poll has closed_"
    else: #still on current question
        api_url += "&text=" + "_Your response: " + answer +"_"
            
        #put answer in database
        dynamodb = boto3.client('dynamodb')
        dynamodb.put_item(TableName='answers', Item={
            'question': {"S" : question},
            'userID' : {"S" : userID},
            'channel' : {"S" : channel},
            'user': {"S" : user},
            'answer': {"S" : answer},
        })
    
    response = requests.post(api_url) #show answer selestion in slack to user only

    print(response.status_code)
    print(response.text)
    

    
    return {"statusCode": 200} #return 200 to say everything worked