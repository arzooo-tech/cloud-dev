#!/usr/bin/env python3

import boto3
import logging


region = 'ap-south-1'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = boto3.client('route53', region_name= region, )


# Method to create route53 record
def createR53Entry(hostName: str, domainNameOfHostedZone: str, HostedZoneId: str, loadBalancerDNSEndpoint: str, AWSHostedZoneIDForLoadbalancerRegionBasis: str):
    """_summary_

    Args:
        hostName (str): hostname to be created
        domainNameOfHostedZone (str): Route53 hosted zone DNS record under which records would be created
        HostedZoneId (str): Hosted Zone ID of zone under which all records would be created
        loadBalancerDNSEndpoint (str): DNS Endpoint of load balancer to point route53 record
        AWSHostedZoneIDForLoadbalancerRegionBasis (str): AWS assigns zone ID for different type of load balancer based on region more details https://docs.aws.amazon.com/general/latest/gr/elb.html

    Returns:
        _type_: Route53 record details
    """
    domainName = hostName + '.' + domainNameOfHostedZone
    try:
        response = client.change_resource_record_sets(
            HostedZoneId=HostedZoneId,
            ChangeBatch={
                'Comment': 'Created by cloud-dev automation',
                'Changes': [
                        {
                            'Action': 'CREATE',
                            'ResourceRecordSet': {
                                'Name': domainName,
                                'Type': 'A',
                                'AliasTarget': {
                                    'DNSName': loadBalancerDNSEndpoint,
                                    'HostedZoneId': AWSHostedZoneIDForLoadbalancerRegionBasis,
                                    'EvaluateTargetHealth': False,
                                }
                            }
                        }
                ]
            }   
        )
        return response
        
    except Exception as e:
        print(str(e))
        return False
    
# Method to delete route53 entry
def DeleteR53Entry(hostName: str, domainNameOfHostedZone: str, HostedZoneId: str, loadBalancerDNSEndpoint: str, AWSHostedZoneIDForLoadbalancerRegionBasis: str):
    """_summary_

    Args:
        hostName (str): hostname to be created
        domainNameOfHostedZone (str): Route53 hosted zone DNS record under which records would be created
        HostedZoneId (str): Hosted Zone ID of zone under which all records would be created
        loadBalancerDNSEndpoint (str): DNS Endpoint of load balancer to point route53 record
        AWSHostedZoneIDForLoadbalancerRegionBasis (str): AWS assigns zone ID for different type of load balancer based on region more details https://docs.aws.amazon.com/general/latest/gr/elb.html

    Returns:
        _type_: Route53 record deletion 
    """
    domainName = hostName + '.' + domainNameOfHostedZone
    try:
        response = client.change_resource_record_sets(
            HostedZoneId=HostedZoneId,
            ChangeBatch={
                'Comment': 'Created by cloud-dev automation',
                'Changes': [
                        {
                            'Action': 'DELETE',
                            'ResourceRecordSet': {
                                'Name': domainName,
                                'Type': 'A',
                                'AliasTarget': {
                                    'DNSName': loadBalancerDNSEndpoint,
                                    'HostedZoneId': AWSHostedZoneIDForLoadbalancerRegionBasis,
                                    'EvaluateTargetHealth': False,
                                }
                            }
                        }
                ]
            }   
        )
        DeleteR53EntryStatus = response['ResponseMetadata']['HTTPStatusCode']
        return DeleteR53EntryStatus
        
    except Exception as e:
        print(str(e))
        return False

# Method to check if route53 record exists
def checkIfRouteRecordExists(DomainName: str, HostedZoneId: str):
    
    """_summary_

    Args:
        DomainName (str): DNS Name to be checked which exists
        HostedZoneId (str):  Hosted Zone ID
    """

    response = client.list_resource_record_sets(
        HostedZoneId=HostedZoneId,
        StartRecordName=DomainName,
        StartRecordType='A'
    )

    if response['IsTruncated']:
        response = client.list_resource_record_sets(
            HostedZoneId=HostedZoneId,
            StartRecordName=DomainName,
            StartRecordType='A',
            StartRecordIdentifier=response['NextRecordIdentifier']
        )

    for record_set in response['ResourceRecordSets']:
        if record_set['Name'] == DomainName and record_set['Type'] == 'A':
            return True
    else:
        return False

