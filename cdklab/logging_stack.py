from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_sns as sns,
    aws_cloudtrail as ctrail,
    aws_s3 as s3,
    aws_logs as logs
   )
import aws_cdk 
from aws_cdk import App, CfnOutput, NestedStack, NestedStackProps, Stack
from cdklab.config.stack_config import AWSPipeline, service_prefix
from constructs import Construct



"""
Stack that enables CloudTrail that sends logs to S3 and CloudWatch and creates three SNS Topics for notification
"""
class logging_stack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, stage, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        acct_info = AWSPipeline[stage]
        region = acct_info.region
        stage = acct_info.stage
        account= acct_info.accountID

        Tags.of(self).add("Name",service_prefix+"_logging_"+stage)
        Tags.of(self).add("Stage", stage)
        Tags.of(self).add("Owner:Name", "SecurityTeam")
        Tags.of(self).add("Owner:ContactEmail", "SecurityTeam@email.com")
        Tags.of(self).add("Owner:BusinessUnit", "IT Security")
        Tags.of(self).add("Owner:CostCenter", "111")
        Tags.of(self).add("DataClassification", "Highly Confidential")
        Tags.of(self).add("Severity", "1")
        Tags.of(self).add("Compliance", "PCI")


       
        high_alert =  sns.Topic(self, 'high_alert',
            display_name='high_alert',
            topic_name="high_alert"
        )

        medium_alert =  sns.Topic(self, 'medium_alert',
            display_name='medium_alert',
            topic_name="medium_alert"
        )

        informational_alert =  sns.Topic(self, 'informational_alert ',
            display_name='informational_alert ',
            topic_name="informational_alert"
        )

        

        # targetBucket = s3.Bucket(self, 'cloudtrail_lab_Bucket',
        #     versioned=True,
        #     bucket_key_enabled=True,
        #     encryption=True
        #     )

        targetBucket = s3.Bucket(self, 'CTBucket',
            versioned=False,
            public_read_access=False,
            encryption=s3.BucketEncryption.KMS_MANAGED
        
        )


        #Create new cloudtrail, send to cloudwatch for event alerting
        lab_ct = ctrail.Trail(self,service_prefix+'-CloudTrail-DO-NOT-DELETE', 
            send_to_cloud_watch_logs= True,
            cloud_watch_logs_retention=logs.RetentionDays.SIX_MONTHS,
            trail_name=service_prefix+'-CloudTrail-DO-NOT-DELETE',
            bucket= targetBucket,
        )


    