import boto3
USER_DATA = '''#!/bin/bash
cd /home/ubuntu
mkdir flask-server
cd flask-server
sudo apt-get update
sudo apt install python3-pip -y
sudo apt install python3.8-venv
python3 -m venv venv
. venv/bin/activate
sudo pip install flask
echo "from flask import Flask" >> app.py
echo "app = Flask(__name__)" >> app.py
echo "@app.route(\'/\')" >> app.py
echo "def health_check():" >> app.py
echo "    return \'<p>health check</p>\'" >> app.py
echo "app.run(host=\'0.0.0.0\', port=80)" >> app.py
sudo python3 app.py
'''

KEY_NAME = "vockey"
REGION_NAME = 'us-east-1'

ec2 = boto3.resource('ec2', region_name=REGION_NAME)
elb = boto3.client("elbv2", region_name=REGION_NAME)

def create_security_group(groupname, description, http=True, ssh=True, https=True):
    security_group = ec2.create_security_group(GroupName=groupname, Description=description)
    if http:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=80,ToPort=80)
    if ssh:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
    if https:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=443,ToPort=443)
    return security_group

def create_instances(instanceType:str,mincount,maxcount,securityGroups):
    instances = ec2.create_instances(
        ImageId='ami-08c40ec9ead489470',
        MinCount=mincount,
        MaxCount=maxcount,
        InstanceType=instanceType,
        KeyName=KEY_NAME,
        UserData=USER_DATA,
        SecurityGroups=securityGroups
    )
    return instances

def create_cluster_target_group(name, instances):
    group = elb.create_target_group(
        Name=name,Protocol='HTTP',
        Port=80,
        TargetType='instance',
        IpAddressType='ipv4'
    )

    arn = group["TargetGroups"][0]['TargetGroupArn']

    targets = []
    for instance in instances:
        targets.append({"Id":instance.instance_id})

    response = elb.register_targets(
        TargetGroupArn=arn,
        Targets=targets
    )

    return group, response, arn

def create_load_balancer(name, securityGroupID):
    balancer = elb.create_load_balancer(
        Name=name,
        Subnets=[
            REGION_NAME + 'a',
            REGION_NAME + 'b'
        ],
        SecurityGroups=[
            securityGroupID
        ],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )
    return balancer

def attach_target_group_to_load_balancer(loadBalancerArn, targetGroupArn):
    response = elb.create_listener(
        DefaultActions=[
            {
                'TargetGroupArn': targetGroupArn,
                'Type': 'forward',
            },
        ],
        LoadBalancerArn=loadBalancerArn,
        Port=80,
        Protocol='HTTP',
    )
    return response

# create security group
securityGroup = create_security_group("Tp1SecurityGroup", "this is the security group used for all instances")

# create 4 with security group
# create a target group

# create 5 with security group
# create a target group

# create an ELB
# attach security group 1 to ELB
# attach security group 2 to ELB


# instances = ec2.create_instances(
#     ImageId='ami-08c40ec9ead489470',
#     MinCount=1,
#     MaxCount=1,
#     InstanceType='t2.micro'
# )

# COMMANDS_TO_RUN = [
#     "sudo apt install python3-venv",
#     "mkdir flask_application && cd flask_application",
#     "python3 -m venv venv",
#     "source venv/bin/activate",
#     "pip install Flask"
# ]

# ssm = boto3.client("ssm", region_name='us-east-1')
# iam = boto3.client('iam')

# ID = "i-0ece96c91260e89bb"
# ROLE = 'AmazonSSMManagedInstanceCore'

# 

# print("waiting until running... ")
# import time
# t = time.time()
# machine.wait_until_running()

# print("total wait time: ", time.time() - t)
# PROFILE = 'TEST-PROFILE'



# instance_profile = iam.create_instance_profile (
#     InstanceProfileName = PROFILE
# )

# response = iam.add_role_to_instance_profile (
#     InstanceProfileName = PROFILE,
#     RoleName            = ROLE
# )

# resp = ssm.send_command(
#     DocumentName="AWS-RunShellScript", # One of AWS' preconfigured documents
#     Parameters={'commands': COMMANDS_TO_RUN},
#     InstanceIds=[ID],
# )

# print(resp.__dict__)

