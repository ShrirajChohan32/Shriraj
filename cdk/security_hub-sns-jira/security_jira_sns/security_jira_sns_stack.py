from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_securityhub as securityhub,
    aws_events_targets as event_targets,
    aws_events as events,
    aws_sns_subscriptions as subscriptions,
    aws_iam as iam,
)


class SecurityJiraSnsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SNS Topic
        topic = sns.Topic(self, "SecurityHubFindings")

        # Lambda Role

        lambda_role = iam.Role(
            self,
            "lambda_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="%sLambdaRole" % self.stack_name,
        )

        # AWS Cloudwatch managed policy
        cloud_watch_full_access = iam.ManagedPolicy.from_aws_managed_policy_name(
            "CloudWatchFullAccess"
        )

        lambda_role.add_managed_policy(cloud_watch_full_access)

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "secretsmanager:GetSecretValue",
                ],
                effect=iam.Effect.ALLOW,
                resources=[
                    "arn:aws:secretsmanager:%s:%s:secret:/prod/*"
                    % (self.region, self.account)
                ],
            )
        )

        # Lambda Layers
        jira_layer = _lambda.LayerVersion(
            self,
            "JiraLayer",
            code=_lambda.Code.from_asset("layer/"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )
        # LAMBDA Function
        my_lambda = _lambda.Function(
            self,
            "JiraHandler",
            timeout=Duration.seconds(29),
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("Lambda"),
            layers=[jira_layer],
            handler="Jira.lambda_handler",
            role=lambda_role,
            reserved_concurrent_executions=1,
        )

        # Subscription
        topic.add_subscription(subscriptions.LambdaSubscription(my_lambda))

        # Eventbridge Rule
        rule = events.Rule(
            self,
            "SecurityHubRule",
            event_pattern=events.EventPattern(
                source=["aws.securityhub"],
                detail_type=["Security Hub Findings - Imported"],
                detail={"findings": {"Severity": {"Label": ["CRITICAL", "HIGH"]}}},
            ),
        )

        rule.add_target(event_targets.SnsTopic(topic))
