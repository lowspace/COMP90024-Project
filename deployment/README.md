# Deployment Entrypoints



| Files/Dir         |       Intro        |                 
|-------------------|:-------------------|
| ```./init.sh``` | First time deployment on MRC  |
| ```./scale.sh``` | Scale up instances on MRC    |
| ```./recluster-couchdb.sh``` | Fix CouchDB cluster after Docker service reboots |
| ```./MRCpassword.txt``` | the password to be entered while executing the above  |
| ```./files/``` | files to be deployed on MRC  |
| ```./roles/``` | Ansible scripts  |

# Deployment Steps

1. Run ```./init.sh```
2. Enter the master password from MRCpassword.txt

# Scaling Steps

1. Inspect ```./host_vars_scale.yaml``` and enter the details of the new resources
2. Run ```./scale.sh```
3. Enter the master password from MRCpassword.txt
4. Go to the "Manage" page (Portainer)
5. Portainer username is admin and password is password. 
6. Scale up services. 

# Fix CouchDB "Failed to load database" Error
1. Run ```recluster-couchdb.sh```


