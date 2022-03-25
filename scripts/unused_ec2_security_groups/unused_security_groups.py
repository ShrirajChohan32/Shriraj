import boto3
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="Specify an AWS account & region")
parser.add_argument("region", help="set region")

args = parser.parse_args()


session = boto3.Session(profile_name=args.profile)
ec2_client = session.client("ec2", region_name=args.region)

security_groups_in_use = []


def get_all_sg() -> list:
    """Get all security group ID

    Returns:
        List[dict]
    """

    all_security_groups = ec2_client.describe_security_groups()

    return [
        security_group["GroupId"]
        for security_group in all_security_groups["SecurityGroups"]
    ]


def get_elasticache_sg():
    """Get all elasticache's security group ID

    Returns:
        None
    """
    elasticache_client = boto3.client(
        "elasticache",
        region_name="ap-southeast-2",
        aws_access_key_id="AKIAUNIV435EI5SUF2UV",
        aws_secret_access_key="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",
    )
    response = elasticache_client.describe_cache_clusters()
    for content in response["CacheClusters"]:
        for groups in content["SecurityGroups"]:
            if groups["SecurityGroupId"] not in security_groups_in_use:
                security_groups_in_use.append(groups["SecurityGroupId"])

    print(security_groups_in_use)
    return


def get_ec2_sg():
    """Get all Ec2 Instance's security group ID

    Returns:
        None
    """
    # print(list_all_sg)
    all_instances = ec2_client.describe_instances()

    # Whole Json content from all_instances variable that
    for json_content in all_instances["Reservations"]:
        # describes_instances and gets json infromation.
        for one_instance in json_content["Instances"]:
            # Gets SecurityGroup Metadata
            for used_security_groups in one_instance["SecurityGroups"]:
                if used_security_groups["GroupId"] not in security_groups_in_use:
                    security_groups_in_use.append(used_security_groups["GroupId"])
    print(security_groups_in_use)

    return


def get_classic_lb_sg():
    """Get all Classic Balancer's security group ID

    Returns:
        None
    """

    elb_client = boto3.client("elb", region_name=args.region)

    elb_dict = elb_client.describe_load_balancers()
    for content in elb_dict["LoadBalancerDescriptions"]:
        for id in content["SecurityGroups"]:
            if id not in security_groups_in_use:
                security_groups_in_use.append(id)
    print(security_groups_in_use)
    return


def get_alb_sg():
    """Get all ELB's security group ID

    Returns:
        None
    """

    elbv2_client = session.client("elbv2", region_name=args.region)

    elb2_dict = elbv2_client.describe_load_balancers()
    for content in elb2_dict["LoadBalancers"]:
        if "SecurityGroups" in content:
            for id in content["SecurityGroups"]:
                if id not in security_groups_in_use:
                    security_groups_in_use.append(id)
    print(security_groups_in_use)
    return


def get_rds_sg():
    """Get all RDS's security group ID

    Returns:
        None
    """

    rds_client = boto3.client("rds", region_name=args.region)

    rds_dict = rds_client.describe_db_instances()

    for content in rds_dict["DBInstances"]:
        # print(content)
        for groups in content["VpcSecurityGroups"]:
            if groups["VpcSecurityGroupId"] not in security_groups_in_use:
                security_groups_in_use.append(content["VpcSecurityGroupId"])

    # print(security_groups_in_use)
    return


# def get_network_interface_sg():
#     # eni_client = boto3.client('ec2', region_name=args.region)
#     # eni_client = boto3.client('ec2', region_name='ap-southeast-2',aws_access_key_id="AKIAUNIV435EI5SUF2UV",aws_secret_access_key="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")
#     # session = boto3.Session(profile_name='warehouse')

#     # session = boto3.Session(service_name='ec2',aws_access_key_id="AKIAUNIV435EI5SUF2UV",aws_secret_access_key="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")
#     eni_client = boto3.client('ec2',region_name='ap-southeast-2',aws_access_key_id="AKIAUNIV435EI5SUF2UV",aws_secret_access_key="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")

#     eni_dict = eni_client.describe_network_interfaces()
#     for content in eni_dict['NetworkInterfaces']:
#     	for j in content['Groups']:
#     	    if j['GroupId'] not in security_groups_in_use:
#                 security_groups_in_use.append(j['GroupId'])
#     print(security_groups_in_use)
#     return


def get_sg_info(list_all_sg):
    """Calculates the unused security groups

    Args:
        list_all_sg: All the used security GroupId.

    Returns:
        unused security group metadata
    """

    sg_metadata = []

    unused_security_group = list(set(list_all_sg) - set(security_groups_in_use))
    sg_id = ec2_client.describe_security_groups(GroupIds=unused_security_group)
    for groups in sg_id["SecurityGroups"]:
        sg_metadata.append(groups)

    return sg_metadata


def write_csv(metadata: dict):
    """Writes to a CSV file

    Returns:
        None
    """

    file_header = ["Unsed Security Groups Name", "Unsed Security Groups ID"]

    with open("./UnusedSgs.csv", "+w") as list_of_sg:

        writer = csv.writer(list_of_sg)
        writer.writerow(file_header)
        for details in metadata:
            group_name = details["GroupName"]
            group_id = details["GroupId"]
            combined_row = [group_name, group_id]
            writer.writerow(combined_row)

        return


def main():

    list_all_sg = get_all_sg()
    get_ec2_sg()
    get_classic_lb_sg()
    get_elasticache_sg()
    # get_network_interface_sg()
    get_alb_sg()
    get_rds_sg()
    metadata = get_sg_info(list_all_sg)
    write_csv(metadata)

    return


if __name__ == "__main__":
    main()
