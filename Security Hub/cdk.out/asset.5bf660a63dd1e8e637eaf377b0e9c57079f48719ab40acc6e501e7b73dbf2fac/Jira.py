import boto3
import base64
import json
import requests
from botocore.exceptions import ClientError


secret_name = "/prod/my-secret-api"
region_name = "ap-southeast-2"
# Create a Secrets Manager client
session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

get_secret_value_response = client.get_secret_value(
    SecretId=secret_name
)
    
secret = json.loads(get_secret_value_response['SecretString'])
token =  secret['Bitbucket']

    #print(json.dumps(json.loads(jsonpickle.encode(get_secret_value_response)), indent=1))


def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    severity = message['detail']['findings'][0]['Severity']['Label']
    region =   message['detail']['findings'][0]['Region']
    title =    message['detail']['findings'][0]['Title']
    account =  message['account']
    
    final = 'There is a NEW AWS SecurityHub finding in '+ region + '. Account '+ account +'. Title of the finding is '+ title + '. Severity is: '+ severity
    
    print (final)
    
    if severity == "CRITICAL":

        url = "https://shrirajchohan32.atlassian.net/rest/api/2/issue"

        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }   
        payload= json.dumps(    
                {   
                "fields":{  
                    "project":
                    {   
                        "key": "SEC"
                    },
                    "summary":title,
                    "description": final,
                    "issuetype":{
                        "name": "Task"
                                },
                    "customfield_10014": "SEC-1"
                                }
                            }
                        )

        response = requests.post(url,headers=headers,data=payload,auth=("shrirajchohan@yahoo.com","qf4v2Toyg08LoePbM1Eu32D8"))

        print(response.text)

    if severity == "HIGH":
    
        url = "https://shrirajchohan32.atlassian.net/rest/api/2/issue"
    
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }   
        payload= json.dumps(    
                {   
                "fields":{  
                    "project":
                    {   
                        "key": "SEC"
                    },
                    "summary":title,
                    "description": final,
                    "issuetype":{
                        "name": "Task"
                                },
                    "customfield_10014": "SEC-2"
                                }
                            }
                        )
    
        response = requests.post(url,headers=headers,data=payload,auth=("shrirajchohan@yahoo.com","qf4v2Toyg08LoePbM1Eu32D8"))
        
        print(response.text)
    
    
    # url = "https://shrirajchohan32.atlassian.net/rest/api/2/issue"
    # headers={
    # "Accept": "application/json",
    # "Content-Type": "application/json"
    # }
    
    # payload= json.dumps(
    #     {
    #         "fields":{
    #             "project":
    #             {
    #                 "key": "IP"
    #             },
    #             "summary":title,
    #             "description": final,
    #             "issuetype":{
    #                 "name": "Task"
    #             }
    #         }
    #     }
    # )
    
    # response = requests.post(url,headers=headers,data=payload,auth=("shrirajchohan@yahoo.com",token))
  
    # print(response.text)
    
    return message
    
    



