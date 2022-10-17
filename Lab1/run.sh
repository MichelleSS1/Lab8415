#!/bin/bash

# You should have aws cli installed for this script to work.

# Make sure neccessary information to connect to AWS is available
AWS_ENV_VAR=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_DEFAULT_REGION")

check_aws_var() {
    var_name=$1

    # Check if variable was set by user doing aws configure
    value=$(aws configure get "${var_name}")

    # If variable not set by cli
    if [ -z "${value}" ]
    then
        echo "${var_name} has not been set by cli"
        
        # Check if variable have been exported by user
        if [ -z "${!var_name}" ]
        then
            # If variable not available in environment,
            # take its value from user input and export it for scripts
            read -r -p "Don't worry! Enter ${var_name} : " answer
            export "${var_name}"="${answer}"
        else 
            printf "It seems you have set the environment variable ${var_name}. Good job!\n"
        fi
    fi
    printf "\n"
}

# Loop through the array AWS_ENV_VAR
for env_var in "${AWS_ENV_VAR[@]}"
do
    check_aws_var "$env_var"
done

# Check if a session_token is needed
answer=''
while [ "${answer,,}" != "y" ] && [ "${answer,,}" != "n" ]
do
    read -r -p "Are you using temporary credentials and need a session token ? [y/N] " answer
done

if [ "${answer,,}" == "y" ]
then
    check_aws_var AWS_SESSION_TOKEN
fi

printf "Hey champion, now that we have what we need to connect to AWS, we can setup the infrastructure!\n\n"

# Install python dependencies
pip install -r requirements.txt
printf "\n"

# Setup infra
python3 infra/setup_infra.py

# Teardown created infra if setup fails then exit
# $? is the exit code of the last executed command
if [ "$?" != "0" ]
then
    python3 infra/teardown_infra.py
    exit 1
fi
printf "\n"

# Set load balancer DNS name 
LB_DNS_NAME=$(cat ./infra/lb_dns_name.txt) 

# Build docker image for bechmark tests
printf "Building docker image for benchmark\n\n"
docker build -q ./benchmark -t log8415_lab1
printf "\n"

# Run a container for tests and make load balancer DNS name available in container for calls
# Adding --rm to docker run to make the container be removed automatically when it exits.
printf "Starting docker container for benchmark\n\n"
docker run --rm -it -e LB_DNS_NAME="${LB_DNS_NAME}" log8415_lab1
printf "\n"

# Delete docker image
printf "Deleting docker image\n"
docker image rm log8415_lab1
printf "\n"

# Get metrics and save diagrams ?
# 

# Teardown of the infrastructure
python3 infra/teardown_infra.py