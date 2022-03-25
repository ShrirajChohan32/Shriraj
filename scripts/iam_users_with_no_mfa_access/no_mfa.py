from ast import parse
from sys import argv
import boto3
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="Specify an AWS account")
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)
iam_client = session.client("iam")

file_header = ["Users with no MFA"]


def get_all_users() -> list:
    """Get user policies
    Args:
        user_name: Name of the user

    Returns:
        str
    """
    # TODO: check paginator https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html
    response = iam_client.list_users(MaxItems=1000)

    iam_users = []

    for user in response["Users"]:
        iam_users.append(user["UserName"])

    return iam_users


def no_mfa_users(all_user: list) -> list:

    """Describes users without mfa

    Args:
        all_user: all user's UserName

    Returns:
        users_without_mfa  set
    """

    users_without_mfa = set()

    for iam_user in all_user:
        json_context = iam_client.list_mfa_devices(UserName=iam_user)
        if not json_context["MFADevices"]:
            users_without_mfa.add(iam_user)
    return users_without_mfa


def write_csv(no_mfa_set: set):

    """Writes users who don't have MFA enabled to a CSV file

    Args:
        no_mfa_set: all user's UserName who don't have MFA enabled

    Returns:
        none
    """

    with open("no_mfa.csv", "w") as no_mfa:
        writer = csv.writer(no_mfa)
        writer.writerow(file_header)
        for user_with_no_mfa in no_mfa_set:
            writer.writerow([user_with_no_mfa])
    return


def main():
    all_user = get_all_users()
    no_mfa_set = no_mfa_users(all_user)
    print(no_mfa_set)
    write_csv(no_mfa_set)

    return


if __name__ == "__main__":
    main()
