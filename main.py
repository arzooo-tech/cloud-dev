#!/usr/bin/env python3

# Modules 
import boto3
import os
import sys
import logging
import argparse
import re 
import random
from simple_colors import *


# Custom imports 
from taskDefinition import taskDefinition
from targetGroup import targetGroup
from route53 import route53
from loadBalancer import loadBalancer
from service import ecsService
from application import application
from healthCheck import healthChecks
from kibana import kibana
from secretManager import secretManager


# Global variables
region = "ap-south-1"

# Global configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# User inputs 
parser = argparse.ArgumentParser(description ='Cloud-dev -- On-demand Testing env')
parser.add_argument('email', type=str, help='Please enter your email address')
parser.add_argument('appName', type=str, help='Name of the service/app being deployed')
parser.add_argument('containerPort', type=int, help='Port on which app will be running')
parser.add_argument('healthCheckPath', type=str, help='Health check path for app')
parser.add_argument('gitRepoName', type=str, help='git Repo name')
parser.add_argument('branchName', type=str, help='Name of the branch to be used for building')
parser.add_argument('secretName', type=str, help='Name of the secret in secret maanger to be copied values from')
parser.add_argument('operation', type=str, help='Operation to be performed allowed values are [create, update, delete]')
parser.add_argument('companyEmailDomain', type=str, help='Email domain against which this needs to be validated')
parser.add_argument('ecsClusterName', type=str, help='Name of the ECS Cluster where all these ECS workloads will be running')
parser.add_argument('region', type=str, help='Region in which all ECS workloads will be running ')
parser.add_argument('awsAccountID', type=str, help='AWS Account ID in which all these resources will be running')
parser.add_argument('HostedZoneId', type=str, help='ID of the Hosted Zone from Route 53 Console under which all domains for these will be created')
parser.add_argument('githubOrgName', type=str, help='Name of the github organization under which projects are present')
parser.add_argument('iamRoleNameForEcsTasks', type=str, help='IAM Role name to be used for tasks Name to be passed NOT ARN of the IAM Role')
parser.add_argument('iamExecutionRoleName', type=str, help='Name of the IAM Execution role name to be passed NOT ARN of the IAM Role')
parser.add_argument('elasticSearchEndpointForLogs', type=str, help='Endpoint of elastic search where logs will be published')
parser.add_argument('elastciUserName', type=str, help='User name for elastic search')
parser.add_argument('elasticPassowrd', type=str, help='Password for elastic')
parser.add_argument('vpcId', type=str, help='AWS VPC Id in which all resources will be created')
parser.add_argument('domainNameOfHostedZone', type=str, help='Route53 hosted zone name under which all records will be created')
parser.add_argument('loadBalancerDNSEndpoint', type=str, help='DNS of load balancer in which all the rules for hosts will be created which will be mapped in route53 alias record PS: Single load balancer is being used for all hosts being created by this project')
parser.add_argument('AWSHostedZoneIDForLoadbalancerRegionBasis', type=str, help='AWS Has fixed hosted zone id for different type of Load balancer based on region that value to be passed details here https://docs.aws.amazon.com/general/latest/gr/elb.html')
parser.add_argument('HTTTPSListenerARN', type=str, help='HTTPS Listener ARN of load balancer ')
parser.add_argument('HTTPListenerARN', type=str, help='HTTP Listener ARN of load balancer')
parser.add_argument('subnetID', type=str, help='Subnet Id in which workloads will run')
parser.add_argument('securityGroupID', type=str, help='Security group ID to be used for ecs')
parser.add_argument('kibanaURL', type=str, help='URL of kibana where application will be published')
args = parser.parse_args()


# Check if aws creds exists in env
def checkIfEnvExists():
    try:
        if os.environ["AWS_ACCESS_KEY_ID"] and os.environ["AWS_SECRET_ACCESS_KEY"]:
            #logger.info(" Found aws creds in env proceeding further")
            return True
        else:
            #logger.error(" Could not find aws creds in env exiting")
            return False
    except Exception as e:
        logger.error(" Could not find aws creds in env exiting")
        return False

