#!/usr/bin/env python3

import boto3
import logging


region = 'ap-south-1'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = boto3.client('ecs', region_name= region)
            
            
def createTaskDefinition(ecsTaskDefinitionName: str, containerName: str, dockerImage: str, appName: str, containerPort: int, userEmail: str, secretName: str, awsAccountId: str, iamRoleNameForEcsTasks: str, iamExecutionRoleName: str, elasticSearchEndpointForLogs: str, elastciUserName: str, elasticPassowrd: str, region: str):
    """_summary_

    Args:
        ecsTaskDefinitionName (str): Name of the task definition
        containerName (str): Name of the conatiner
        dockerImage (str): Docker image 
        appName (str): Name of the app being deployed 
        containerPort (int): Port on which container runs
        userEmail (str): User email to tag it to resources
        secretName (str): Name of the secret from secret manager to be used for inheriting
        awsAccountId (str): AWS Account ID
        iamRoleNameForEcsTasks (str): Name of the IAM role to be used for tasks 
        iamExecutionRoleName (str): Name of the IAM role for execution 
        elasticSearchEndpointForLogs (str): Endpoint for pushing logs to elasticsearch 
        elastciUserName (str): UserName of the elastic
        elasticPassowrd (str): Password of the elastic
        region (str): Region in which firelens will be used for logs 

    Returns:
        _type_: _description_
    """
    dockerImage = dockerImage + ':latest'
    try:
        response = client.register_task_definition(
            family = ecsTaskDefinitionName,
            taskRoleArn = 'arn:aws:iam::' + awsAccountId + ':role/' + iamRoleNameForEcsTasks,
            executionRoleArn = 'arn:aws:iam::' + awsAccountId + ':role/' + iamExecutionRoleName,
            networkMode = 'awsvpc',
            cpu ='256',
            memory ='512',
            tags = [
                {
                    'key': 'pod',
                    'value': 'cloud-dev'
                },
                {
                    'key': 'Name',
                    'value': ecsTaskDefinitionName
                },
                {
                    'key': 'userName',
                    'value': userEmail
                },
            ],
            runtimePlatform = {
                'cpuArchitecture': 'X86_64',
                'operatingSystemFamily': 'LINUX'
            },
            requiresCompatibilities = [
                'FARGATE'
            ],
            containerDefinitions = [
                {
                    'name': containerName,
                    'image': dockerImage,
                    'portMappings': [
                        {
                            'containerPort': containerPort,
                            'protocol': 'tcp'
                        },
                    ],
                    'essential': True,
                    'environment': [
                        {
                            'name': 'ENVIRONMENT_KEY',
                            'value': secretName
                        }
                    ],
                    'logConfiguration': {
                        'logDriver': 'awsfirelens',
                        'options': {                            
                            'Name': 'es',
                            'Time_Key': '@timestamp',
                            'Port': '9200',
                            'Logstash_Prefix': appName,
                            'Host': elasticSearchEndpointForLogs,
                            'Index': appName,
                            'Logstash_DateFormat': '%Y.%m.%d',
                            'Logstash_Format': 'true',
                            'Time_Key_Format': '%Y-%m-%dT%H:%M:%S',
                            'Type': '_doc',
                            'HTTP_User': elastciUserName,
                            'HTTP_Passwd': elasticPassowrd
                        }
                    }
                },
                # log router container 
                {
                    'name': 'log_router',
                    'image': '906394416424.dkr.ecr.ap-south-1.amazonaws.com/aws-for-fluent-bit:latest',
                    'essential': True,
                    'firelensConfiguration': {
                        'type': 'fluentbit'
                    },
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options':{
                            "awslogs-group": "firelens-container",
                            "awslogs-region": "ap-south-1",
                            "awslogs-create-group": "true",
                            "awslogs-stream-prefix": "firelens"
                        }                        
                    }
                }
                
            ]
        )
        
        taskDefinitionARN = (response['taskDefinition']['taskDefinitionArn'])
        taskDefinitionName = taskDefinitionARN.split('/')[1].split(':')[0]
        return taskDefinitionARN, taskDefinitionName
    
    except Exception as e:
        print(str(e))
        return False


