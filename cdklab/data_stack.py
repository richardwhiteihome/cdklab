from webbrowser import GenericBrowser
from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_iam as iam,
    aws_secretsmanager as secrets,
    aws_rds as rds,
    aws_kms as kms,
    aws_ec2 as ec2,


    
    
   )
import aws_cdk 
import json
from aws_cdk import App, CfnOutput, NestedStack, NestedStackProps, Stack
from cdklab.config.stack_config import EC2_Keys, AWSPipeline, bastion_inbound_ip, bastion_inbound_port, service_prefix
from constructs import Construct

"""
Stack that creates RDS Instance, encrypts the data with a CMK Key and uses Secrets manager Credentials

Creates a KMS Key with Policy for encrypting RDS Data
Creates an RDS MySQl Instance with Credentials provided by Secrets manager
Retrieved Credentials from Secrets Manager and attached to Secrets manager for Credential management

"""
class data_stack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, stage, vpc,web_sg, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        acct_info = AWSPipeline[stage]
        region = acct_info.region
        stage = acct_info.stage
        account= acct_info.accountID

        Tags.of(self).add("Name","data_instance_"+stage)
        Tags.of(self).add("Stage", stage)
        Tags.of(self).add("Owner:Name", "SecurityTeam")
        Tags.of(self).add("Owner:ContactEmail", "SecurityTeam@email.com")
        Tags.of(self).add("Owner:BusinessUnit", "IT Security")
        Tags.of(self).add("Owner:CostCenter", "111")
        Tags.of(self).add("DataClassification", "Highly Confidential")
        Tags.of(self).add("Severity", "1")
        Tags.of(self).add("Compliance", "PCI")

     
        strService = 'kms:ViaService:rds.'+ region
        strCallerAccount = strService+':CallerAccount:'+ account
        strPrincipalAccount =  'arn:aws:iam::'+ account+':root'

        kmsstatement = iam.PolicyStatement(
            actions= ['kms:DescribeKey', 
                'kms:Encrypt',
                'kms:Decrypt',
                'kms:ReEncrypt',
                'kms:GenerateDataKey',                ],
            resources=[strService, strCallerAccount],
            principals=[ iam.ArnPrincipal(strPrincipalAccount)],
        )

        prstatement = iam.PolicyStatement(
            actions=[ "kms:*"],
            resources=['*'],
            principals=[iam.ArnPrincipal(strPrincipalAccount)]
        )

        KMSPolicy = iam.PolicyDocument()

        KMSPolicy.add_statements(prstatement)
        KMSPolicy.add_statements(kmsstatement)

        kmskey = kms.Key(self, 'KMSKey' ,
                removal_policy=aws_cdk.RemovalPolicy.DESTROY,
                alias=stage+'/rds_kms/cdklab',
                # trust_account_identities=True,
                description='KMS key for encrypting the objects in RDS',
                enable_key_rotation=True,
                policy=KMSPolicy
                )



        my_secret = rds.Credentials.from_generated_secret("mysql_admin", secret_name=stage+"/"+service_prefix+"/cdklab")

        db = rds.DatabaseInstance(self, "Instance",
                engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0_28),
                vpc=vpc,
                multi_az=True,
                instance_identifier=stage+"-cdklab",
                instance_type=  ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL),
                credentials=my_secret,
                storage_encryption_key=kmskey,
                database_name="cdklab",
                vpc_subnets={
                    "subnet_type": ec2.SubnetType.PRIVATE_ISOLATED
                },
                publicly_accessible=False
            )

        db.connections.allow_default_port_from(web_sg, "Web Security Group")

        # for asg_sg in asg_security_groups:
        #     db.connections.allow_default_port_from(asg_sg, "EC2 Autoscaling Group access MySQL")
