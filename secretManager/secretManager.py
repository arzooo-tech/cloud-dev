import boto3
from botocore.exceptions import ClientError


region = 'ap-south-1'

# Create a Secrets Manager client
client = boto3.client('secretsmanager', region_name= region)


# Method to create new secret by inheriting from existing secret
def getAndCreateSecret(sourceSecretName: str, destSecretName: str, userEmail: str):
    """_summary_

    Args:
        sourceSecretName (str): Name of the secret to copy from
        destSecretName (str): Name of the secret to copy to
        userEmail (str): Email id of the user for tagging resources for tracking
    """
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
def deleteSecret(secretName: str):
    """_summary_

    Args:
        secretName (str): Name of the secret to be deleted
    """
    try:
        response = client.delete_secret(
            SecretId = secretName,
            ForceDeleteWithoutRecovery=True
        )
        return True
    
    except Exception as e:
        print(str(e))
        return False
        


    