# Check if user email address is valid
def validateEmail(email: str, companyEmailDomain: str):
    fulleEmailDomain = email.split('@')[1].split('.')
    if fulleEmailDomain[0] == companyEmailDomain and fulleEmailDomain[1] == 'com':
        return True
    else:
        return False
    
# Get username for using it in naming
def getUserName(email: str):
    userNameFull = email.split('@')[0]
    UserNameFiltered = re.sub('\W+','', userNameFull)       # Remove special characters from username if any special characters are not allowed in task definition name
    return UserNameFiltered

# Main function
def main():
    # Validate user email address
    emailValidated = validateEmail(args.email, args.companyEmailDomain)
    if emailValidated:
        logger.info(" Email address is valid proceeding")
    else:
        logger.error(" Please enter valid Email address")
        sys.exit()
    # Check if aws credentials are present in env
    credEnvCheck = checkIfEnvExists() 
    if credEnvCheck:
        logger.info(" Found aws creds in env proceeding further")
    else:
        logger.error(" Could not find aws creds in env exiting")
        sys.exit()
        
    # Get username to add in Task definition name
    userName = getUserName(args.email)
    
    
    if args.operation == 'create':
        # cloud-dev is the prefix with which all the taskdefinition will be created
        ecsTaskDefinitionName = 'cloud-dev' + '-' + userName + '-' + args.appName 
        secretName = 'cloud-dev' + '-' + userName + '-' + args.appName
        # Check if ecs service exists 
        checkIfEcsServiceExists = ecsService.checkIfServiceExists(ecsTaskDefinitionName, args.ecsClusterName, args.region, args.awsAccountID)
        if checkIfEcsServiceExists:
            logger.error(" ECS service with name {} already exists please consider using the same exiting".format(ecsTaskDefinitionName))
            sys.exit(1)
        else:
            logger.info(" Service does not exist proceeding with creating all ECS resources ")
            
        # Check if ECR Repo exists 
        checkIfECRRepoExistsResponse = application.checkIfECRRepoExists(args.appName, args.awsAccountID, args.region)
        if checkIfECRRepoExistsResponse:
            logger.error(" ECR Repo already exists with name of {} please consider using the same exiting".format(args.appName))
            sys.exit(1)
        else:
            logger.info(" ECR Repo does not exist proceeding")
        
        # Check if route 53 record exist 
        domainName = userName + '-' + args.appName 
        checkIfRouteRecordExistsResponse = route53.checkIfRouteRecordExists(domainName, args.HostedZoneId, args.region)
        if checkIfRouteRecordExistsResponse:
            logger.error(" DNS already exists with same name exiting")
            sys.exit(1)
        else:
            logger.info(" DNS Doesnot exist proceeding")
        
        
        clonedRepo = application.clone_repo(args.gitRepoName, args.branchName, args.githubOrgName)
        if clonedRepo:
            logger.info(" Cloned {} repo".format(args.gitRepoName))
            logger.info(" Building docker image ")
            dockerImageBuild = application.buildDockerImage(args.gitRepoName, args.appName)
            if dockerImageBuild:
                logger.info(" Image built with name of {}".format(args.appName))
                ecrRepoName, ecrRepoURI = application.createECRRepo(args.appName, args.email, args.awsAccountID, args.region)
                if ecrRepoName:
                    logger.info(" ECR repo created with name of {} ".format(ecrRepoName))
                    imagePushedToECR = application.pushImageToECR(ecrRepoName, args.appName, args.region)
                    if imagePushedToECR:
                        logger.info(" Pushed image to ecr")
                    else:
                        logger.error(" Unable to push image to ecr please check for error")
                else:
                    logger.error(" Unable to create ECR repo please check for error")
            else:
                logger.error(" Docker image build failed with error")
                sys.exit(1)
        else:
            logger.error(" Unable to clone repo please check for error")
            sys.exit(1)
        
        # Inherit and create new secret in secret manager
        #sourceSecretName = args.sourceSecretName    # This will be sent as parameter when all the services will be moved to secret manager
        createNewSecretSecretManager = secretManager.getAndCreateSecret(args.secretName, ecsTaskDefinitionName, args.email, args.region)
        if createNewSecretSecretManager:
            logger.info(" Secret has been created with name of {} in secret maanger".format(createNewSecretSecretManager))
        else:
            logger.error(" Unable to create secret in secret manager please check for error ")
            
        # create task definition
        ecsCreateTaskDefinitionResponse = taskDefinition.createTaskDefinition(ecsTaskDefinitionName, args.appName, ecrRepoURI, args.appName, args.containerPort, args.email, createNewSecretSecretManager, args.awsAccountID, args.iamRoleNameForEcsTasks, args.iamExecutionRoleName, args.elasticSearchEndpointForLogs, args.elastciUserName, args.elasticPassowrd, args.region)
        taskDefinitionARN, taskDefinitionName = ecsCreateTaskDefinitionResponse[0], ecsCreateTaskDefinitionResponse[1]
        if ecsCreateTaskDefinitionResponse:
            logger.info(" Task definition has been cretated with name of {}".format(ecsTaskDefinitionName))
        else:
            logger.error(" Unable to create task definition please check for error")
        
        # create target group
        targetGroupNameFull = userName + '-' + args.appName             # Target group will be created based on username and app name being passed 
        targetGroupNameShort = targetGroupNameFull[:31]                 # Target group names are allowed to have only 32 characters long hence restricting it to 32 characters 
        targetGroupNameShort = re.sub('[^a-zA-Z0-9 \n\.]', '', targetGroupNameShort)    # Remove any special characters from target as special character at the end is not allowed 
        createTargetGroupResponse = targetGroup.createTargetGroup(targetGroupNameShort, args.containerPort, args.healthCheckPath, args.email, args.vpcId, args.region)
        targetGroupARN, targetGroupNameShort  = createTargetGroupResponse[0], createTargetGroupResponse[1]
        if createTargetGroupResponse:
            logger.info(" Target group has been created with name of {} ".format(targetGroupNameShort))
        else:
            logger.error(" Unable to create target group please check for error ")
            sys.exit(1)
        
        # create R53 Entry
        domainName = targetGroupNameFull
        FullDomainName = domainName + '.' + args.domainNameOfHostedZone
        createRoute53Response = route53.createR53Entry(domainName, args.domainNameOfHostedZone, args.HostedZoneId, args.loadBalancerDNSEndpoint, args.AWSHostedZoneIDForLoadbalancerRegionBasis, args.region)
        if createRoute53Response:
            logger.info(" Domain has been created and the URL is {}".format(FullDomainName))
        else:
            logger.error(" Unable to create domain for URL {}  please check for error".format(FullDomainName))
            sys.exit(1)
    
        # Add http and https in listener of load balancer generating and picking random int to assign priority it should not matter as it is host based mapping in load balancer and not PATH Based
        randomPriorityHttps = random.randint(1,1000)
        randomPriorityHttp = random.randint(1001,2000)
        checkIfHTTPSListenerxists = loadBalancer.checkIfListenerExistsHTTPS(FullDomainName, args.HTTTPSListenerARN, args.region)
        if checkIfHTTPSListenerxists == False:
            logger.error(" Host entry already exists with {} ".format(FullDomainName))
            sys.exit(1)
        else:
            AddListenerHTTPSResponseARN = loadBalancer.addRuleToLoadBalancerHttps(FullDomainName, targetGroupARN, randomPriorityHttps, args.HTTTPSListenerARN, args.region)
            if AddListenerHTTPSResponseARN:
                logger.info(" DNS entry has been added in load balancer listener for https")
            else:
                logger.error(" Unable to add entry in listener in load balancer")
                
            checkIfHTTPListenerExists = loadBalancer.checkIfListenerExistsHTTP(FullDomainName, args.HTTPListenerARN, args.region)
            if checkIfHTTPListenerExists == False:
                logger.error(" Host entry already exists with same name {} ".format(FullDomainName))
                sys.exit(1)
            else:
                AddListenerHTTPResponseARN = loadBalancer.addRuleToLoadBalancerHttp(FullDomainName, targetGroupARN, randomPriorityHttp, args.HTTPListenerARN, args.region)
                if AddListenerHTTPResponseARN:
                    logger.info(" DNS entry has been added in load balancer listener for http")
                else:
                    logger.error(" Unable to add DNS in load balancer for http please check for error")
    
        # Create ecs service 
        createECSServiceResponse = ecsService.createService(ecsTaskDefinitionName, ecsTaskDefinitionName, targetGroupARN, args.appName, args.containerPort, args.email, args.ecsClusterName, args.subnetID, args.securityGroupID, args.region)
        ecsServiceName , ecsServiceARN = createECSServiceResponse[0], createECSServiceResponse[1]
        try:
            if createECSServiceResponse:
                logger.info(" ECS service has been created with name of {} ".format(ecsServiceName))
            else:
                logger.error(" Unable to create ECS service please check for error")
        except Exception as e:
            print(str(e))
    
        
        # Create index in kibana
        createIndexPatternResponse= kibana.createIndexPattern(args.appName, args.kibanaURL)
        if createIndexPatternResponse:
            logger.info(" Index has been created in kibana with name {}".format(args.appName))
        else:
            logger.error(" Unable to create index in kibana please create index pattern in kibana manually")

                
        # Health check for service endpoint
        healthCheckResponse = healthChecks.pingHealthEndpoint(FullDomainName, args.healthCheckPath)
        if healthCheckResponse:
            logger.info(" Health check passed for URL {} ".format(FullDomainName))
        else:
            logger.error(" Health check failed for URL {} please check kibana for error".format(FullDomainName))
            
            # Delete ecs service
            ecsServiceDeleteResponse = ecsService.deleteEcsService(ecsServiceName, args.ecsClusterName, args.region)
            if ecsServiceDeleteResponse:
                logger.info(" ECS service {} deleted ".format(ecsServiceName))
            else:
                logger.error(" Unable to delete ECS service {}".format(ecsServiceName))
                
            # Delete http rule from load balancer
            deleteRuleHTTPResponse = loadBalancer.deleteHTTPRuleLoadBalancer(AddListenerHTTPResponseARN, args.region)
            logger.info(" Deleted entry from load balancer for http")
            if deleteRuleHTTPResponse:
            # Delete https rule from load balancer
                deleteRuleHTTPSResponse = loadBalancer.deleteHTTPSRuleLoadBalancer(AddListenerHTTPSResponseARN, args.region)
                if deleteRuleHTTPSResponse:
                    logger.info(" Deleted entry from load balancer for https")
                else:
                    logger.error(" Unable to delete rule from load balancer for https")
            else:
                logger.error(" Unable to delete rule from load balancer for http")
                    
            # Delete target group 
            deleteTargetGroup = targetGroup.deleteTargetGroup(targetGroupARN, args.region)
            if deleteTargetGroup:
                logger.info(" Deleted target group ")
            else:
                logger.error(" Unable to delete target group ")
                    
            # Delete Route53 entry
            deleteR53EntryResponse = route53.DeleteR53Entry(domainName, args.domainNameOfHostedZone, args.HostedZoneId, args.loadBalancerDNSEndpoint, args.AWSHostedZoneIDForLoadbalancerRegionBasis, args.region)
            if deleteR53EntryResponse:
                logger.info(" Deleted r53 entry {}".format(FullDomainName))
            else:
                logger.error(" Unable to delete r53 entry {}".format(FullDomainName))
                
            # Delete secret from secret manager        
            DeleteSecretFromSecretManagerResponse = secretManager.deleteSecret(secretName, args.region)
            if DeleteSecretFromSecretManagerResponse:
                logger.info(" Secret {} deleted from secret manager ".format(secretName))
            else:
                logger.error(" Unable to delete secret please check for error")
            
            #List all revisions of Taskdefinitions
            listTaskDefinitionARNS = taskDefinition.listTaskDefinitionARNS(ecsTaskDefinitionName, args.region)
            if (len(listTaskDefinitionARNS)) == 0:
                logger.info(" No task definition matched with name of {} ".format(ecsTaskDefinitionName))
            else:
                logger.info(" Found task definitions with name of {} de-registering all the revisions".format(ecsTaskDefinitionName))   
            # De-Register task definition 
            deRegisterTaskDefinitionResponse = taskDefinition.deRegisterTaskDefinition(listTaskDefinitionARNS, args.region)
            if deRegisterTaskDefinitionResponse:
                logger.info(" Task definition de-registered")
            else:
                logger.error(" Unble to de-register task definition")
            
            # Delete ECR Repo
            deleteECRRepoResponse = application.deleteECRRepo(args.appName, args.awsAccountID, args.region)
            if deleteECRRepoResponse:
                logger.info(" ECR repo deleted")
            else:
                logger.error(" Unable to delete ECR Repo")
                
            # Delete secret from secret manager        
            DeleteSecretFromSecretManagerResponse = secretManager.deleteSecret(secretName)
            if DeleteSecretFromSecretManagerResponse:
                logger.info(" Secret {} deleted from secret manager ".format(secretName))
            else:
                logger.error(" Unable to delete secret please check for error")
    
    
    elif args.operation == 'update':
        ecsTaskDefinitionName = 'cloud-dev' + '-' + userName + '-' + args.appName 
        ecrRepoURI = args.awsAccountID + '.dkr.ecr.' + args.region + '.amazonaws.com/' + args.appName
        checkIfEcsServiceExistsUpdated = ecsService.checkIfServiceExists(ecsTaskDefinitionName)
        if checkIfEcsServiceExistsUpdated:
            logger.info(" Found service with name {} proceeding with re-deployment".format(ecsTaskDefinitionName))
        else:
            logger.error(" Unable to find service with name {} please check app name passed ".format(ecsTaskDefinitionName))
            sys.exit(1)
            
        clonedRepo = application.clone_repo(args.gitRepoName, args.branchName)
        if clonedRepo:
            logger.info(" Cloned {} repo".format(args.gitRepoName))
            logger.info(" Building docker image ")
            dockerImageBuild = application.buildDockerImage(args.gitRepoName, args.appName)
            if dockerImageBuild:
                logger.info(" Image built with name of {}".format(args.appName))
                imagePushedToECR = application.pushImageToECR(args.appName, args.appName, args.region)
                if imagePushedToECR:
                    logger.info(" Pushed image to ECR")
                else:
                    logger.error(" Unable to push image to ECR")
            else:
                logger.error(" Docker image build failed with error")
                sys.exit(1)
        else:
            logger.error(" Unable to clone repo please check for error")
            sys.exit(1)

        
        # Create new revision of task definition 
        updatedecsCreateTaskDefinitionResponse = taskDefinition.updateTaskDefinition(ecsTaskDefinitionName, args.appName, ecrRepoURI, args.appName, args.containerPort, args.email, args.secretName, args.awsAccountID, args.iamRoleNameForEcsTasks, args.iamExecutionRoleName, args.elasticSearchEndpointForLogs, args.elastciUserName, args.elasticPassowrd, args.region)
        updatedtaskDefinitionARN, updatedtaskDefinitionName = updatedecsCreateTaskDefinitionResponse[0], updatedecsCreateTaskDefinitionResponse[1]
        if updatedecsCreateTaskDefinitionResponse:
            logger.info(" Task definition has been cretated with name of {}".format(updatedtaskDefinitionName))
        else:
            logger.error(" Unable to create task definition please check for error")
            
        # Update ecs service with new task definition revision 
        updateECSServiceResponse = ecsService.updateECSService(updatedtaskDefinitionName, updatedtaskDefinitionARN, args.ecsClusterName, args.region)
        if updateECSServiceResponse:
            logger.info(" ECS Service {} is updated with new task definition revision".format(updatedtaskDefinitionName))
        else:
            logger.error(" Unable to update ecs service with new task definition revision please check for error")

    
    elif args.operation == 'delete':
        secretName = 'cloud-dev' + '-' + userName + '-' + args.appName
        ecsTaskDefinitionName = 'cloud-dev' + '-' + userName + '-' + args.appName 
        ecsServiceName = 'cloud-dev' + '-' + userName + '-' + args.appName 
        domainName = userName + '-' + args.appName 
        FullDomainName = domainName + '.' + args.domainNameOfHostedZone
        # Delete ecs service
        ecsServiceDeleteResponse = ecsService.deleteEcsService(ecsServiceName, args.ecsClusterName, args.region)
        if ecsServiceDeleteResponse:
            logger.info(" ECS service {} deleted ".format(ecsServiceName))
        else:
            logger.error(" Unable to delete ECS service {}".format(ecsServiceName))
        
        # Delete route53 record 
        deleteR53EntryResponse = route53.DeleteR53Entry(domainName, args.domainNameOfHostedZone, args.HostedZoneId, args.loadBalancerDNSEndpoint, args.AWSHostedZoneIDForLoadbalancerRegionBasis, args.region)
        if deleteR53EntryResponse:
            logger.info(" Deleted r53 entry {}".format(FullDomainName))
        else:
            logger.error(" Unable to delete r53 entry {}".format(FullDomainName))
        
        # Delete ECR Repo 
        deleteECRRepoResponse = application.deleteECRRepo(args.appName, args.awsAccountID, args.region)
        if deleteECRRepoResponse:
            logger.info(" ECR repo deleted")
        else:
            logger.error(" Unable to delete ECR Repo")
        
        # De-register task definition 
        listTaskDefinitionARNS = taskDefinition.listTaskDefinitionARNS(ecsTaskDefinitionName, args.region)
        if (len(listTaskDefinitionARNS)) == 0:
            logger.info(" No task definition matched with name of {} ".format(ecsTaskDefinitionName))
        else:
            logger.info(" Found task definitions with name of {} de-registering all the revisions".format(ecsTaskDefinitionName))
            deregisterTaskDefinisionRevs = taskDefinition.deRegisterTaskDefinition(listTaskDefinitionARNS, args.region)
            if deregisterTaskDefinisionRevs:
                logger.info(" Task definition have been de-registered")
            else:
                logger.error(" Unable to de-register task definition ")    
            
        # Delete secret from secret manager        
        DeleteSecretFromSecretManagerResponse = secretManager.deleteSecret(secretName, args.region)
        if DeleteSecretFromSecretManagerResponse:
            logger.info(" Secret {} deleted from secret manager ".format(secretName))
        else:
            logger.error(" Unable to delete secret please check for error")
        
        # get and delete http rules arn from load balancer listener
        getHTTPRuleARNResponse = loadBalancer.getHTTPRuleARN(FullDomainName, args.HTTPListenerARN, args.region)
        if getHTTPRuleARNResponse:
            deleteHTTPRuleEntryResponse = loadBalancer.deleteHTTPRuleLoadBalancer(getHTTPRuleARNResponse, args.region)
            if deleteHTTPRuleEntryResponse:
                logger.info(" Deleted http rule from load balancer")
            else:
                logger.error(" Unable to delete https rule from load balancer")
            
        # get and delete https rules arn from load balancer listener
        getHTTPSRuleARNResponse = loadBalancer.getHTTPSRuleARN(FullDomainName, args.HTTTPSListenerARN, args.region)
        if getHTTPSRuleARNResponse:
            deleteHTTPSRuleEntryResponse = loadBalancer.deleteHTTPSRuleLoadBalancer(getHTTPSRuleARNResponse, args.region)
            if deleteHTTPSRuleEntryResponse:
                logger.info(" Deleted https rule from load balancer")
            else:
                logger.error(" Unable to delete https rule from load balancer")
            
        # Delete target group 
        targetGroupNameFull = userName + '-' + args.appName
        targetGroupNameShort = targetGroupNameFull[:31]
        targetGroupNameShort = re.sub('[^a-zA-Z0-9 \n\.]', '', targetGroupNameShort)
        getTargetGroupARN = targetGroup.getTargetGroupARN(targetGroupNameShort, args.region)
        if getTargetGroupARN:
            deleteTargetGroupResponse = targetGroup.deleteTargetGroup(getTargetGroupARN, args.region)
            if deleteTargetGroupResponse:
                logger.info(" Target group deleted")
            else:
                logger.error(" Unable to delete target group")
        else:
            logger.error(" Unable to get target group ARN")
        
        
    else:
        logger.error(" Please choose the correct operation exiting")
        sys.exit(1)
    
if __name__ == "__main__":
    main()
    



