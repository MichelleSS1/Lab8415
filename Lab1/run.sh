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
            echo "It seems you have set the environment variable ${var_name}. Good job!"
        fi
    fi
    echo ""
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

echo ""
echo "Hey champion, now that we have what we need to connect to AWS, we can setup the infrastructure!"
echo ""

# Install python dependencies
pip install -r requirements.txt
echo ""

# Setup infra
# teardown created infra if setup fails and exit
python3 infra/setup_infra.py || python3 infra/teardown_infra.py; exit 1

# Set load balancer DNS name 
LB_DNS_NAME=$(cat ./infra/lb_dns_name.txt) 

# Run a container for tests and make load balancer DNS name available in container for calls
#
# `docker build -q` outputs nothing but the final image hash
# Adding --rm to docker run to make the container be removed automatically when it exits.
docker run --rm -it $(docker build -q ./benchmark) -e LB_DNS_NAME=${LB_DNS_NAME}

# Get metrics and save diagrams ?
# 

# Teardown of the infrastructure
python3 infra/teardown_infra.py