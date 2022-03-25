import boto3
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="Specify an AWS account")
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)
iam_client = session.client("iam")


def get_all_users_in_groups() -> list:
    """Get all Users that are tied to groups

    Returns:
        List[str]
    """
    group_name_append = set()
    group_users = set()

    response = iam_client.list_groups()
    users = iam_client.list_users(MaxItems=1000)

    for group in response["Groups"]:

        group_details = iam_client.get_group(GroupName=group["GroupName"])
        group_name_append.add(group["GroupName"])
        for users in group_details["Users"]:
            group_users.add(users["UserName"])

    return group_users


def get_all_users() -> list:
    """Get all users in the account.

    Returns:
        List[str]
    """
    total_users = set()

    users = iam_client.list_users()
    for u in users["Users"]:
        total_users.add(u["UserName"])

    return total_users


def write_csv(all_users, users_with_groups):

    """Subtracts users within the groups from all users and writes to CSV

    Args:
        all_users: all users' UserName,
        users_with_groups: all the users' UsernName who belong to a group.

    Returns:
        None
    """

    file_header = ["Users not tied with Groups"]

    users_without_groups = all_users - users_with_groups

    with open("./users_without_groups.csv", "+w") as users_not_assigned_to_groups:
        writer = csv.writer(users_not_assigned_to_groups)
        writer.writerow(file_header)
        for data in users_without_groups:
            writer.writerow([data])
    return


def main():

    users_with_groups = get_all_users_in_groups()
    all_users = get_all_users()
    write_csv(all_users, users_with_groups)


if __name__ == "__main__":
    main()
