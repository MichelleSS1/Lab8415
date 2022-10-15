#!/bin/bash


mkdir flask-server
cd flask-server || exit

sudo apt-get update
sudo apt install python3-pip -y

pip install flask

AWS_INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
export AWS_INSTANCE_ID

git clone https://github.com/MichelleSS1/Lab8415.git
cd Lab8415/TP1 || exit
git checkout lab1/benchmark

python3 app_cluster<target_group>.py