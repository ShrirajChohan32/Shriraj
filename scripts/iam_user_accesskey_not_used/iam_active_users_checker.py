import boto3
import datetime
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="Specify an AWS account")
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)
iam_client = session.client("iam")


def get_days_since_access_key_used(access_key_id: str) -> int:
    """Get last day since access key used
    Args:
        access_key_id: Access key ID of the user

    Returns:
        int
    """
    today = datetime.datetime.now()

    # Get Metadata of their access key
    last_used_response = iam_client.get_access_key_last_used(AccessKeyId=access_key_id)

    if "LastUsedDate" in last_used_response["AccessKeyLastUsed"]:
        key_last_used = last_used_response["AccessKeyLastUsed"].get("LastUsedDate")
        return (today - key_last_used.replace(tzinfo=None)).days
    else:
        return 0


def get_user_policies(username: str) -> str:
    """Get user policies
    Args:
        user_name: Name of the user

    Returns:
        str
    """
    policies = ""
    inline_policies = iam_client.list_user_policies(UserName=username)
    managed_policies = iam_client.list_attached_user_policies(UserName=username)

    for inline_policy in inline_policies.get("PolicyNames"):
        if policies:
            policies = "{} {}".format(policies, inline_policy)

    for managed_policy in managed_policies.get("AttachedPolicies"):
        policies = "{} {}".format(policies, managed_policy["PolicyName"])

    return policies


def write_csv():

    users = iam_client.list_users(MaxItems=300)
    file_header = ["User", "Policies", "Days"]

    with open("./iam_user_accesskey_not_used.csv", "w") as list_of_users:
        writer = csv.writer(list_of_users)
        writer.writerow(file_header)

        for user in users["Users"]:
            username = user["UserName"]

            # Get their access keys
            keys_response = iam_client.list_access_keys(UserName=username)
            for key_id in keys_response["AccessKeyMetadata"]:
                days_since_used = get_days_since_access_key_used(key_id["AccessKeyId"])
                policies = get_user_policies(username)
                user_access_key_data = [username, policies, days_since_used]
                writer.writerow(user_access_key_data)

    return


def main():

    write_csv()


if __name__ == "__main__":
    main()
