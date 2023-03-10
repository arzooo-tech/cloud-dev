#!/usr/bin/env python3

import boto3
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


#client = boto3.client('ecs', region_name= region)


# Method for check is ecs service exists using service ARNs
def checkIfServiceExists(ecsServiceName: str, ecsClusterName: str, region: str, awsAccountID: str):
    """_summary_

    Args:
        ecsServiceName (str): Name of the ecs service to be created
        ecsClusterName (str): Name of the ecs cluster in which service will be created
        region (str): Region in which firelens will be created
        awsAccountID (str): AWS Account ID

    Returns:
        _type_: If ECS Service exists
    """
    client = boto3.client('ecs', region_name= region)
    response = client.list_services(
        cluster = ecsClusterName,
        launchType = 'FARGATE'
    )
    ecsServiceARN = 'arn:aws:ecs:' + region + ':' + awsAccountID + ':service/' + ecsClusterName + '/' + ecsServiceName
    service_arns = response['serviceArns']
    if ecsServiceARN in service_arns:
        return True
    else:
        return False

# Method to create ecs service
def createService(ecsServiceName: str, taskDefinitionName: str, targetGroupArn: str, containerName: str, containerPort: int, userEmail: str, ecsClusterName: str, subnetID: str, securityGroupID: str, region: str):
    """_summary_

    Args:
        ecsServiceName (str): Name of the service getting deployed
        taskDefinitionName (str): Name of the task definition to be used for service
        targetGroupArn (str): Target group to use for service
        containerName (str): Name of the contianer
        containerPort (int): Port on which container runs
        ecsClusterName (str): Port on which container runs
        subnetID (str): Subnet in which ecs service will be running
        securityGroupID (str): Security group to be used for ecs services

    Returns:
        _type_: ECS service details
    """
    client = boto3.client('ecs', region_name= region)
    try:
        response = client.create_service(
            cluster = ecsClusterName,
            serviceName = ecsServiceName,
            taskDefinition = taskDefinitionName,
            desiredCount = 1,
            launchType = 'FARGATE',
            loadBalancers = [
                {
                    'targetGroupArn': targetGroupArn,
                    'containerName': containerName,
                    'containerPort': containerPort
                },
            ],
            networkConfiguration = {
                'awsvpcConfiguration': {
                    'subnets': [subnetID],
                    'securityGroups': [securityGroupID],
                    'assignPublicIp': 'ENABLED'
                }
            },
            tags = [
                {
                    'key': 'Name',
                    'value': ecsServiceName
                },
                {
                    'key': 'pod',
                    'value': 'cloud-dev'
                },
                {
                    'key': 'userName',
                    'value':userEmail
                },
            ],
            propagateTags = 'TASK_DEFINITION'
        )
        serviceName = response['service']['serviceName']
        serviceARN = response['service']['serviceArn']
        return serviceName, serviceARN
    
        
    except Exception as e:
        print(str(e))
        return False

# Method to delete ECS Service
def deleteEcsService(serviceName: str, ecsClusterName: str, region: str):
    """_summary_

    Args:
        serviceName (str): Name of the service to be deleted
        ecsClusterName (str): ECS Cluster name
    """
    client = boto3.client('ecs', region_name= region)
    try:
        response = client.delete_service(
            cluster = ecsClusterName,
            service = serviceName,
            force=True
        )
        serviceName = response['service']['serviceName']
        return True
    
    except Exception as e:
        print(str(e))
        return False

# Method to update existing ECS Service
def updateECSService(ecsServiceName: str, taskDefinitionARN: str, ecsClusterName: str, region: str):
    """_summary_

    Args:
        serviceName (str): Name of the service to be updated
        taskDefinitionARN (str): ARN of the task definition to be updated
    """
    client = boto3.client('ecs', region_name= region)
    try:
        response = client.update_service(
            cluster = ecsClusterName,
            service = ecsServiceName,
            taskDefinition = taskDefinitionARN,
            forceNewDeployment = True
        )
        
        serviceName = (response['service']['serviceName'])
        return True
    
    except Exception as e:
        print(str(e))
        return False

