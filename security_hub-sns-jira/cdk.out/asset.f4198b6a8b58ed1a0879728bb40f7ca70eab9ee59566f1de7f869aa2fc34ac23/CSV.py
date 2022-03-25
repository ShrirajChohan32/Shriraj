import boto3
import csv
import base64
import json
from csv import writer


s3 = boto3.resource('s3')

bucket = s3.Bucket('shriraj-csv') # Enter your bucket name, e.g 'Data'
# key path, e.g.'customer_profile/Reddit_Historical_Data.csv'
key = 'SecurityHub.csv'


def lambda_handler(event, context):
    
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    severity = message['detail']['findings'][0]['Severity']['Label']
    region =   message['detail']['findings'][0]['Region']
    title =    message['detail']['findings'][0]['Title']
    account =  message['account']
    
    obj = list(bucket.objects.filter(Prefix=key))
    if obj:
        print("exist")
        # download s3 csv file to lambda tmp folder
        local_file_name = '/tmp/SecurityHub.csv' #
        s3.Bucket('shriraj-csv').download_file(key,local_file_name)
        
        # list you want to append
        lists = [severity,region,title,account] 
        # write the data into '/tmp' folder
        with open('/tmp/SecurityHub.csv','r') as infile:
            reader = list(csv.reader(infile))
            reader = reader[::-1] # the date is ascending order in file
            reader.insert(0,lists)
        
        with open('/tmp/SecurityHub.csv', 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            for line in reversed(reader): # reverse order
                writer.writerow(line)
                
        # upload file from tmp to s3 key
        bucket.upload_file('/tmp/SecurityHub.csv', key)
    
        print("Success")
        
    else:
        
        print("Not Exists")
        
        with open('/tmp/SecurityHub.csv', 'w') as output_file:
            wf = csv.writer(output_file)
            wf.writerow(['SEVERITY','REGION','TITLE','ACCOUNT'])

        bucket.upload_file('/tmp/SecurityHub.csv', key)
    return
