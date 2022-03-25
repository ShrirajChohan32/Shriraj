# Description

This script's purpose is to gather all the EC2's metadata to analyze if any instances have 0.0.0.0/0 rule written in there.

1. Get all the security groups' metadata
2. Check if those security groups' Permission have 0.0.0.0/0 ingress rule from any port.
3. If yes then append the security groups' name and write to a new CSV file row by row.


## Workflow

To run this script.

1. Connect to your VPN via Global Protect.
2. Run the script using this command python3 ec2_sg_ingress_anywhere {client account name}. use -h for help
3. This script will download the Ec2's security groups' metadata from the account.
4. Check if they have 0.0.0.0/ ingress rules in them.
5.
