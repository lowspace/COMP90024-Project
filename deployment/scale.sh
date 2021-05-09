#!/bin/bash
ansible-playbook scale-up-instance.yaml; sleep 30; ansible-playbook -i openstack_inventory.py scale-up-swarm.yaml;