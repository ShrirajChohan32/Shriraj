import datetime
import csv
import boto3
import argparse
from botocore.exceptions import ClientError


TODAY = datetime.datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="Specify an AWS account")
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)
iam_client = session.client("iam")
# session = boto3.Session(profile_name="devopstesting")
# iam_client = session.client("iam")


def generate_aws_credential_report(iam_client):
    """Trigger AWS' credential report

    Reference:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.generate_credential_report
    https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_getting-report.html

    Args:
        iam_client: boto3 iam client object

    Returns:
        None
    """
    iam_client.generate_credential_report()
    response = iam_client.get_credential_report()
    report = response["Content"].decode("utf-8")

    with open("./report.csv", "w") as csvfile:
        csvfile.write(report)
        print("Done")
    return


def get_max_password_age(iam_client) -> int:
    """Get max password age policy from AWS

    Args:
        iam_client: boto3 iam client object

    Returns:
        int: max number of days allowed for a password to exist
    """
    try:
        response = iam_client.get_account_password_policy()
        for password_policy_age in response["PasswordPolicy"]:
            if password_policy_age == "MaxPasswordAge":
                return int(response["PasswordPolicy"]["MaxPasswordAge"])
            else:
                response = 90
                return response
    except ClientError as e:
        print("Unexpected error in get_max_password_age: %s" + e.message)
        return


def create_credential_report(password_max_age: int):
    """Create credential report file based on AWS credential report

    Creates a new file called "User_Password_Report.csv"
    Opens `report.csv` created by generate_credential_report()
    Checks the report.csv line by line
    It checksif
        1) the row does not start with "user" and
        2)  user has password enabled
    Fetches the column 6 of that user's row which is "password_last_changed"
    Compares it to password_max_age
    Writes to User `User_Password_Report.csv` if password is too old

    Args:
        password_max_age: int -> Password policy configured on current account

    Returns:
        None
    """
    password_report_header = ["Users", "Password Last Updated"]

    with open("./User_Password_Report.csv", "+w") as password_report:
        writer = csv.writer(password_report)
        writer.writerow(password_report_header)
        with open("./report.csv", "r") as credential_report:
            for line in credential_report.readlines():
                if line.split(",")[0] == "user":
                    continue
                elif line.split(",")[3] != "true":
                    continue
                else:
                    user = line.split(",")[0]
                    password_last_changed = line.split(",")[5]
                    password_last_changed = datetime.datetime.strptime(
                        password_last_changed, "%Y-%m-%dT%H:%M:%S+00:00"
                    )
                    print(password_last_changed)

                    password_last_changed_days = (
                        TODAY - password_last_changed.replace(tzinfo=None)
                    ).days

                    if password_last_changed_days > password_max_age:
                        user_password_info = [user, password_last_changed_days]
                        writer.writerow(user_password_info)
                        print(password_last_changed_days)
        return


def main():
    password_max_age = get_max_password_age(iam_client)
    print(password_max_age)
    generate_aws_credential_report(iam_client)
    create_credential_report(password_max_age)


if __name__ == "__main__":
    main()
