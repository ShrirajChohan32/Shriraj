import boto3
import csv
import argparse

ANYWHERE = "0.0.0.0/0"

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="Specify an AWS account & region")
parser.add_argument("region", help="set region")

args = parser.parse_args()


session = boto3.Session(profile_name=args.profile)
ec2_client = session.client("ec2", region_name=args.region)


def get_ec2_sg() -> list:

    """Get all Ec2 Instance's security group ID

    Returns:
        used_sg: list
    """
    all_instances = ec2_client.describe_instances()
    used_sg = []

    # Whole Json content from all_instances variable that
    for json_content in all_instances["Reservations"]:
        # describes_instances and gets json infromation.
        for one_instance in json_content["Instances"]:
            # Gets SecurityGroup Metadata
            for used_security_groups in one_instance["SecurityGroups"]:
                used_sg.append(used_security_groups["GroupId"])

    return used_sg


def get_sg_info(list_of_used_sg: list) -> list:

    """Gets all unused security group information

    Args:
        sg_all_list: All the security groups, sg_used_list: All the used security groups list.

    Returns:
        List[dict]
    """

    open_ip = []

    # unused_security_group = list(set(sg_all_list) - set(sg_used_list))
    sg_id = ec2_client.describe_security_groups(GroupIds=list_of_used_sg)
    for groups in sg_id["SecurityGroups"]:
        for permission in groups["IpPermissions"]:
            # open_ip = [range for range in permission["IpRanges"] if range["CidrIp"] == ANYWHERE]
            for range in permission["IpRanges"]:
                if range["CidrIp"] == ANYWHERE:
                    open_ip.append(groups["GroupId"])

    return open_ip


def write_csv(list_sg_info: dict):
    """Get all security group ID

    Args:
        list_sg_info: All the unused security group metadata.

    Returns:
        None
    """

    file_header = ["Ec2 Sg allowing 0.0.0.0/0"]
    sg_metadata = []

    sg_id = ec2_client.describe_security_groups(GroupIds=list_sg_info)
    for groups in sg_id["SecurityGroups"]:
        sg_metadata.append(groups)

    with open("sg_ingress_anywhere.csv", "w") as sg_ingress_anywhere:
        writer = csv.writer(sg_ingress_anywhere)
        writer.writerow(file_header)

        for details in sg_metadata:
            group_name = details["GroupName"]
            group_id = details["GroupId"]
            combined_row = [group_name, group_id]
            writer.writerow(combined_row)

    return


def main():

    list_of_used_sg = get_ec2_sg()
    list_sg_info = get_sg_info(list_of_used_sg)
    write_csv(list_sg_info)
    return


if __name__ == "__main__":
    main()
