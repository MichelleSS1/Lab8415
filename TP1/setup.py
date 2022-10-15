import boto3
import http.client

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

def create_security_group(groupname:str, description:str, http=True, ssh=True, https=True):
    """
    creates a security group for instances with GroupName = groupname, Description = description. The parameters http, 
    ssh and https specifies whether incoming HTTP, SSH and HTTPS traffic are allowed; if it is allowed, all sources 
    of such traffic are allowed Ex. if http is true, then anyone may send an HTTP request to the instance with this
    security group.

    @param groupname:str    name of the security group
    @param description:str  description of the security group
    @param http:boolean     allow incoming HTTP traffic? True = yes False = no
    @param ssh:boolean      allow incoming SSH traffic? True = yes False = no
    @param https:boolean    allow incoming HTTPS traffic? True = yes False = no
    
    @return                 response with the security group ID and other data 
    """
    
    security_group = ec2.create_security_group(GroupName=groupname, Description=description)
    if http:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=80,ToPort=80)
    if ssh:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=22,ToPort=22)
    if https:
        security_group.authorize_ingress(IpProtocol="tcp",CidrIp="0.0.0.0/0",FromPort=443,ToPort=443)
    return security_group

def create_instances(instanceType:str, mincount:int, maxcount:int,security_groups:"list[str]"):
    """
    Create maxcount instances, and at least mincount instances if not possible, with instanceType specifying the type
    of machine to be created and security_groups specifying the security groups of each instance. The operating system
    will be ubuntu. The script USER_DATA will be executed on each instance once it's running.

    @param instanceType:str             type of instance, specifies the available CPU, memory, etc. ex. t2.micro
    @param mincount:int                 create at least this many instances
    @param maxcount:int                 try to create this many instances
    @param security_groups:list[str]    security groups ids to be applied ['sg-id1', 'sg-id2']

    @return                             response containing the instance IDs and other data 
    """

    instances = ec2.create_instances(
        ImageId='ami-08c40ec9ead489470',
        MinCount=mincount,
        MaxCount=maxcount,
        InstanceType=instanceType,
        KeyName=KEY_NAME,
        UserData=USER_DATA,
        SecurityGroupIds=security_groups
    )
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

def create_cluster_target_group(name:str, instances:"list[str]", vpc_Id:str):
    """
    Creates a target group that contains all the instances specified in instances in the virtual private cloud
    with id = vpc_Id; by default there is only one VPC. The protocol used is HTTP (targets receives traffic on port
    80)
    @param name:str             name of the target group to be created
    @param instances:list[str]  list of the instance ids to be included in that group ['i-id1', 'i-id2']
    @param vpc_Id:str           id of the Virtual Private Cloud

    @return:                    response containing the target group, response of registering targets, target group ARN
    """
    group = elb.create_target_group(
        Name=name,
        Protocol='HTTP',
        Port=80,
        TargetType='instance',
        IpAddressType='ipv4',
        VpcId=vpc_Id
    )
    arn = group["TargetGroups"][0]['TargetGroupArn']
    targets = []
    for instance in instances:
        targets.append({"Id":instance})
    response = elb.register_targets(TargetGroupArn=arn, Targets=targets)
    return group, response, arn

def create_load_balancer(name:str, security_group_IDs:"list[str]"):
    """
    creates an internet facing application load balancer with Name=name and the security groups specified in security_group_IDs
    the subnets used will be by default us-east-1a and us-east-1b as specified in SUBNETS. IpV4 is used for IP.
    
    @param name: str                        the name of the load balancer
    @param security_group_IDs: list[str]    the list of security group IDs (['sg-id1', sg-'id2'])
    
    @return:                                response containing the balancer arn and other data
    """
    balancer = elb.create_load_balancer(
        Name=name,
        Subnets=[
            SUBNETS[0]['SubnetId'],
            SUBNETS[1]['SubnetId']
        ],
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4',
        SecurityGroups=security_group_IDs
    )
    return balancer

