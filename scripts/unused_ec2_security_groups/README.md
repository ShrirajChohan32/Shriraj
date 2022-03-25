# Description

1. Get all the EC2's informtion from the account
2. Looks at all the security groups attached to the Ec2 Instances
3. gets the security group ID that are attached to the Ec2 Instances
4. Get all the Security Group from the AWS account
5. Looks at the Security Groups' metadata of each individual security.
6. Gets at all the security groups' ID from the each Security Group metadata.
7. In the main function it calls get_all_sg function & get_all_sg
8. It subtracts get_all_sg - get_all_sg sets(), to get all the unused security groups ID.
9. It then opens up a file and writes those unused security groups' ID row by row.

## Workflow

To run this script.

1. Connect to your VPN via Global Protect.
2. Run the script using this command python3 unused_security_groups {client account name}. use -h for help
3. This script will download all the Ec2's metadata using boto3 when this object is called ec2.describe_security_groups()
4. This python script will also download all the Security group's metadata and append all the security groups's ID in sg_append set()
5. When main fucntion is called it subtracts instance_sg_name_append from sg_append set to get the unused security groups
6. And then it writes those unused security groups in an csv file with a header unused security group.
