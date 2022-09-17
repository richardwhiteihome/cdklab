from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elb,
    aws_ec2 as ec2,
    aws_certificatemanager as cert_manager,
    
    
   )
import aws_cdk 
from aws_cdk import App, CfnOutput, NestedStack, NestedStackProps, Stack
from cdklab.config.stack_config import EC2_Keys, AWSPipeline, bastion_inbound_ip, bastion_inbound_port, service_prefix
from constructs import Construct

# linux_ami = ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX,
#                                  edition=ec2.AmazonLinuxEdition.STANDARD,
#                                  virtualization=ec2.AmazonLinuxVirt.HVM,
#                                  storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
#                                  )  

linux_ami = ec2.MachineImage.latest_amazon_linux(
            edition=ec2.AmazonLinuxEdition.STANDARD,
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )




with open("./user_data/user_data.sh") as f:
    user_data = f.read()

"""
Stack that creates Compute resources that are launched from a Load Balancer

Bastion host for access in Public subnet an set security group to allow only port 22
Application Load Balancer in Public subnet
Auto Scaling Group in Private subnet that launches pre-defined AMI’s with desired_capacity=1,
min_capacity=1,
max_capacity=3
and set security group to allow only port 22 and 80

"""
class compute_stack(NestedStack):

    def __init__(self, scope: Construct, id: str, stage, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        acct_info = AWSPipeline[stage]
        stage = acct_info.stage

        Tags.of(self).add("Name","ec2_instance_"+stage)
        Tags.of(self).add("Stage", stage)
        Tags.of(self).add("Owner:Name", "SecurityTeam")
        Tags.of(self).add("Owner:ContactEmail", "SecurityTeam@email.com")
        Tags.of(self).add("Owner:BusinessUnit", "IT Security")
        Tags.of(self).add("Owner:CostCenter", "111")
        Tags.of(self).add("DataClassification", "Highly Confidential")
        Tags.of(self).add("Severity", "1")
        Tags.of(self).add("Compliance", "PCI")


        # Setup key_name for EC2 instance login 
        key_name = EC2_Keys[stage]
        ec2_type = "t2.micro"

        # security_group = ec2.SecurityGroup.from_security_group_id(self, "BastionSecurityGroup", "BastionSecurityGroup",
        #     mutable=False,

        # )
        security_group = ec2.SecurityGroup(self, "BastionSecurityGroup", 
                vpc=vpc,
                security_group_name="BastionSecurityGroup",
                description="Bastion Security Group")


        for entry in bastion_inbound_port:
           security_group.add_ingress_rule(ec2.Peer.ipv4(bastion_inbound_ip), ec2.Port.tcp(int(entry)), "Internet access ")


        # Create Bastion
        bastion = ec2.BastionHostLinux(self, service_prefix+"_Bastion",
                                       vpc=vpc,
                                       subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                       instance_name="myBastionHostLinux",
                                       instance_type=ec2.InstanceType(instance_type_identifier=ec2_type))
        bastion.instance.instance.add_property_override("KeyName", key_name),
        bastion.connections.add_security_group(security_group)


        with open("./user_data/user_data.sh") as f:
            user_data = f.read()


        # Create Web server
        webServer = ec2.Instance(self, service_prefix+"_EC2",
                            instance_type=ec2.InstanceType(
                                instance_type_identifier=ec2_type),
                            instance_name=service_prefix+"_webserver_"+stage,
                            machine_image=linux_ami,
                            vpc=vpc,
                            key_name=key_name,
                            vpc_subnets=ec2.SubnetSelection(
                                subnet_type=ec2.SubnetType.PUBLIC),
                            user_data=ec2.UserData.custom(user_data)
                            )

        self.web_security_group = ec2.SecurityGroup(self, "WebSecurityGroup", 
                vpc=vpc,
                security_group_name="WebSecurityGroup",
                description="Web Security Group")

        self.web_security_group.add_ingress_rule(ec2.Peer.ipv4(bastion_inbound_ip), ec2.Port.tcp(443), "Internet access ")
        webServer.add_security_group(self.web_security_group)



        # webServer.connections.allow_from_any_ipv4(ec2.Port.tcp(22), "Internet access SSH")
        # webServer.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Internet access https")
        # webServer.connections.allow_from_any_ipv4(ec2.Port.tcp(443), "Internet access https")
        
