#!/usr/bin/env python3

import boto3
import logging


region = 'ap-south-1'

# Define the custom logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# define the boto client
client = boto3.client('elbv2', region_name= region)


def createTargetGroup(targetGroupName: str, port: int, healthCheckPath: str, userEmail: str, vpcId: str):
    """ Method to create target group
    
    Args:
        serviceName (str): Name of the service getting deployed
        port (str): The port on which the targets receive traffic.
        healthCheckPath (str): The destination for health checks on the targets
        vpcId (str): VPC ID where resources will be created in AWS
        
    Returns:
        task definition arn (str): ARN of the target group created
        task definition name(str): Name of the target group created
        
    """
    try:
        response = client.create_target_group(
            Name = targetGroupName,
            Protocol = 'HTTP',
            ProtocolVersion='HTTP1',
            Port = port,
            VpcId = vpcId,
            HealthCheckProtocol = 'HTTP',
            HealthCheckPort = str(port),
            HealthCheckEnabled = True,
            HealthCheckPath = '/' + healthCheckPath,
            # Default health attributes on target group feel free to change based on type of applications
            HealthCheckIntervalSeconds=120,
            HealthCheckTimeoutSeconds=60,
            HealthyThresholdCount=3,
            UnhealthyThresholdCount=2,
            Matcher={
                'HttpCode': '200'
            },
            TargetType='ip',
            Tags=[
                    {
                    'Key': 'Name',
                    'Value': targetGroupName
                    },
                    {
                    'Key': 'pod',
                    'Value': 'cloud-dev'
                    },
                    {
                    'Key': 'userName',
                    'Value': userEmail
                    },
                ],
            IpAddressType='ipv4'
        )
        
        targetGroupARN =  response['TargetGroups'][0]['TargetGroupArn']
        targetGroupName = response['TargetGroups'][0]['TargetGroupName']
        return targetGroupARN, targetGroupName
    
        
    except Exception as e:
        print(str(e))
        return False


def getTargetGroupARN(targetGroupName: str):
    """_summary_

    Args:
        targetGroupName (str): Name of the target group
    """
    try:
        response = client.describe_target_groups(
        Names=[targetGroupName]
        )   
        target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
        return target_group_arn
    except Exception as e:
        print(str(e))
        return False
    
#print(getTargetGroupARN('arzooo-be-test-som'))
    
def deleteTargetGroup(targetGroupARN: str):
    """_summary_

    Args:
        targetGroupARN (str): ARN of target group
    """
    try:
        deleteTargetGroupResponse = client.delete_target_group(
            TargetGroupArn = targetGroupARN
        )
        
        deleteTargetGroupStatusCode = deleteTargetGroupResponse['ResponseMetadata']['HTTPStatusCode']
        return deleteTargetGroupStatusCode
    
    except Exception as e:
        print(str(e))
    
