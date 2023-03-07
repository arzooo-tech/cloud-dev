def email = env.BUILD_USER_ID

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
      string defaultValue: 'health', description: 'Health check path for app, eg: health', name: 'healthCheckPath', trim: false
      string defaultValue: '', description: 'Git repo name to be deployed eg: arzooo-be-v2', name: 'gitRepoName',  trim: true
      string defaultValue: '', description: 'Git repo branch to be deployed eg: test-som', name: 'branchName',  trim: true
      string defaultValue: 'homeyantra-test', description: 'Name of the secret from secret manager to copy values from', name: 'secretName',  trim: true
      choice(choices: ['update', 'create', 'delete'], name: 'operation', description: 'Type of operation to be performed')
      
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
                    //sh "python3 main.py ${email} ${appName} ${appName} ${containerPort} ${healthCheckPath} ${gitRepoName} ${branchName} ${appName}"
                      sh "python3 -u main.py ${email} ${appName} ${containerPort} ${healthCheckPath} ${gitRepoName} ${branchName} ${secretName} ${operation}"
                      
                }
            }
        }

    }
}
