#ci/cd stages
StageName = {
    "ALPHA": "alpha",
    "BETA" : "beta",
    "PROD" : "prod"
}

#regions by name
RegionName = {
    "US-EAST-1" : "us-east-1",
    "US-EAST-2" : "us-east-2",
    "US-WEST-1" : "us-west-1",
    "US-WEST-2" : "us-west-2"
}

#replace key value pairs with your actual accounts
Accounts = {
    "PROD" : "346808235809",
    "ALPHA": "346808235809",
    "BETA": "346808235809"
}

#replace key value pairs with your actual ec2 pem file names with out the PEM extension
EC2_Keys = {
    "prod" : "seclab",
    "alpha": "seclab",
    "beta": "seclab"
}

# KMS Keys to be created in the KMS Stack
kms_services = ["s3", "ec2" ]

#Defien the Service prefix top create resource with a unique name: Stagename/service_prefix/service - prod/cdklab/mysql_secret
service_prefix = "cdklab"

#define the ip range and inbound ports for the Bastion host
bastion_inbound_ip = "0.0.0.0/24"
bastion_inbound_port = [ '22', '3389' ]

#VPC Settings for AZ to be utilized and the VPC CIR Range
vpc_max_az = 2
vpc_cidr = "10.0.0.0/16"

class AWSAccount:
    def __init__(self, stage, accountID, region) -> None:
        self.stage = stage
        self.accountID = accountID
        self.region = region

AWSPipeline = {
        StageName["PROD"] :  AWSAccount(StageName["PROD"], Accounts["PROD"], RegionName["US-EAST-1"]),
        StageName["ALPHA"] :  AWSAccount(StageName["ALPHA"], Accounts["ALPHA"], RegionName["US-WEST-1"]),  
        StageName["BETA"] :  AWSAccount(StageName["BETA"], Accounts["BETA"], RegionName["US-WEST-2"]),           
    }
