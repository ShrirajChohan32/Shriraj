from inspect import stack
from platform import architecture
from sys import path
from tkinter.tix import Tree
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns_subscriptions as subs,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_lambda as _lambda,
    aws_securityhub as securityhub,
    aws_events_targets as event_targets,
    aws_events as events,
    aws_sns_subscriptions as subscriptions,
)
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_lambda import LayerVersion, AssetCode
from constructs import Construct

class SechubStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "SecHubQueue",
            visibility_timeout=Duration.seconds(30),
            delivery_delay=Duration.seconds(31),
            receive_message_wait_time=Duration.seconds(20)
        )

            # Lambda Role
        lambda_role=iam.Role(
            self, 'lambda_role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            role_name='%sLambdaRole' %self.stack_name
        )
        # AWS Cloudwatch managed policy
        CloudWatchFullAccess = iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchFullAccess')

        lambda_role.add_managed_policy(CloudWatchFullAccess)

        # Secrets manager inline policy.
        
        lambda_role.add_to_policy(iam.PolicyStatement(
            actions=[
                'secretsmanager:GetSecretValue',
            ],
            effect=iam.Effect.ALLOW,
            resources=['arn:aws:secretsmanager:%s:%s:secret:/prod/*' 
            % (self.region, self.account)]))

        #Lambda Layers 
        jira_layer = _lambda.LayerVersion(self, "JiraLayer",
        code=_lambda.Code.from_asset('layer/'),
        compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
)
        #LAMBDA Function
        my_lambda = _lambda.Function(
            self, 'JiraHandler',
            timeout=Duration.seconds(29),
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('Lambda'),
            layers=[jira_layer],
            handler='Jira.lambda_handler',
            role=lambda_role,
            reserved_concurrent_executions=1
            )

        #EventBridge -> SQS -> LAMBDA trigger
        my_lambda.add_event_source(SqsEventSource(queue,
        batch_size=1, 
        max_batching_window=Duration.seconds(4)))


        # Eventbridge Rule 
        rule = events.Rule(self,"SecurityHubRule",
        event_pattern=events.EventPattern(source=['aws.securityhub'],
        detail_type=['Security Hub Findings - Imported'],
        detail={'findings':{'Severity':{'Label':['CRITICAL','HIGH']}}}))

        rule.add_target(event_targets.SqsQueue(queue))
