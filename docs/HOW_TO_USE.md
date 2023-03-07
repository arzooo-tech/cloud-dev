
#           How to use cloud-dev platform 

### On Mac Machine

1. Clone the repository using 
    `git clone <repo_url`
2. Install the python3 on machine based on system 

    a. `brew install python@3.11`
    b. `AWS access key and AWS secret keys setup as environment variables`
    c. `Kibana username and password setup as environment variables`
3. Install the dependencies required by project by using [requirements.txt]
    `pip3 install -r requirements.txt`
4. This is CLI Based app before running get to know the parameters to be passed by running 
    `python3 main.py -h`
        It would output all the required parameter to run the project 
        Cloud-dev -- On-demand Testing env

            positional arguments:
            email                 Please enter your email address
            appName               Name of the service/app being deployed
            containerPort         Port on which app will be running
            healthCheckPath       Health check path for app
            gitRepoName           git Repo name
            branchName            Name of the branch to be used for building
            secretName            Name of the secret in secret maanger to be copied values from
            operation             Operation to be performed allowed values are [create, update, delete]
            companyEmailDomain    Email domain against which this needs to be validated
            ecsClusterName        Name of the ECS Cluster where all these ECS workloads will be running
            region                Region in which all ECS workloads will be running
            awsAccountID          AWS Account ID in which all these resources will be running
            HostedZoneId          ID of the Hosted Zone from Route 53 Console under which all domains for these will be created
            githubOrgName         Name of the github organization under which projects are present
            iamRoleNameForEcsTasks
                                    IAM Role name to be used for tasks Name to be passed NOT ARN of the IAM Role
            iamExecutionRoleName  Name of the IAM Execution role name to be passed NOT ARN of the IAM Role
            elasticSearchEndpointForLogs
                                    Endpoint of elastic search where logs will be published
            elastciUserName       User name for elastic search
            elasticPassowrd       Password for elastic
            vpcId                 AWS VPC Id in which all resources will be created
            domainNameOfHostedZone
                                    Route53 hosted zone name under which all records will be created
            loadBalancerDNSEndpoint
                                    DNS of load balancer in which all the rules for hosts will be created which will be mapped in route53 alias record PS: Single load balancer is being used for all hosts being created by
                                    this project
            AWSHostedZoneIDForLoadbalancerRegionBasis
                                    AWS Has fixed hosted zone id for different type of Load balancer based on region that value to be passed details here https://docs.aws.amazon.com/general/latest/gr/elb.html
            HTTTPSListenerARN     HTTPS Listener ARN of load balancer
            HTTPListenerARN       HTTP Listener ARN of load balancer
            subnetID              Subnet Id in which workloads will run
            securityGroupID       Security group ID to be used for ecs
            kibanaURL             URL of kibana where application will be published

5. Run the project
    python3 main.py <email> <appName> <containerPort> <healthCheckPath> <gitRepoName> <branchName> <secretName> <operation> <companyEmailDomain> <ecsClusterName> <region> <awsAccountID> <HostedZoneId> <githubOrgName> <iamRoleNameForEcsTasks> <iamExecutionRoleName> <elasticSearchEndpointForLogs> <elastciUserName> <elasticPassowrd> <vpcId> <domainNameOfHostedZone> <loadBalancerDNSEndpoint> <AWSHostedZoneIDForLoadbalancerRegionBasis> <HTTTPSListenerARN> <HTTPListenerARN> <subnetID> <securityGroupID> <kibanaURL>

        change the above values as per your environment 

