import boto3
import json
import requests

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    severity = message['detail']['findings'][0]['Severity']['Label']
    region =   message['detail']['findings'][0]['Region']
    title =    message['detail']['findings'][0]['Title']
    account =  message['account']
    
    final = 'There is a NEW AWS SecurityHub finding in '+ region + '. Account '+ account +'. Title of the finding is '+ title + '. Severity is: '+ severity
    
    
    "New AWS SecurityHub finding in <region> for Account: <account>. The finding title is <title> and the description of the finding is <findingDescription>. Severity is <severity>"

    
    print (final)
    
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
                    "key": "IP"
                },
                "summary":title,
                "description": final,
                "issuetype":{
                    "name": "Task"
                }
            }
        }
    )
    
    response = requests.post(url,headers=headers,data=payload,auth=("shrirajchohan@yahoo.com","qf4v2Toyg08LoePbM1Eu32D8"))
  
    print(response.text)
    
    return message
    
    
