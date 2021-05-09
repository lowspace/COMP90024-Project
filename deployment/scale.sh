#!/bin/bash
. ./unimelb-comp90024-2021-grp-39-openrc.sh; ansible-playbook scale-up-instance.yaml; sleep 30; ansible-playbook -i openstack_inventory.py scale-up-swarm.yaml;