def attach_target_group_to_load_balancer(load_balancer_arn:str, target_group_arn:str, port:int):
    """
    attaches target group with ARN = target_group_arn to load balancer with ARN = load_balancer_arn
    the load balancer will listen on Port = port
    
    @param load_balancer_arn:str    ARN of the load balancer
    @param target_group_arn:str     ARN of the target group
    @param port:int                 Port on which the listener will listen
    
    @return: response after creating the listener
    """
    response = elb.create_listener(
        DefaultActions=[
            {
                'TargetGroupArn': target_group_arn,
                'Type': 'forward',
            },
        ],
        LoadBalancerArn=load_balancer_arn,
        Port=port,
        Protocol='HTTP',
    )
    return response

def wait_for_flask(instances:"list[ec2.Instance]"):
    """
    Wait for all instances specified in instances to deploy flask. This works by sending GET requests to each instance
    until all instances return a valid response code (>=200 and < 300).

    @params instances:list[Instance]    A list of ec2.Instance objects

    @return                             None
    """
    
    
    # since connection.request can throw an error, this will mimick an connection object
    # and allow the operation connection.getresponse().code
    # not used anywhere except here
    class FakeCode:
        def __init__(self) -> None:
            self.code = 500
    class FakeConnection:
        def __init__(self) -> None:
            pass
        def getresponse(self):
            return FakeCode()

    public_ips = [instance.public_ip_address for instance in instances]
    codes = None

    # stay in the while loop as long as all the instances don't return a response
    # with 200 something (2XX = request is a success so flask is running)
    while True:
        connections = [http.client.HTTPConnection(ip) for ip in public_ips]
        for i in range(len(connections)):
            try:
                connections[i].request('GET', '/')
            except:
                connections[i] = FakeConnection()

        codes = [connection.getresponse().code for connection in connections]
        all_ready = True
        
        for code in codes:
            all_ready = all_ready and (code >= 200 and code < 300)
        

        if all_ready:
            break

def get_ip_policy(port:int):
    """
    Helper function for security group, gets an IP policy that uses the Port=port for TCP. CidrIp = 0.0.0.0/0 means that
    this can receive / send traffic from / to the whole internet (receiving if used for authorize_ingress, sending if 
    used for authorize_egress)

    @param port:int Port that we want to use for TCP

    @return         IP policy with the specified port 
    """
    return {
        'FromPort': port,
        'IpProtocol': 'tcp',
        'IpRanges': [
            {
                'CidrIp': '0.0.0.0/0',
                'Description': 'everything'
            },
        ],
        'ToPort': port,
    }

def create_security_group_elb(groupname:str, description:str, listening_ports:"list[int]", dest_ports:"list[int]"):
    """
    Creates a security group for an internet facing application load balancer that can receive traffic and send traffic
    on specified ports.

    @param groupname:str                Name of the security group
    @param description:str              Description of the security group
    @param listening_ports:"list[int]"  Ports of the load balancer listener; inbound traffic can be sent to these ports
    @param dest_ports:"list[int]"       Ports of the instance listeners; outbound traffic can be sent to these ports

    @return                             Response containing the ID of the security group and other data
    """
    
    security_group = ec2.create_security_group(GroupName=groupname, Description=description)
    
    # send to every destination on port 80
    egress_IpPermissions=[]
    for port in dest_ports:
        egress_IpPermissions.append(
            get_ip_policy(port)
        )
    # everyone can send us stuff on the following listening ports
    ingress_IpPermissions=[]
    for port in listening_ports:
        ingress_IpPermissions.append(
            get_ip_policy(port)
        )

    security_group.authorize_ingress(
        IpPermissions=ingress_IpPermissions
    )
    security_group.authorize_egress(
        IpPermissions=egress_IpPermissions
    )
    return security_group

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

print("creating security group for the load balancer")
elb_sec_group = create_security_group_elb("elbSecurityGroup", "securituy group for ELB", [8080, 8000], [80])
print("done")

print("create load balancer: ")
balancer = create_load_balancer("my-load-balancer", [elb_sec_group.id])
balancer_arn = balancer['LoadBalancers'][0]['LoadBalancerArn']
print("done")

print("attach target1")
attach_target_group_to_load_balancer(balancer_arn, target_arn1, 8080)
print("done")

print("attach target 2")
attach_target_group_to_load_balancer(balancer_arn, target_arn2, 8000)
print("done")
from time import time

print("wait until flask has been deployed on all machines:")
t = time()
wait_for_flask(all_instances)
print("total wait time:", time() - t, "seconds")


