# Description

This script's purpose is to gather all the users' that do not have MFA enabled.

1. Get all the users metadata
2. Check if those users have any mfa devices listed
3. If not then append all the users in the set() = users_without_mfa
4. Create a CSV and write all the users from the set users_without_mfa row by row


## Workflow

To run this script.

1. Connect to your VPN via Global Protect.
2. Run the script using this command python3 no_mfa {client account name}. use -h for help
3. This script will download the users's metadata from the account.
4. The no_mfa_users function checks if the user has any listed mfa devices listed.
5. If not then it returns users_without_mfa set
6. The users_without_mfa set is then called in to write_csv() function
7. Which then wrties all the users_without_mfa into na csv row by row.
