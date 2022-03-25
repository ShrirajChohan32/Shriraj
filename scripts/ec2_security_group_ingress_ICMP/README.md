# Description
This script's purpose to gather all ec2 instance security groups and check for ICMP.

1. Gets all the instance's security groups' metadata
2. Check if those security groups have ICMP that is allowed in from 0.0.0.0/0
3. If Yes then gather the security group ID and name of those ids
4. And write them to an CSV file


## Workflow

To run this script.

1. Connect to your VPN via Global Protect.
2. Run the script using this command python3 users_with_no_groups {client account name}. use -h for help
3. This script will download all the EC2 instance's metadat from ec2_client.describe_instances()
4. This python script will loop through all instances's security group protocls to check if they allow ICMP from everywhere.
5. If the security group do allow those two rules. get_sg_info() function will append those security groups metata as list.
6. It will the pass the return statement of the get_sg_info() to write_csv argument
7. Where the group ID and name will be written in to a CSV file.
