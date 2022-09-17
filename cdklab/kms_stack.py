from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_kms as kms,
    aws_iam as iam,
    aws_secretsmanager as secrets,

   )
import aws_cdk 
from aws_cdk import App, CfnOutput, NestedStack, NestedStackProps, Stack
from cdklab.config.stack_config import AWSPipeline, kms_services, service_prefix
from constructs import Construct
"""
Stack that creates CMK KMS keys from a list for basic
Functionality for most common services
  * kms:DescribeKey
  * kms:Encrypt
  * kms:Decrypt
  * kms:ReEncrypt
  * kms:GenerateDataKey

Creates a KMS Key with Policy for encrypting AWS Services and assigning priviledges to manage
The key list is configured from a list in the cdklab/config/stack_config.py, kms_services
"""
class kms_stack(NestedStack):

    def __init__(self, scope: Construct, id: str, stage, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        acct_info = AWSPipeline[stage]
        region = acct_info.region
        stage = acct_info.stage
        account= acct_info.accountID

        Tags.of(self).add("Name",service_prefix+"_kms_"+stage)
        Tags.of(self).add("Stage", stage)
        Tags.of(self).add("Owner:Name", "SecurityTeam")
        Tags.of(self).add("Owner:ContactEmail", "SecurityTeam@email.com")
        Tags.of(self).add("Owner:BusinessUnit", "IT Security")
        Tags.of(self).add("Owner:CostCenter", "111")
        Tags.of(self).add("DataClassification", "Highly Confidential")
        Tags.of(self).add("Severity", "1")
        Tags.of(self).add("Compliance", "PCI")



        kmsservices = kms_services
      
        for entry in kmsservices:

            pService = entry

            strService = 'kms:ViaService:'+pService+'.'+ region
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

            kmskey = kms.Key(self, pService+'Key' ,
                    removal_policy=aws_cdk.RemovalPolicy.DESTROY,
                    alias=stage+'/lab_'+pService,
                    # trust_account_identities=True,
                    description='KMS key for encrypting the objects in '+pService,
                    enable_key_rotation=True,
                    policy=KMSPolicy
                    )



            CfnOutput(self, pService+'_key-arn',value=kmskey.key_arn)
