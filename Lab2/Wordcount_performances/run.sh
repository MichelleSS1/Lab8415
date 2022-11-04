#!/bin/bash

# You should have aws cli installed for this script to work.

# Make sure neccessary information to connect to AWS is available
AWS_ENV_VAR=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "REGION")

check_aws_var() {
    var_name=$1

    # Check if variable was set by user doing aws configure
    value=$(aws configure get default."${var_name,,}")

    if [ "${var_name}" == "REGION" ]
    then
        var_name="AWS_DEFAULT_REGION"
    fi

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

# Install python dependencies in a virtual environment
sudo apt-get update -y
sudo apt install python3-venv
python3 -m venv log8415_lab1_venv
source log8415_lab1_venv/bin/activate

pip install -r requirements.txt
pip install -e .
printf "\n"

# Setup infra
python infra/setup_infra.py

# Run Hadoop and Spark experiments remotely
python scripts/remote_exec.py

# Teardown of the infrastructure
python infra/teardown_infra.py

# Exit virtual environment
deactivate