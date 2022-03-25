# Description
This script's purpose to gather & list all the users that are not attached to any groups.

1. Gets all the users
2. Gets all the groups
3. Gets all the users from all the groups
4. Subtracts all the group users from all the total number of users in the account.
5. The result of the subtraction is the number of users who don't belong to an IAM group.


## Workflow

To run this script.

1. Connect to your VPN via Global Protect.
2. Run the script using this command python3 users_with_no_groups {client account name}. use -h for help
3. This script will download all the User's metadata using boto3 when this object is called users = iam.list_users()
4. This python script will also download all the Group's metada using response = iam.list_groups()
5. It will loop through all the groups to find the users
6. It will subtract all the users who belong to an IAM group from the total number of users in the aws account.
7. The result will written in to an CSV.
