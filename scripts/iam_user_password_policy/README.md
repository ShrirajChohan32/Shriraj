# Description

1. Get credential report from aws
2. open the file in read mode
3. ignore the first line
4. check if `password_enabled` is set to `TRUE`
5. get max password age policy directly from AWS
6. Compare max password age with `password_last_changed`
7. If password_last_changed is older than max password age, write a new report file

## Workflow

To run this script. 

1. Connect to your VPN via Global Protect. 
2. Change the customer's name in the session variable for .e.g, if you want to assume devopstesting account 
    , then we should assume the devopstesting account role session = boto3.Session(profile_name='devopstesting')
3. This script will download the aws credential report that will have all the user's information. 
4. The script also has a function that checks the maximum password age from the aws account policy. (Default is 90 days)
3. The script will loop through the credential report csv file line by line, checking if the user has password enabled.
4. If the user has password enabled it checks for the password_last_changed date (coloumn 6) from the credentials report csv 
5. It then compares it to the maximum password age from the aws account policy by an if statement.
6. If the user's password changed date minus today's date is more than the maximum password age from the aws account policy
7. parse_credential_report function writes username and the number of days since they haven't last changed their password 
    in a new password_report.csv file. 