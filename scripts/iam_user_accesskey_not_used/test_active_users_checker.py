import os, csv, datetime
import boto3
from pyparsing import delimited_list
import pytest
import iam_active_users_checker
import botocore.exceptions


# TODO: Change to environment variable
session = boto3.Session(profile_name="devopstesting")
iam_client = session.client("iam")

TEMP_IAM_USERNAME = "ac3_active_user_checker_test_account"


def delete_key_and_user():
    if iam_client.get_user(UserName=TEMP_IAM_USERNAME)["User"]:
        # get access key id

        resp = iam_client.list_access_keys(UserName=TEMP_IAM_USERNAME)[
            "AccessKeyMetadata"
        ]
        print(resp)
        if len(resp) > 0:
            accessKeyId = resp[0]["AccessKeyId"]
        else:
            accessKeyId = resp["AccessKeyId"]
        delete_key = iam_client.delete_access_key(
            UserName=TEMP_IAM_USERNAME, AccessKeyId=accessKeyId
        )
        print(f"Deleted Access Key: {delete_key}")
        delete_user = iam_client.delete_user(UserName=TEMP_IAM_USERNAME)
        print(f"Deleted temporary IAM user: {delete_user}")


@pytest.fixture(scope="session")
def tempuser():
    """
    Fixture to create temporary IAM user which is used in tests and delete IAM user once tests finish.
    Returns: dict - see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_access_key
    """

    try:
        iam_client.get_user(UserName=TEMP_IAM_USERNAME)
    except botocore.exceptions.ClientError as e:

        iam_user = iam_client.create_user(UserName=TEMP_IAM_USERNAME)
        print(f"Created temporary IAM user for testing: {iam_user}")
        yield iam_user
        # Code below is for fixture teardown after all tests have ran
        delete_key_and_user()
        # delete_key = iam_client.delete_access_key(UserName="", AccessKeyId=accessKeyId)
        # delete_user = iam_client.delete_user(UserName=TEMP_IAM_USERNAME)

        print(f"Deleted temporary IAM user: {delete_user}")

    iam_user = iam_client.get_user(UserName=TEMP_IAM_USERNAME)
    print(f"Using existing temporary IAM user for testing: {iam_user}")
    yield iam_user

    delete_key_and_user()


@pytest.fixture(scope="session")
def access_key(tempuser):
    """
    Fixture to create access key which is used in tests, and remove it when tests finish
    Returns: dict - see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_access_key
    """
    key = iam_client.create_access_key(UserName=tempuser["User"]["UserName"])
    print(f"Created Key: {key}")
    accessKeyId = key["AccessKey"]["AccessKeyId"]
    yield key
    # Code below is for fixture teardown after all tests have ran
    delete_key_and_user()
    # delete_key = iam_client.delete_access_key(
    #     UserName="cdk-test", AccessKeyId=accessKeyId
    # )
    # print(f"Deleted Key: {delete_key}")


@pytest.fixture(scope="session")
def script_csv_output():
    iam_active_users_checker.main()


def test_get_days_since_access_key_used(access_key, tempuser) -> None:
    """
    Tests function get_days_since_access_key_used properly
    Expected result: pass
    Example input data: AKIAIOSFODNN7EXAMPLE
    """
    days_since_usage = iam_active_users_checker.get_days_since_access_key_used(
        access_key["AccessKey"]["AccessKeyId"]
    )

    assert isinstance(days_since_usage, int)
    assert isinstance(session, boto3.Session)

    last_used_response = iam_client.get_access_key_last_used(
        AccessKeyId=access_key["AccessKey"]["AccessKeyId"]
    )

    # Shouldn't be in the response since it was just created
    assert "LastUsedDate" not in last_used_response["AccessKeyLastUsed"]
    assert days_since_usage is 0


# BROKEN
def test_get_days_since_access_key_used_active(tempuser, access_key):
    # Find a key that has been used in the past & Verify that the script returns the correct days since usage
    # We only should have to do this once, since if the script's function is used to write to the CSV file.

    # Loop over all users in account and find a key that's been used, then compare the value to value that function get_days_since_access_key_used returns
    users = iam_client.list_users(MaxItems=300)
    active_key = {}
    for user in users["Users"]:
        username = user["UserName"]
        keys_response = iam_client.list_access_keys(UserName=username)

        for key_id in keys_response["AccessKeyMetadata"]:
            # Check if key is active and has been used
            key_info = iam_client.get_access_key_last_used(
                AccessKeyId=key_id["AccessKeyId"]
            )

            if "LastUsedDate" in key_info["AccessKeyLastUsed"]:
                key_last_used = key_info["AccessKeyLastUsed"].get("LastUsedDate")
                key_last_used_date = (
                    datetime.datetime.now() - key_last_used.replace(tzinfo=None)
                ).days
                if key_last_used_date > 0:
                    active_key["AccessKeyId"] = key_id["AccessKeyId"]
                    active_key["LastUsedDate"] = key_last_used_date
                    print(active_key)
                    # we found our active key
                    print(
                        f"Found active key {key_id['AccessKeyId']}, last used {key_last_used_date} days ago"
                    )

                    break
                else:
                    continue
        break

    # Compare last used date from script to function above to verify its correct
    assert (
        iam_active_users_checker.get_days_since_access_key_used(
            active_key["AccessKeyId"]
        )
        == active_key["LastUsedDate"]
    )

    assert (
        iam_active_users_checker.get_days_since_access_key_used(
            active_key["AccessKeyId"]
        )
        is not 0
    )


def test_with_invalid_access_key() -> None:
    """
    Tests function "get_days_since_access_key_used" fails when an access key that doesn't exist is passed to function

    Expected result: Failure
    Example input data: AKIAIOSFODNN7EXAMPLE_
    """
    with pytest.raises(Exception):
        days_since_usage = iam_active_users_checker.get_days_since_access_key_used(
            "AKIAIOSFODNN7EXAMPLE_"
        )


def test_file_created(script_csv_output) -> None:

    # Verify file exists
    # Call script
    path = os.path.join(os.getcwd(), "iam_user_accesskey_not_used.csv")
    assert os.path.exists(path)


def test_verifyFileContents(
    path=os.path.join(os.getcwd(), "iam_user_accesskey_not_used.csv")
) -> None:
    """ """
    with open(path) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=",")
        line_count = 0
        print("Reading CSV file")
        for row in reader:
            print(f"Row: {row}")
            # Check formatting is right
            assert row["Days"].isdecimal()
            # Verify each user exists
            assert iam_client.get_user(UserName=row["User"])["User"]
            #
