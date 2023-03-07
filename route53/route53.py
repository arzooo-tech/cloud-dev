#!/usr/bin/env python3

import boto3
import logging


region = 'ap-south-1'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = boto3.client('route53', region_name= region, )

def createR53Entry(hostName: str, domainNameOfHostedZone: str, HostedZoneId: str, loadBalancerDNSEndpoint: str, AWSHostedZoneIDForLoadbalancerRegionBasis: str):
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
    

def DeleteR53Entry(hostName: str, domainNameOfHostedZone: str, HostedZoneId: str, loadBalancerDNSEndpoint: str, AWSHostedZoneIDForLoadbalancerRegionBasis: str):
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


def checkIfRouteRecordExists(DomainName: str, HostedZoneId: str):
    """_summary_

    Args:
        DomainName (str): DNS Name to be checked which exists
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

