import boto3
from botocore.exceptions import ClientError


# Create a Secrets Manager client
#client = boto3.client('secretsmanager', region_name= region)

# Method to check if secret exists
def checkIfSecretExists(secretName: str, regionName: str):
    client = boto3.client('secretsmanager', region_name= region)
    """_summary_

    Args:
        secretName (str): Name of the secret to be checked if exists
        regionName (str): region to be checked
    """
    try:
        checkIfSecretExistsResponse = client.describe_secret(SecretId = secretName)
        if checkIfSecretExistsResponse:
            return True
    except Exception as e:
       return False

# Method to create new secret by inheriting from existing secret
def getAndCreateSecret(sourceSecretName: str, destSecretName: str, userEmail: str, region: str):
    """_summary_

    Args:
        sourceSecretName (str): Name of the secret to copy from
        destSecretName (str): Name of the secret to copy to
        userEmail (str): Email id of the user for tagging resources for tracking
    """
    client = boto3.client('secretsmanager', region_name= region)
    try:
        response = client.get_secret_value(SecretId=sourceSecretName)
    except ClientError as e:
        print(str(e))
        

    # Create a new secret by inheriting the existing one
    try:
        response = client.create_secret(
            Name=destSecretName,
            SecretString=response['SecretString'],
            Description=destSecretName,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': userEmail
                },
                {
                    'Key': 'userName',
                    'Value': userEmail
                },
                
            ]
        )
        return destSecretName
    except ClientError as e:
        print(str(e))
        return False


# Method to delete secret from secret manager
def deleteSecret(secretName: str, region: str):
    """_summary_

    Args:
        secretName (str): Name of the secret to be deleted
    """
    client = boto3.client('secretsmanager', region_name= region)
    try:
        response = client.delete_secret(
            SecretId = secretName,
            ForceDeleteWithoutRecovery=True
        )
        return True
    
    except Exception as e:
        print(str(e))
        return False
        


    
