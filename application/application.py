import logging
import git
import os
from git import Repo
import subprocess
import boto3
import sys
import base64
import docker


# Logger config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Method to Clone the repo 
def clone_repo(gitRepoName: str, branchName: str, githubOrgName: str): 
    # We will be using github as source code managment from which all the codes will be cloned and built 
    # Below 2 credentials have to configured in env variables for performing git operations depending where this will be run
    githubUserName = os.environ.get('github_creds_USR')
    githubPassword = os.environ.get('github_creds_PSW')
    
    """_summary_

    Args:
        gitRepoName (str): Name of the repo to be cloned
        branchName (str): Name of the branch
        githubOrgName (str): Name of orgnization in github 

    Returns:
        _type_: Repo details
    """
    try:

        check_for_repo = os.path.exists(gitRepoName)
        if (check_for_repo):
            remove_dir = 'rm -rf {}'.format(gitRepoName)
            os.system(remove_dir)
            logger.info(" Removed the directory which was already present cloning with recent changes")
        else:
            logger.info("The directory is not present. Cloning ")
        HTTPS_REMOTE_URL = f"https://{githubUserName}:{githubPassword}@github.com/{githubOrgName}/{gitRepoName}.git"
        repository = git.Repo.clone_from(HTTPS_REMOTE_URL, gitRepoName)
        repository.git.checkout(branchName)
        logger.info(" Checked out {} branch ".format(branchName))
        return repository
    except Exception as e:
        print(" Exception occured. please check error")
        print(e)
        return None


# Method to build docker image
def buildDockerImage(gitRepoName: str, imageName: str,):
    """_summary_

    Args:
        gitRepoName (str): Name of the github repo
        imageName (str): Name of the docker image to be built

    Returns:
        _type_: docker image
    """
    os.chdir(gitRepoName)
    
    dockerBuildcommand = "docker build -t {} .".format(imageName)
    result = os.system(dockerBuildcommand)
    if result == 0:
        return True
    else:
        logger.error(result)
        return False
    
# Method to check if ECR Repo exists
def checkIfECRRepoExists(ecrRepoName: str, registryId: str, region: str):
    """_summary_
    
    Args:
        ecrRepoName (str): Name of the ecr repo
        registryId (str): AWS Account ID where image will be stored
    
    Returns:
        _type_: Image exists in ECR Repo
    
    """
    client = boto3.client("ecr", region_name= region)
    try:
        response = client.describe_repositories(
            registryId = registryId,
            repositoryNames = [ecrRepoName]
        )
        return True
    except client.exceptions.RepositoryNotFoundException:
        return False

    
# Method to create ECR Repo
def createECRRepo(ecrRepoName: str, userEmail: str, registryId: str, region: str):
    """_summary_

    Args:
        ecrRepoName (str): Name of the ECR Repo
        userEmail (str): User email ID to tag under ECR Repo 
        registryId (str): AWS Account ID

    Returns:
        _type_: Created ECR Repo details
    """
    try:
        client = boto3.client("ecr", region_name= region)
        response = client.create_repository(
            registryId= registryId, 
            repositoryName= ecrRepoName,
            tags=[
                {
                    'Key': 'UserName',
                    'Value': userEmail
                },
                {
                    'Key': 'pod',
                    'Value': 'cloud-dev'
                },
            ],
            )
        repository = response["repository"]
        ecrRepoName = repository['repositoryName']
        ecrRepoURI = repository['repositoryUri']
        return ecrRepoName, ecrRepoURI
    except Exception as e:
        print(str(e))
        return False


# Method to push docker image to AWS ECR
def pushImageToECR(ecrRepoName: str, imageName: str, region: str):
    """_summary_

    Args:
        ecrRepoName (str): Name of the ECR Repo
        imageName (str): Docker image name

    Raises:
        Exception: Unable to push docker image to AWS ECR 

    Returns:
        _type_: _description_
    """
    try:
        # get AWS ECR login token
        ecr_client = boto3.client('ecr', region_name= region)
        ecr_credentials = (ecr_client.get_authorization_token()['authorizationData'][0])
        ecr_username = 'AWS'
        ecr_password = (base64.b64decode(ecr_credentials['authorizationToken']).replace(b'AWS:', b'').decode('utf-8'))
        ecr_url = ecr_credentials['proxyEndpoint']
        ecr_url_new = ecr_url.strip('https://')
        dockerLoginCMD = "docker login -u {} -p {} {}".format(ecr_username, ecr_password, ecr_url)
        dockerLoginResult = os.system(dockerLoginCMD)
        if dockerLoginResult != 0:
            raise Exception("Docker login failed")
        dockerTagCMD = "docker tag {} {}/{}".format(imageName, ecr_url_new, imageName)
        dockerTagResult = os.system(dockerTagCMD)
        if dockerTagResult !=0:
            raise Exception("Docker tagging failed")
        else:
            logger.info("Docker image tagged ")
        
        dockerPushCMD = "docker push {}/{}".format(ecr_url_new, imageName)
        dockerPushResult = os.system(dockerPushCMD)
        
        if dockerPushResult != 0:
            raise Exception("Unable to push image to ecr")
        return True
        
    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)
        return False
        
# Method to delete ECR Repo
def deleteECRRepo(ECRrepositoryName: str, registryId: str, region: str):
    """_summary_

    Args:
        ECRrepositoryName (str): ECR Repo name
        registryId (str): AWS Account ID

    Returns:
        _type_: If ECR Repo deleted
    """
    try:
        ecr_client = boto3.client('ecr', region_name= region)
        deleteECRRepoResponse = ecr_client.delete_repository(
            registryId=registryId,
            repositoryName=ECRrepositoryName,
            force=True
        )
        return True
    
    except Exception as e:
        print(str(e))
        return False
    
