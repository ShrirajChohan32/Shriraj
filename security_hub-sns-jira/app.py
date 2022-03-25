#!/usr/bin/env python3

import aws_cdk as cdk

from security_jira_sns.security_jira_sns_stack import SecurityJiraSnsStack


app = cdk.App()
SecurityJiraSnsStack(app, "security-jira-sns")

app.synth()
