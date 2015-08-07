#!/usr/bin/env bash

ansible-playbook playbooks/$1.yml -i hosts/hosts.txt -e "var_dir=$PWD/vars" \
    --private-key=~/.vagrant.d/insecure_private_key
