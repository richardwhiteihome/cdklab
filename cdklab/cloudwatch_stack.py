
from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_events as events,
    aws_cloudwatch_actions as cw_actions,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_cloudwatch as cloudwatch,
    aws_logs as logs
   )
import aws_cdk 
from aws_cdk import App, CfnOutput, NestedStack, NestedStackProps, Stack
from cdklab.config.stack_config import AWSPipeline, service_prefix
from constructs import Construct

"""
Stack that creates CloudWatch metrics, Alarm and Events Rule with a Target

Creates a Metric from an existing Metric CPUUtilization, creates an alarm and sends notification to a SNS Topic
Creates an Event Rule that monitors for Guard duty alerts and sends notification to a SNS Topic with a formatted message
"""
class cloudwatch_stack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, stage, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        acct_info = AWSPipeline[stage]
        region = acct_info.region
        stage = acct_info.stage
        account= acct_info.accountID


        Tags.of(self).add("Name",service_prefix+"_cloudwatch_alerts_"+stage)
        Tags.of(self).add("Stage", stage)
        Tags.of(self).add("Owner:Name", "SecurityTeam")
        Tags.of(self).add("Owner:ContactEmail", "SecurityTeam@email.com")
        Tags.of(self).add("Owner:BusinessUnit", "IT Security")
        Tags.of(self).add("Owner:CostCenter", "111")
        Tags.of(self).add("DataClassification", "Highly Confidential")
        Tags.of(self).add("Severity", "1")
        Tags.of(self).add("Compliance", "PCI")


        cpu_metric =  cloudwatch.Metric(
            namespace= "AWS/EC2",
            metric_name= 'CPUUtilization',
            dimensions_map= {  "stat": "Average"  }
            )
        

        cpualarm = cloudwatch.Alarm(self,"cpu_alarm",
            metric=cpu_metric,
            alarm_name=service_prefix+" CPU High Alarm",
            threshold= 70,
            evaluation_periods= 1,
            datapoints_to_alarm= 1,
            # period=aws_cdk.Duration.minutes(5),
            alarm_description="A Alarm to send an sns message if CPU goes above 70 percent"
        )

        sns_topic = sns.Topic.from_topic_arn(self, "getsnstopic","arn:aws:sns:"+region+":"+account+":medium_alert")

        cpualarm.add_alarm_action(cw_actions.SnsAction(sns_topic) )

        #Transform for message text to be added to the alert
        ruleTargetText = "The alert in ${EventField.fromPath('$.detail.accountId')}' in region ${EventField.fromPath('$.detail.awsRegion')} for alert ${EventField.fromPath('$.detail.eventName')} " \



        #create rules with Targets
        rule1 = events.Rule(self, 'AWSGuardDutyEventReporting', 
        description='Creates a CloudWatch Event and SNS Push Notification for events triggered by AWS GuardDuty',
        rule_name='AWSGuardDutyEventReporting',
        enabled= True,
        event_pattern=events.EventPattern(
            source=['aws.guardduty'],
            detail_type= ['GuardDuty Finding']
        )
        )

        rule1.add_target(target=targets.SnsTopic(sns_topic, message=events.RuleTargetInput.from_text(ruleTargetText)))

        rule2 = events.Rule(self, 'DetectNetworkChangeEvents', 
        description= 'Publishes formatted network change events to an Alert',
        rule_name= 'DetectNetworkChangeEvents',
        enabled= True,
            event_pattern=events.EventPattern(
            source=['ec2'],
            detail_type=['AWS API Call via CloudTrail'],
            detail={ 
                "eventSource": ['ec2.amazonaws.com'],
                "eventName": ['AttachInternetGateway',
                            'AssociateRouteTable',
                            'CreateCustomerGateway',
                            'CreateInternetGateway',
                            'CreateRoute',
                            'CreateRouteTable',
                            'DeleteCustomerGateway',
                            'DeleteInternetGateway',
                            'DeleteRoute',
                            'DeleteRouteTable',
                            'DeleteDhcpOptions',
                            'DetachInternetGateway',
                            'DisassociateRouteTable',
                            'ReplaceRoute',
                            'ReplaceRouteTableAssociation']
            }
            
        ))


        rule2.add_target(target=targets.SnsTopic(sns_topic, message=events.RuleTargetInput.from_text(ruleTargetText)))


        rule3 = events.Rule(self, 'DetectCloudTrailChanges', 
        description= 'Publishes formatted CloudTrail change events to an Alert',
        rule_name= 'DetectCloudTrailChanges',
        enabled=True,
        event_pattern=events.EventPattern(
            source= ['ec2'],
            detail_type=['AWS API Call via CloudTrail'],
            detail= {
            "eventSource": ['ec2.amazonaws.com'],
            "eventName": [ 'CreateTrail',
                            'UpdateTrail',
                            'StopLogging',
                            'DeleteTrail',]
            }
        ))

    
        rule3.add_target(target=targets.SnsTopic(sns_topic, message=events.RuleTargetInput.from_text(ruleTargetText)))

        rule4 = events.Rule(self, 'DetectNetworkAclChanges', 
        description= 'Publishes formatted network ACL change events to an alert',
        rule_name= 'DetectNetworkAclChanges',
        enabled= True,
        event_pattern=events.EventPattern(
        source= ['ec2'],
        detail_type=['AWS API Call via CloudTrail'],
        detail= {
            "eventSource": ['ec2.amazonaws.com'],
            "eventName": [ 'CreateNetworkAcl',
                        'CreateNetworkAclEntry',
                        'DeleteNetworkAcl',
                        'DeleteNetworkAclEntry',
                        'ReplaceNetworkAclEntry',
                        'ReplaceNetworkAclAssociation',]
            }
        ))

        rule4.add_target(target=targets.SnsTopic(sns_topic, message=events.RuleTargetInput.from_text(ruleTargetText)))    
    
        rule5 = events.Rule(self, 'DetectCloudWatchLogsChanges', 
            description= 'Changes to Amazon CloudWatch',
            rule_name= 'DetectCloudWatchLogsChanges',
            enabled= True,
            event_pattern=events.EventPattern(
            source= ['aws.logs'],
            detail_type=['AWS API Call via CloudTrail'],
            detail= {
                "eventsource": ['logs.amazonaws.com'],
                "eventName": [ 'DeleteDestination',
                            'DeleteLogGroup',
                            'DeleteLogStream',
                            'DeleteRetentionPolicy',]
            }
        ))
    

        rule5.add_target(target=targets.SnsTopic(sns_topic, message=events.RuleTargetInput.from_text(ruleTargetText)))


        rule6 = events.Rule(self, 'DetectSecurityGroupChanges', 
            description= 'Publishes formatted security group change events to an Alert',
            rule_name= 'DetectSecurityGroupChanges',
            enabled= True,
            event_pattern=events.EventPattern(
            source= ['ec2'],
            detail_type=['AWS API Call via CloudTrail'],
            detail= {
                "eventsource":['ec2.amazonaws.com'],
                "eventName":  [ 'AuthorizeSecurityGroupIngress',
                            'AuthorizeSecurityGroupEgress',
                            'RevokeSecurityGroupIngress',
                            'RevokeSecurityGroupEgress',
                            'CreateSecurityGroup',
                            'DeleteSecurityGroup',]
            }
        ))


        rule6.add_target(target=targets.SnsTopic(sns_topic, message=events.RuleTargetInput.from_text(ruleTargetText)))

 




