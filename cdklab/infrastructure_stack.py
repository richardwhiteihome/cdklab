from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_ssm as ssm,
    aws_ec2 as ec2,
   )
import aws_cdk 
from aws_cdk import App, CfnOutput, NestedStack, NestedStackProps, Stack
from cdklab.config.stack_config import vpc_cidr, service_prefix, vpc_max_az, AWSPipeline

from constructs import Construct

"""
Stack that creates VPC Infrastructure, Internet Gateway, public and private subnets, NAT Gateway
Sets the following Attributes:
            cidr = '10.0.0.0/16',
            max_azs = 2,
            enable_dns_hostnames = True,
            enable_dns_support = True


"""
class infrastructure_stack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, stage,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        acct_info = AWSPipeline[stage]
        stage = acct_info.stage
        
        Tags.of(self).add("Name",service_prefix+"_vpc_"+stage)
        Tags.of(self).add("Stage", stage)
        Tags.of(self).add("Owner:Name", "SecurityTeam")
        Tags.of(self).add("Owner:ContactEmail", "SecurityTeam@email.com")
        Tags.of(self).add("Owner:BusinessUnit", "IT Security")
        Tags.of(self).add("Owner:CostCenter", "111")
        Tags.of(self).add("DataClassification", "Highly Confidential")
        Tags.of(self).add("Severity", "1")
        Tags.of(self).add("Compliance", "PCI")



        self.vpc = ec2.Vpc(self, service_prefix+'_labvpc',
            cidr = vpc_cidr,
            max_azs = vpc_max_az,
            enable_dns_hostnames = True,
            enable_dns_support = True, 
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name = 'Public-Subnet',
                    subnet_type = ec2.SubnetType.PUBLIC,
                    cidr_mask = 24
                ),
                ec2.SubnetConfiguration(
                    name = 'Private-Subnet',
                    subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask = 24
                ),
                ec2.SubnetConfiguration(
                    name = 'Isolated-Subnet',
                    subnet_type = ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask = 28
                )
            ],
            nat_gateways = 1,

        )

        self.vpc.add_flow_log("FlowLogCloudWatch",
            traffic_type=ec2.FlowLogTrafficType.ALL
        )

        # priv_subnets = [subnet.subnet_id for subnet in self.vpc.private_subnets]

        # count = 1
        # for psub in priv_subnets: 
        #     ssm.StringParameter(self, 'private-subnet-'+ str(count),
        #         string_value = psub,
        #         parameter_name = '/private-subnet-'+str(count)
        #         )
        #     count += 1 




