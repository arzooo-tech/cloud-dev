def email = env.BUILD_USER_ID   // Email ID being fetched from jenkins logged in user session

pipeline {
    agent {
        kubernetes {
            cloud "kubernetes"
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  namespace: jenkins
spec:
  containers:
  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-graph-storage
      mountPath: /var/lib/docker
  restartPolicy: Never
  volumes:
  - name: docker-graph-storage
    emptyDir: {}
'''
          }
      }


    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws_access_key_id')
        AWS_SECRET_ACCESS_KEY = credentials('aws_secret_access_key')
        AWS_DEFAULT_REGION    = 'ap-south-1'
        github_creds          = credentials('jenkins-github-sre')
        GIT_PYTHON_REFRESH    = "quiet" 
        kibanaUsername        = credentials('kibanaUsername')
        kibanaPassword        = credentials('kibanaPassword')
    }

    parameters {
      
      string defaultValue: '', description: 'Name of the app to be deployed this can be any name NOT necessarily exact app name', name: 'appName',  trim: true
      string defaultValue: '4000', description: 'Port on which app runs', name: 'containerPort',  trim: true
      string defaultValue: 'health', description: 'Health check path for app, eg: health', name: 'healthCheckPath', trim: true
      string defaultValue: '', description: 'Git repo name to be deployed eg: arzooo-be-v2', name: 'gitRepoName',  trim: true
      string defaultValue: '', description: 'Git repo branch to be deployed eg: test-som', name: 'branchName',  trim: true
      string defaultValue: 'homeyantra-test', description: 'Name of the secret from secret manager to copy values from', name: 'secretName',  trim: true
      choice(choices: ['update', 'create', 'delete'], name: 'operation', description: 'Type of operation to be performed')
      string defaultValue: '', description: 'Email domain against which this needs to be validated, eg: <comapny-name>', name: 'companyEmailDomain', trim: true
      string defaultValue: '', description: 'Name of the ECS Cluster where all these ECS workloads will be running', name: 'ecsClusterName', trim: true
      string defaultValue: '', description: 'Region in which all ECS workloads will be running', name: 'region', trim: true
      string defaultValue: '', description: 'AWS Account ID in which all these resources will be running', name: 'awsAccountID', trim: true
      string defaultValue: '', description: 'ID of the Hosted Zone from Route 53 Console under which all domains for these will be created', name: 'HostedZoneId', trim: true
      string defaultValue: '', description: 'Name of the github organization under which projects are present', name: 'githubOrgName', trim: true
      string defaultValue: '', description: 'IAM Role name to be used for tasks Name to be passed NOT ARN of the IAM Role', name: 'iamRoleNameForEcsTasks', trim: true
      string defaultValue: '', description: 'Name of the IAM Execution role name to be passed NOT ARN of the IAM Role', name: 'iamExecutionRoleName', trim: true
      string defaultValue: '', description: 'Endpoint of elastic search where logs will be published', name: 'elasticSearchEndpointForLogs', trim: true
      string defaultValue: '', description: 'User name for elastic search', name: 'elastciUserName', trim: true
      string defaultValue: '', description: 'Password for elastic', name: 'elasticPassowrd', trim: true 
      string defaultValue: '', description: 'AWS VPC Id in which all resources will be created', name: 'vpcId', trim: true 
      string defaultValue: '', description: 'Route53 hosted zone name under which all records will be created', name: 'domainNameOfHostedZone', trim: true 
      string defaultValue: '', description: 'DNS of load balancer in which all the rules for hosts will be created which will be mapped in route53 alias record PS: Single load balancer is being used for all hosts being created by this project', name: 'loadBalancerDNSEndpoint', trim: true 
      string defaultValue: '', description: 'AWS Has fixed hosted zone id for different type of Load balancer based on region that value to be passed details here https://docs.aws.amazon.com/general/latest/gr/elb.html', name: 'AWSHostedZoneIDForLoadbalancerRegionBasis', trim: true 
      string defaultValue: '', description: 'HTTPS Listener ARN of load balancer ', name: 'HTTTPSListenerARN', trim: true 
      string defaultValue: '', description: 'HTTP Listener ARN of load balancer', name: 'HTTPListenerARN', trim: true 
      string defaultValue: '', description: 'Subnet Id in which workloads will run', name: 'subnetID', trim: true 
      string defaultValue: '', description: 'Security group ID to be used for ecs', name: 'securityGroupID', trim: true 
      string defaultValue: '', description: 'URL of kibana where application will be published', name: 'kibanaURL', trim: true 
      
    }

    stages {

        stage("Input conversion ") {
            steps {
                container("dind") {
                    script{
                      env.appName = env.appName.toLowerCase()
                    }
                }
            }
        }


        stage("install packages") {
            steps {
                container("dind") {
                    sh "apk add curl"
                    sh "apk add py3-pip"
                    sh "apk add git"
                    sh "curl https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py && python get-pip.py"
                }
            }
        }

        stage("install requirements.txt ") {
            steps {
                container("dind") {
                    sh "pip3 install -r requirements.txt > /dev/null"
                }
            }
        }

        stage("Run Python code for building and deploying app") {
            steps {
                container("dind") {                 
                      sh "python3 -u main.py ${email} ${appName} ${containerPort} ${healthCheckPath} ${gitRepoName} ${branchName} ${secretName} ${operation} ${companyEmailDomain} ${ecsClusterName} ${region} ${awsAccountID} ${HostedZoneId} ${githubOrgName} ${iamRoleNameForEcsTasks} ${iamExecutionRoleName} ${elasticSearchEndpointForLogs} ${elastciUserName} ${elasticPassowrd} ${vpcId} ${domainNameOfHostedZone} ${loadBalancerDNSEndpoint} ${AWSHostedZoneIDForLoadbalancerRegionBasis} ${HTTTPSListenerARN} ${HTTPListenerARN} ${subnetID} ${securityGroupID} ${kibanaURL}"
                      
                }
            }
        }

    }
}
