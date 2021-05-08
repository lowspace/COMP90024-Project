# Deployment Guide 

The entire deployment process is done by Ansible. 

## Steps to deploy

mrc.yaml creates the instances with correct volumes and security groups on Melbourne Research Cloud. 

deployment.yaml deploys the project to the instances. 

To deploy the project to the team 39 project on Melbourne Research Cloud, run 
```
chomd -x all.sh
./all.sh
```
Enter the password from MRCpassword.txt.

To deploy the project to other projects on Melbourne Research Cloud, you need to download the openrc.sh from the project, and put the private key named "Group39key.pem" in this directory. 

To deploy the project out of Melbourne Research Cloud, you need to re-configure the Ansible hosts in deployment.yaml. 

## Deployment Methods

The deployment process is divided up to 2 phases, the instances phase and the applications phase.

### Instances

In the instances phase, Ansible will communicate with the Cloud via openstacksdk to create the instances, security groups, and volumes that the project needs. The steps are defined in mrc.yaml. 

### Applications

All the configuration and deployment on each instance will be conducted in the applications phase. The steps are defined in deployment.yaml. 

List of tasks in deployment: 

1. Configure the environment so that the required software are in place. 
2. Initialise docker swarm on instance1 and let other instances join.
3. Deploy the applications with docker stack and initialise them. 

### Challenges

#### Permissions

Permissions of all files and programs need to be correct for Docker to access and run. 

#### Docker Swarm

The automated deployment of docker swarm requires Ansible to know the IP of each instance. We utilised openstack_inventory.py to import hosts gathered from the Cloud, so that all the IP addresses and instance names are stored in Ansible hostvars. When Ansible is initialising Swarm mode on instance1, the join token is saved into a variable in  dummy host so that other hosts can access this variable. 

#### Containers 

All scripts and files are copied to the instances via Ansible. 

Only 1 instance needs to deploy the Docker stack defined in docker-compose.yml. Docker Swarm will automatically assign the servies to instances in the swarm. 

After CouchDB is set up, all CouchDB nodes are programmatically added to the CouchDB cluster by Python in recluster.py, which is launched by Ansible. 

Another Python script reshard.py is used to recover database shards when the services are restarted, or when Docker Swarm nodes are restarted/moved/removed. This is not needed in deployment, but prepared for disaster recovery. When a service is deployed, Docker Swarm will assign a random task ID to each service, and the task ID is a part of CouchDB's node name. Since CouchDB maintains a map (database) between shards and CouchDB node name, it will not be able to open shards if the node name does not match the shards ID in the map. Thus, reshard.py is provided to fix the shard mapping. No data loss will occur in this fix. 
