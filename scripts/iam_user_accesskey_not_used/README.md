
# Description

1. Create an empty csv file with the following headers:
    a) user
    b) policies
    c) days
2. Loop through each user
3. For each user, get the list of attached policies
4. For each user get their access key
5. For each access key get the number of days since access key was used

## Workflow

To run this script. 

1. Connect to your VPN via Global Protect. 
2. Change the customer's name in the session variable for .e.g, if you want to assume devopstesting account 
    , then we should assume the devopstesting account role session = boto3.Session(profile_name='devopstesting')
3. The script will loop through all the users' by fetching their Access Key, if any and then check their access key's metadata.
4. Within their metadata, the script will check the last used date of the access key.
5. The last used date of the access key will be subtracted from today's date and the output of the result will be give as days in integer.
6. For e.g. Last_used_access_key_date - today_date = 149. The 149 will be in days. 
7. This script will also fetch user's policy infrmation such as user's inline and managed policy assigned ot them
8. After gathering all these 3 information (Username, policies attached to the users, Number of days since the access key was last used) from the account.
9. It will then write it to a new CSV file row by row.