def updateTaskDefinition(ecsTaskDefinitionName: str, containerName: str, dockerImage: str, appName: str, containerPort: int, userEmail: str, secretName: str, awsAccountId: str, iamRoleNameForEcsTasks: str, iamExecutionRoleName: str, elasticSearchEndpointForLogs: str, elastciUserName: str, elasticPassowrd: str, region: str):
    """_summary_

    Args:
        ecsTaskDefinitionName (str): task definition name to be formed from username
        containerName (str): name of the container
        dockerImage (str): docker image tag 
        appName (str): name of the service to be derived from username
        containerPort (int): Port on which container runs
        userEmail (str): User email to tag it to resources
        secretName (str): Name of the secret from secret manager to be used for inheriting
        awsAccountId (str): AWS Account ID
        iamRoleNameForEcsTasks (str): Name of the IAM role to be used for tasks 
        iamExecutionRoleName (str): Name of the IAM role for execution 
        elasticSearchEndpointForLogs (str): Endpoint for pushing logs to elasticsearch 
        elastciUserName (str): UserName of the elastic
        elasticPassowrd (str): Password of the elastic
        region (str): Region in which firelens will be used for logs 

    Returns:
        task definition arn (str): task definition arn which is created
    """
    dockerImage = dockerImage + ':latest'
    try:
        response = client.register_task_definition(
            family = ecsTaskDefinitionName,
            taskRoleArn = 'arn:aws:iam::' + awsAccountId + ':role/' + iamRoleNameForEcsTasks,
            executionRoleArn = 'arn:aws:iam::' + awsAccountId + ':role/' + iamExecutionRoleName,
            networkMode = 'awsvpc',
            cpu ='256',
            memory ='512',
            tags = [
                {
                    'key': 'pod',
                    'value': 'cloud-dev'
                },
                {
                    'key': 'Name',
                    'value': ecsTaskDefinitionName
                },
                {
                    'key': 'userName',
                    'value': userEmail
                },
            ],
            runtimePlatform = {
                'cpuArchitecture': 'X86_64',
                'operatingSystemFamily': 'LINUX'
            },
            requiresCompatibilities = [
                'FARGATE'
            ],
            containerDefinitions = [
                {
                    'name': containerName,
                    'image': dockerImage,
                    'portMappings': [
                        {
                            'containerPort': containerPort,
                            'protocol': 'tcp'
                        },
                    ],
                    'essential': True,
                    'environment': [
                        {
                            'name': 'ENVIRONMENT_KEY',
                            'value': secretName
                        }
                    ],
                    'logConfiguration': {
                        'logDriver': 'awsfirelens',
                        'options': {                            
                            'Name': 'es',
                            'Time_Key': '@timestamp',
                            'Port': '9200',
                            'Logstash_Prefix': appName,
                            'Host': elasticSearchEndpointForLogs,
                            'Index': appName,
                            'Logstash_DateFormat': '%Y.%m.%d',
                            'Logstash_Format': 'true',
                            'Time_Key_Format': '%Y-%m-%dT%H:%M:%S',
                            'Type': '_doc',
                            'HTTP_User': elastciUserName,
                            'HTTP_Passwd': elasticPassowrd
                        }
                    }
                },
                # log router container 
                {
                    'name': 'log_router',
                    'image': '906394416424.dkr.ecr.ap-south-1.amazonaws.com/aws-for-fluent-bit:latest',
                    'essential': True,
                    'firelensConfiguration': {
                        'type': 'fluentbit'
                    },
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options':{
                            "awslogs-group": "firelens-container",
                            "awslogs-region": region,
                            "awslogs-create-group": "true",
                            "awslogs-stream-prefix": "firelens"
                        }                        
                    }
                }
                
            ]
        )
        
        taskDefinitionARN = (response['taskDefinition']['taskDefinitionArn'])
        taskDefinitionName = taskDefinitionARN.split('/')[1].split(':')[0]
        return taskDefinitionARN, taskDefinitionName
    
    except Exception as e:
        print(str(e))
        return False


# def deRegisterTaskDefinition(*taskDefinitionARN: str):
#     """_summary_

#     Args:
#         taskDefinitionARN (str): ARN of task definition
#     """
#     try:
#         deRegisterTaskDefinitionResponse = client.deregister_task_definition(
#             taskDefinition = taskDefinitionARN
#         )
#         return True
    
#     except Exception as e:
#         print(str(e))
#         return False
    
def deRegisterTaskDefinition(taskDefinitionARNs: list):
    
    """_summary_

    Args:
        taskDefinitionARN (str): ARN of task definition
    """
    for taskDefinitionARN in taskDefinitionARNs:
        try:
            deRegisterTaskDefinitionResponse = client.deregister_task_definition(
                taskDefinition = taskDefinitionARN
            )
        except Exception as e:
            print(str(e))
            return False
    return True
        

def listTaskDefinitionARNS(taskDefinitionName: str):
    """_summary_

    Args:
        taskDefinition (str): Name of the task definition

    Returns:
        _type_: _description_
    """
    response = client.list_task_definitions(familyPrefix=taskDefinitionName)
    task_definition_arns = response['taskDefinitionArns']
    return task_definition_arns
    
