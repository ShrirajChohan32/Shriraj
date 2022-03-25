import boto3
import json
import csv
from jira import JIRA


# Severity = "CRITICAL"
# Region = "eu-west-1"
# Title = "MFA needsto be enabled on root account"
# Account = "24561370098"

# new_finding= [Severity,Region,Title,Account]
# file_header= ['Severity','Region','Title','Title']

LOCAL_FILEPATH = "/tmp/Hub.csv"

secret_name = "/prod/my-secret-api"
region_name = "ap-southeast-2"

# Create a Secrets Manager client
session = boto3.session.Session()

secrets_manager = session.client(service_name="secretsmanager", region_name=region_name)

get_secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)

secret = json.loads(get_secret_value_response["SecretString"])
token = secret["Bitbucket"]
email = secret["email"]
restapi = secret["api"]


def lambda_handler(event, context):

    message = json.loads(event["Records"][0]["Sns"]["Message"])

    severity = message["detail"]["findings"][0]["Severity"]["Label"]
    region = message["detail"]["findings"][0]["Region"]
    title = message["detail"]["findings"][0]["Title"]
    account = message["account"]

    file_header = ["Severity", "Region", "Title", "Account"]
    new_finding = [severity, region, title, account]

    jira_options = {"server": "https://shrirajchohan32.atlassian.net"}

    jira_auth = (email, token)
    jira = JIRA(options=jira_options, basic_auth=(jira_auth))

    jql = 'project = "SEC" AND text ~ "ALL SECURITY FINDINGS"'

    raw_issue = jira.search_issues(jql_str=jql, fields=["attachment"])

    def create_csv():
        with open(LOCAL_FILEPATH, "w") as new_csv:
            writer = csv.writer(new_csv)
            writer.writerow(file_header)
            writer.writerow(new_finding)
            # data = pd.read_csv(LOCAL_FILEPATH)
            # ic(data)
        return

    def get_attachment_id(issue):
        pass

    def upload_attachment_jira():
        # Opening the file in read mode and then attaching it to jira.attachment to upload it to the ticket.
        with open(LOCAL_FILEPATH, "rb") as appended_csv:
            try:
                jira.add_attachment(
                    issue.key, attachment=appended_csv, filename="Hub.csv"
                )
                return
            except Exception as e:
                print("An error occurred: %s" % e)
                return

    # This loop is only valid if we have more than one issue
    for issue in raw_issue:
        print(issue.key)  # Gets the issue key from the Jira Project
        print(issue.fields.attachment)  # Gets the Attachement ID from the issue key

        if not issue.fields.attachment:
            print("Not Exist")
            create_csv()
            upload_attachment_jira()

        else:
            print("EXIST")

        for item in issue.fields.attachment:
            att_id = item.id
            print(att_id)
            att = jira.attachment(att_id)
            print(att)
            name_of_file = att.filename

            # Take this below if statement outsde of For loop
            if name_of_file == "Hub.csv":
                print("Hub.csv Exist")
                att_id = item.id
                print(att_id)
                print(att.filename)
                file_name = att.get()  # gets the file from the ticket
                with open(LOCAL_FILEPATH, "wb") as temporary_csv:
                    temporary_csv.write(file_name)

                with open(LOCAL_FILEPATH, "r") as infile:
                    reader = list(csv.reader(infile))
                    reader = reader[::-1]  # the date is ascending order in file
                    reader.insert(0, new_finding)

                with open(LOCAL_FILEPATH, "w") as outfile:
                    writer = csv.writer(outfile)
                    for line in reversed(reader):  # reverse order
                        writer.writerow(line)

                query = jira.search_issues(
                    jql_str=jql, json_result=True, fields="key, attachment"
                )

                for i in query["issues"]:
                    for a in i["fields"]["attachment"]:
                        print(
                            "For issue {0}, found attach: '{1}' [{2}].".format(
                                i["key"], a["filename"], a["id"]
                            )
                        )
                        jira.delete_attachment(a["id"])

                upload_attachment_jira()

            else:
                create_csv()
                upload_attachment_jira()

                return
