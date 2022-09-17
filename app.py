#!/usr/bin/env python3
import os

from aws_cdk import (
    Duration,
    Stack,
    Tags,
   )
import aws_cdk 


from constructs import Construct


from cdklab.config.stack_config import AWSPipeline

from cdklab.infrastructure_stack import infrastructure_stack
from cdklab.compute_stack import compute_stack

from cdklab.kms_stack import kms_stack
from cdklab.logging_stack import logging_stack
from cdklab.data_stack import data_stack
from cdklab.cloudwatch_stack import cloudwatch_stack

app = aws_cdk.App()
acct_info = AWSPipeline["prod"]

region = acct_info.region
stage = acct_info.stage
account = acct_info.accountID


main_stack = aws_cdk.Stack(app, 'MainStack', env={'region': region, 'account': account})

infrastack = infrastructure_stack(main_stack, "infrastructureStack", stage=stage)
computestack = compute_stack(main_stack, "ComputeStack", stage, vpc=infrastack.vpc,)
kmsstack = kms_stack(main_stack, "KmsStack", stage=stage, vpc=infrastack.vpc,)
dataStack = data_stack(main_stack, "DataStack", stage=stage, vpc=infrastack.vpc, web_sg=computestack.web_security_group )
loggingstack = logging_stack(main_stack, "LoggingStack", stage=stage,)
cloudwatchstack = cloudwatch_stack(main_stack, "cloudwatchStack", stage=stage ,)

app.synth()
