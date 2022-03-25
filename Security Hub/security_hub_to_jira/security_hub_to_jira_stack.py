from aws_cdk import (
    core,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_securityhub as securityhub,
    aws_events_targets as event_targets,
    aws_events as events,
    aws_sns_subscriptions as subscriptions,
    aws_iam as iam
)

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

class SecurityHubToJiraStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        #SNS Topic
        topic = sns.Topic(self, "SecurityHubFindings")

        # Lambda Role

        lambda_role=iam.Role(
            self, 'lambda_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            role_name='%sLambdaRole' %self.stack_name
        )

        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                'secretsmanager:GetSecretValue',
            ],
            effect=iam.Effect.ALLOW,
            resources=['arn:aws:secretsmanager:%s:%s:secret:/prod/*' 
            % (self.region, self.account)]))

        #LAMBDA Function
        my_lambda = _lambda.Function(
            self, 'JiraHandler',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('Lambda'),
            handler='Jira.lambda_handler',role=lambda_role)

        #Subscription
        topic.add_subscription(subscriptions.LambdaSubscription(my_lambda))

        # Eventbridge Rule 
        rule = events.Rule(self,"SecurityHubRule",
        event_pattern=events.EventPattern(source=['aws.securityhub'],
        detail_type=['Security Hub Findings - Imported'],
        detail={'findings':{'Severity':{'Label':['CRITICAL','HIGH']}}}))

        rule.add_target(event_targets.SnsTopic(topic))
