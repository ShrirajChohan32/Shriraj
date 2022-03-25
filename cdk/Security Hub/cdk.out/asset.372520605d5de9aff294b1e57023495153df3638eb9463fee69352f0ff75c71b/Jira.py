import boto3
import base64
import json
import requests
from botocore.exceptions import ClientError
secret_name = "/prod/my-secret-api"
region_name = "ap-southeast-2"
# Create a Secrets Manager client
session = boto3.session.Session()
# FIXME: change the client name to something more meaningful ie: secrets_manager 
secrets_manager = session.client(
    service_name='secretsmanager',
    region_name=region_name
)
get_secret_value_response = secrets_manager.get_secret_value(
    SecretId=secret_name
)
    
secret = json.loads(get_secret_value_response['SecretString'])
token =  secret['Bitbucket']
email = secret['email']
restapi = secret['api']
    #print(json.dumps(json.loads(jsonpickle.encode(get_secret_value_response)), indent=1))
def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    severity = message['detail']['findings'][0]['Severity']['Label']
    region =   message['detail']['findings'][0]['Region']
    title =    message['detail']['findings'][0]['Title']
    account =  message['account']
    
    final = """
    There is a NEW AWS SecurityHub finding in: {}. 
    Account: {}. 
    Title of the finding is: {}.  
    Severity is: {}. """.format(region,account,title,severity)
    
    print (final)
    #def send_finding_jira(severity: str, region: str, title: str, account: str) -> bool:
    def send_finding_jira() -> bool:
        url = restapi
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        }   
        
        if severity == "CRITICAL":
            custom_field = "SEC-1"
        if severity == "HIGH":
            custom_field = "SEC-2"
        
        payload= json.dumps(    
                {   
                "fields":{  
                    "project":{   
                        "key": "SEC"
                    },
                    "summary": title,
                    "description": final,
                    "issuetype": {
                        "name": "Task"
                    },
                    "customfield_10014": custom_field
                    }
                }
            )
        try:
            response = requests.post(url,
                                    headers=headers,
                                    data=payload,
                                    auth=(email,token))
            return True
        except Exception as e:
            print("Error found while posting content to jira: {}".format(e))
            return False
    
    
    if send_finding_jira(severity,region,title,account):
        print("Successfully posted to jira")
    else:
        print("Failed to post to jira")
    return message
