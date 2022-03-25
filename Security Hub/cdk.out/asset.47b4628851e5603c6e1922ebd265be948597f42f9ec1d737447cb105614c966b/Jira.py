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

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

try:
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
        raise e
    elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
        raise e
    elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
        raise e
    elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
        raise e
    elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
        raise e
else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in get_secret_value_response:
        secret = json.loads(get_secret_value_response['SecretString'])
    else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            
    # Your code goes here. 

    #print(json.dumps(json.loads(jsonpickle.encode(get_secret_value_response)), indent=1))
token = secret['Bitbucket']

print (token)

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    severity = message['detail']['findings'][0]['Severity']['Label']
    region =   message['detail']['findings'][0]['Region']
    title =    message['detail']['findings'][0]['Title']
    account =  message['account']

    # severity = "CRITICAL"
    # region = "AUCKLAND"
    # title = "RDS.4 RDS cluster snapshots and database snapshots should be encrypted at rest"
    # account = "12479041358"
    
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
    
    response = requests.post(url,headers=headers,data=payload,auth=("shrirajchohan@yahoo.com",token))
  
    print(response.text)
    
    return message
    
    



