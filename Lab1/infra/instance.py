import boto3

ec2_client = boto3.client('ec2') 
ec2 = boto3.resource('ec2')
elb = boto3.client("elbv2")


def create_ubuntu_instances(
    instance_type:str, 
    min_count:int, 
    max_count:int, 
    key_name:str, 
    user_data:str, 
    subnet_id:str, 
    security_groups:"list[str]"
):
    """
    Create max_count instances, and at least min_count instances if not possible, with instance_type specifying the type
    of machine to be created and security_groups specifying the security groups of each instance. The operating system
    will be ubuntu. The script user_data will be executed on each instance once it's running. 
    They will be located in subnet whose id is subnet_id.

    @param instance_type:str             type of instance, specifies the available CPU, memory, etc. ex. t2.micro
    @param min_count:int                 create at least this many instances
    @param max_count:int                 try to create this many instances
    @param key_name:str                 the name of the key pair used to connect to the instances
    @param user_data:str                script to be executed on startup
    @param subnet_id                    subnet where the machines will be located
    @param security_groups:list[str]    security groups ids to be applied ['sg-id1', 'sg-id2']

    @return                             response containing the instance IDs and other data 
    """
    print("Creating instances of type: ", instance_type)
    instances = ec2.create_instances(
        ImageId='ami-08c40ec9ead489470',
        MinCount=min_count,
        MaxCount=max_count,
        InstanceType=instance_type,
        KeyName=key_name,
        UserData=user_data,
        SubnetId=subnet_id,
        SecurityGroupIds=security_groups
    )

    i = 0
    for instance in instances:
        ec2.create_tags(Resources=[instance.id], Tags=[
            {
                'Key': 'Name',
                'Value': instance_type.replace('.','-') + '-' + str(i),
            },
        ])
        i += 1

    print("done")
    return instances

def create_cluster(name:str, instances_ids:"list[str]", vpc_id:str):
    """
    Creates a target group that contains all the instances specified in instances in the virtual private cloud
    with id = vpc_id; by default there is only one VPC. The protocol used is HTTP (targets receives traffic on port
    80)
    @param name:str                 name of the target group to be created
    @param instances_ids:list[str]  list of the instance ids to be included in that group ['i-id1', 'i-id2']
    @param vpc_id:str               id of the Virtual Private Cloud

    @return:                    response containing the target group, response of registering targets, target group ARN
    """
    print("Creating target group: ", name)

    group = elb.create_target_group(
        Name=name,
        Protocol='HTTP',
        Port=80,
        TargetType='instance',
        IpAddressType='ipv4',
        VpcId=vpc_id
    )

    arn = group["TargetGroups"][0]['TargetGroupArn']
    targets = []

    for instance in instances_ids:
        targets.append({"Id":instance})
    response = elb.register_targets(TargetGroupArn=arn, Targets=targets)

    print("done")
    return response, arn 

def get_stopped_instances_ids(instances_ids:list[str]):
    """
    Retrieve instances whose state is 'shutting-down' | 'terminated' | 'stopping' | 'stopped'.

    @param instances_ids:list[str]     List of instances ids among which to look

    @return                            Found ids
    """
    stopped_instances_ids = []
    instances_to_remove = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'shutting-down', 'terminated', 'stopping', 'stopped'
                ]
            }, 
        ],
        InstanceIds=instances_ids
    )['Reservations']
    if (len(instances_to_remove) > 0):
        instances_to_remove = instances_to_remove[0]['Instances']
        stopped_instances_ids = [instance['InstanceId'] for instance in instances_to_remove]

    return stopped_instances_ids

def terminate_instances(instance_ids:"list[str]"):
    """
    Shuts down one or more instances. This operation is idempotent; if you terminate an instance more than once, each call succeeds.

    @param instance_ids:list    One or more instance IDs.
    @return: dict
    """
    print("Terminating instances")
    return ec2_client.terminate_instances(InstanceIds=instance_ids)