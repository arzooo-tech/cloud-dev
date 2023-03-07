#!/usr/bin/env python3

import requests
import logging
import time


# Define the custom logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Method to ping health check endpoint
def pingHealthEndpoint(domainName: str, healthCheckPath: str):
    """_summary_

    Args:
        domainName (str): DNS name to which service is pointing to 
        healthCheckPath (str): Health check path for service

    Returns:
        _type_: Service response
    """
    
    healthCheckUrlFull = 'https://' + domainName + '/' + healthCheckPath
    print("health check url is {} {} {}".format('\033[1m', healthCheckUrlFull, '\033[0m'))
    print("Please wait while app is getting deployed")
    print(healthCheckUrlFull)
    time.sleep(120)         # Sleep is added to wait untill application gets deployed 
    response = requests.get('https://' + domainName + '/' + healthCheckPath)
    if response.status_code == (200 or 201 or 301 or 302):
        print(response)
        return True
    else:
        print(response)
        return False
        
        
