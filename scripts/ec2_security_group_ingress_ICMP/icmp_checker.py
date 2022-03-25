from socket import IPPROTO_ICMP
import boto3
import csv
import argparse

IPPROTO_ICMP = "icmp"
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
        None
    """

    used_sg = []
    all_instances = ec2_client.describe_instances()

    # Whole Json content from all_instances variable that
    for json_content in all_instances["Reservations"]:
        # describes_instances and gets json infromation.
        for one_instance in json_content["Instances"]:
            # Gets SecurityGroup Metadata
            for used_security_groups in one_instance["SecurityGroups"]:
                used_sg.append(used_security_groups["GroupId"])
    # print(used_sg)

    return used_sg


def get_sg_info(list_of_used_sg: list) -> list:

    """Gets all unused security group information

    Args:
        sg_all_list: All the security groups, sg_used_list: All the used security groups list.

    Returns:
        List[dict]
    """
    icmp_protocol_sg_group_id = []

    sg_id = ec2_client.describe_security_groups(GroupIds=list_of_used_sg)
    for groups in sg_id["SecurityGroups"]:
        for permission in groups["IpPermissions"]:
            # print(permission)
            if (
                permission["IpProtocol"] == IPPROTO_ICMP
                and permission["IpRanges"][0]["CidrIp"] == ANYWHERE
            ):
                if groups["GroupId"] not in icmp_protocol_sg_group_id:
                    icmp_protocol_sg_group_id.append(groups)

    return icmp_protocol_sg_group_id


def write_csv(icmp_sg_id: list):

    file_header = ["Security group ID"]

    with open("./ICMP.csv", "+w") as icmp:

        writer = csv.writer(icmp)
        writer.writerow(file_header)
        for id in icmp_sg_id:
            group_name = id["GroupName"]
            group_id = id["GroupId"]
            combined_row = [group_name, group_id]
            writer.writerow(combined_row)

    return


def main():

    list_of_used_sg = get_ec2_sg()
    icmp_sg_id = get_sg_info(list_of_used_sg)
    write_csv(icmp_sg_id)

    return


if __name__ == "__main__":
    main()
