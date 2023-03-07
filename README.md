#                           cloud-dev

# What is cloud-dev ?

Ondemand testing environment deployed on AWS ECS which can created and destroyed as and when needed 

1. This creates all the necessary resources that are needed for deploying dockerized application on AWS ECS
2. Deploy a branch from any of the github repository which needs to be tested/deployed on AWS ECS
3. Outputs a endpoint/DNS which points to application DEPLOYED


# UseCases and Features
1. User should be able create/destroy test environment using any github branch, repo as and when needed dockerized applications on AWS ECS 
2. Enable to figure errors while executing job – verbose logs for user to see if any issues while bringing up environment
3. Application logs to be published in kibana 
4. User should be able to re-deploy on same branch with existing ECS Resources with out creating new ECS Stack from scratch


## Documentation 

1. To know more about on how to use the script, refer [How_To_Use.md](docs/HOW_TO_USE.md) 
2. To know more about the Flow, refer [FLOWDIAGRAM.md](docs/FLOWDIAGRAM.md)


## Contributing

To Contribute in the project, refer 
   1. [Contributing.md](docs/CONTRIBUTING.md)
   2. [Changelog.md](docs/CHANGELOG.md)


## Authors and acknowledgment
Somashekhar kanade




