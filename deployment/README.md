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
# Scaling Steps

1. Inspect ```./host_vars_scale.yaml``` and enter the details of the new resources
2. Run ```./scale.sh```



