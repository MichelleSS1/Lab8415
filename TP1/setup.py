from pyexpat.errors import codes
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
VPC_ID = None
ec2 = boto3.resource('ec2', region_name=REGION_NAME)
elb = boto3.client("elbv2", region_name=REGION_NAME)
ec2client = boto3.client('ec2', region_name=REGION_NAME)
SUBNETS = ec2client.describe_subnets()['Subnets']

def create_security_group(groupname, description, http=True, ssh=True, https=True):
    security_group = ec2.create_security_group(GroupName=groupname, Description=description)
    if http:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=80,ToPort=80)
    if ssh:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
    if https:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=443,ToPort=443)
    return security_group

def create_instances(instanceType:str, mincount:int, maxcount:int,securityGroups:"list[str]"):
    instances = ec2.create_instances(
        ImageId='ami-08c40ec9ead489470',
        MinCount=mincount,
        MaxCount=maxcount,
        InstanceType=instanceType,
        KeyName=KEY_NAME,
        UserData=USER_DATA,
        SecurityGroupIds=securityGroups
    )
    # global VPC_ID
    # VPC_ID = boto3.client("ec2",REGION_NAME).describe_instances()['Reservations'][0]['Instances'][0]['VpcId']
    i = 0
    for instance in instances:
        ec2.create_tags(Resources=[instance.id], Tags=[
            {
                'Key': 'Name',
                'Value': instanceType.replace('.','-') + '-' + str(i),
            },
        ])
        i += 1
    return instances

def create_cluster_target_group(name, instances, vpcId):
    group = elb.create_target_group(
        Name=name,
        Protocol='HTTP',
        Port=80,
        TargetType='instance',
        IpAddressType='ipv4',
        VpcId=vpcId
    )
    arn = group["TargetGroups"][0]['TargetGroupArn']
    targets = []
    for instance in instances:
        targets.append({"Id":instance})
    response = elb.register_targets(TargetGroupArn=arn, Targets=targets)
    return group, response, arn

def create_load_balancer(name, securityGroupID=None):
    balancer = elb.create_load_balancer(
        Name=name,
        Subnets=[
            SUBNETS[0]['SubnetId'],
            SUBNETS[1]['SubnetId']
        ],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4',
        # SecurityGroups=securityGroupID
    )
    return balancer

def attach_target_group_to_load_balancer(loadBalancerArn, targetGroupArn, port):
    response = elb.create_listener(
        DefaultActions=[
            {
                'TargetGroupArn': targetGroupArn,
                'Type': 'forward',
            },
        ],
        LoadBalancerArn=loadBalancerArn,
        Port=port,
        Protocol='HTTP',
    )
    return response

def wait_for_flask(instances):
    class FakeCode:
        def __init__(self) -> None:
            self.code = 500

    class FakeConnection:
        def __init__(self) -> None:
            pass
        def getresponse(self):
            return FakeCode()

    public_ips = [instance.public_ip_address for instance in instances]
    import http.client
    codes = None
    while True:
        connections = [http.client.HTTPConnection(ip) for ip in public_ips]
        for i in range(len(connections)):
            try:
                connections[i].request('GET', '/')
            except:
                connections[i] = FakeConnection()
        # ================================================================ Logging purpose only
        if codes == None:
            previous = [False for _ in connections]
        else:
            previous = [(code >= 200 and code < 300) for code in codes]
        # ================================================================


        codes = [connection.getresponse().code for connection in connections]
        all_ready = True
        
        for code in codes:
            all_ready = all_ready and (code >= 200 and code < 300)
        
        # ================================================================ Logging purpose only
        ready = [(code >= 200 and code < 300) for code in codes]
        for i in range(len(ready)):
            if previous[i] == False and ready[i] == True:
                print("Flask is ready at IP address ", public_ips[i])
        # ================================================================

        if all_ready:
            break

print("create security group: ")
group = create_security_group("test 2", "test 2")
print("done")


print("create instances group 1: ")
instances1 = create_instances("t1.micro",4,4,[group.id])
instanceIDs1 = [instance.id for instance in instances1]
print("done")

print("create instances group 2: ")
instances2 = create_instances("t2.micro",4,4,[group.id])
instanceIDs2 = [instance.id for instance in instances2]
print("done")

all_instances = instances1 + instances2

print("wait all of them are in a running state")
waiter = ec2client.get_waiter('instance_running')
all_instances_IDs = instanceIDs1 + instanceIDs2
waiter.wait(InstanceIds=all_instances_IDs)
print("done")

print("reload all instances")
for instance in all_instances:
    instance.reload()
print("done")

VPC_ID = boto3.client("ec2",REGION_NAME).describe_vpcs()['Vpcs'][0]['VpcId']

print("create target groups 1: ")
target_group1, attach_succeeded1, target_arn1 = create_cluster_target_group("target-cluster-1", instanceIDs1, VPC_ID)
print("done")

print("create target groups 2: ")
target_group2, attach_succeeded2, target_arn2 = create_cluster_target_group("target-cluster-2", instanceIDs2, VPC_ID)
print("done")

print("create load balancer: ")
balancer = create_load_balancer("my-load-balancer")
balancer_arn = balancer['LoadBalancers'][0]['LoadBalancerArn']
print("done")

print("attach target1")
attach_target_group_to_load_balancer(balancer_arn, target_arn1, 8080)
print("done")

print("attach target 2")
attach_target_group_to_load_balancer(balancer_arn, target_arn2, 80)
print("done")

print("wait until flask has been deployed on all machines:")
# TODO
# I'm thinking about, like, sending http requests until they all get "health check" back

from time import time

t = time()
wait_for_flask(all_instances)
print("total wait time:", time() - t, "seconds")