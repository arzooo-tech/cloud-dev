#!/usr/bin/env python3

import boto3
import sys
import logging
import random

region = 'ap-south-1'
#HTTTPSListenerARN = 'arn:aws:elasticloadbalancing:ap-south-1:092042625037:listener/app/cloud-dev-ondemand-lb/04f65db33b0e9ca8/796cdecd56a4734a'
#HTTPListenerARN = 'arn:aws:elasticloadbalancing:ap-south-1:092042625037:listener/app/cloud-dev-ondemand-lb/04f65db33b0e9ca8/b552173237ed9660'


# Define the custom logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# define the boto client
client = boto3.client('elbv2', region_name= region)

def addRuleToLoadBalancerHttps(domainName: str, targetGroupArn: str, priority: int, HTTTPSListenerARN: str):
    """_summary_

    Args:
        domainName (str): DNS to be matched for host in load balancer rule
        targetGroupArn (str): ARN of target group
        priority (int): random int generated

    Returns:
        _type_: load balancer rules
    """
    try:
        response = client.create_rule(
            ListenerArn = HTTTPSListenerARN,
            Priority = priority,
            Conditions = [
                {
                    'Field': 'host-header',
                    'Values': [domainName]
                }
            ],
            Actions = [
                {
                'Type': 'forward',
                'TargetGroupArn': targetGroupArn
                }
            ]
        )
        HTTSPruleARN = response['Rules'][0]['RuleArn']
        return HTTSPruleARN
    
    except Exception as e:
        print(str(e))
        return False


def addRuleToLoadBalancerHttp(domainName: str, targetGroupArn: str, priority: int, HTTPListenerARN: str):
    """_summary_

    Args:
        domainName (str): DNS to be matched for host in load balancer rule
        targetGroupArn (str): ARN of target group
        priority (int): random int generated

    Returns:
        _type_: load balancer rule ARN
    """
    try:
        response = client.create_rule(
            ListenerArn = HTTPListenerARN,
            Priority = priority,
            Conditions = [
                {
                    'Field': 'host-header',
                    'Values': [domainName]
                }
            ],
            Actions = [
                {
                'Type': 'redirect',
                'RedirectConfig': {
                    'Protocol': 'HTTPS',
                    'Port': '443',
                    'Host': '#{host}',
                    'Path': '/#{path}',
                    'Query': '#{query}',
                    'StatusCode': 'HTTP_301'
                }
                }
            ]
        )
        HTTPruleARN = response['Rules'][0]['RuleArn']
        return HTTPruleARN
    
    except Exception as e:
        print(str(e))
        return False


def checkIfListenerExistsHTTPS(domainName: str, HTTTPSListenerARN: str):
    """`_summary_`

    Args:
        domainName (str): Domain name created for test env
    """
    response = client.describe_rules(
        ListenerArn = HTTTPSListenerARN,
    )
    for rules in response['Rules']:
        for hostHeader in rules['Conditions']:
            hostHeader = (hostHeader['Values'])
            if domainName in hostHeader:
                return False
                break
            else: 
                return True
                

def checkIfListenerExistsHTTP(domainName: str, HTTPListenerARN: str):
    """`_summary_`

    Args:
        domainName (str): Domain name created for test env
    """
    response = client.describe_rules(
        ListenerArn = HTTPListenerARN,
    )
    for rules in response['Rules']:
        for hostHeader in rules['Conditions']:
            hostHeader = (hostHeader['Values'])
            if domainName in hostHeader:
                return False
                break
            else: 
                return True
        
        
def deleteHTTPRuleLoadBalancer(httpRuleARN: str):
    """_summary_

    Args:
        ruleARN (str): Rule ARN of load balancer
    """
    try:
        response = client.delete_rule(
            RuleArn = httpRuleARN
        )
    
        deleteRuleHTTPStatus = (response['ResponseMetadata']['HTTPStatusCode'])
        return deleteRuleHTTPStatus
    
    except Exception as e:
        print(str(e))
        return False


def deleteHTTPSRuleLoadBalancer(HTTPSRuleARN: str):
    """_summary_

    Args:
        ruleARN (str): Rule ARN of load balancer
    """
    try:
        response = client.delete_rule(
            RuleArn = HTTPSRuleARN
        )
    
        deleteRuleHTTPSStatus = (response['ResponseMetadata']['HTTPStatusCode'])
        return deleteRuleHTTPSStatus
    
    except Exception as e:
        print(str(e))
        return False


def getHTTPRuleARN(hostHeader: str, HTTPListenerARN: str):
    """_summary_

    Args:
        hostHeader (str): host name for which listener rule to be fetched

    Returns:
        _type_: _description_
    """
    listener_rules = client.describe_rules(ListenerArn=HTTPListenerARN)['Rules']
    filtered_rules = [r for r in listener_rules if r['Conditions'] and r['Conditions'][0]['Values'][0] == hostHeader]
    try:
        httpRuleArn = filtered_rules[0]['RuleArn']
        return httpRuleArn
    except Exception as e:
        return False


def getHTTPSRuleARN(hostHeader: str, HTTTPSListenerARN: str):
    """_summary_

    Args:
        hostHeader (str): host name for which listener rule to be fetched

    Returns:
        _type_: _description_
    """
    listener_rules = client.describe_rules(ListenerArn=HTTTPSListenerARN)['Rules']
    filtered_rules = [r for r in listener_rules if r['Conditions'] and r['Conditions'][0]['Values'][0] == hostHeader]
    try:
        httpsRuleArn = filtered_rules[0]['RuleArn']
        return httpsRuleArn
    except Exception as e:
        return False
    
    



