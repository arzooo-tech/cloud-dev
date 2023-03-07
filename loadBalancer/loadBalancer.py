#!/usr/bin/env python3

import boto3
import sys
import logging
import random

region = 'ap-south-1'

# Define the custom logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# define the boto client
client = boto3.client('elbv2', region_name= region)


# Method to add https rule to load balancer
def addRuleToLoadBalancerHttps(domainName: str, targetGroupArn: str, priority: int, HTTTPSListenerARN: str):
    """_summary_

    Args:
        domainName (str): DNS to be matched for host in load balancer rule
        targetGroupArn (str): ARN of target group
        priority (int): random int generated
        HTTTPSListenerARN (str): HTTPS Listener ARN

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

# Method to add http rule to load balancer
def addRuleToLoadBalancerHttp(domainName: str, targetGroupArn: str, priority: int, HTTPListenerARN: str):
    """_summary_

    Args:
        domainName (str): DNS to be matched for host in load balancer rule
        targetGroupArn (str): ARN of target group
        priority (int): random int generated
        HTTPListenerARN (str): HTTP Listener ARN

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


# Check if listener already exists
def checkIfListenerExistsHTTPS(domainName: str, HTTTPSListenerARN: str):
    """`_summary_`

    Args:
        domainName (str): Domain name created for test env
        HTTTPSListenerARN (str):  HTTPS Listener ARN
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
                

# Check if listener already exists
def checkIfListenerExistsHTTP(domainName: str, HTTPListenerARN: str):
    """`_summary_`

    Args:
        domainName (str): Domain name created for test env
        HTTPListenerARN (str):  HTTP Listener ARN
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
        
        
# Delete http rule from listener
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

# Delete https rule from listener
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


# Get ARN for HTTP Rule
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


# Get ARN for HTTPS Rule
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
    
    