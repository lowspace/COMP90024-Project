#!/bin/bash
. ./unimelb-comp90024-2021-grp-39-openrc.sh; ansible-playbook -i openstack_inventory.py deployment.yml