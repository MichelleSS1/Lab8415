import os
import sys
import boto3
from infra_utils import InfraInfo, create_security_group, get_key_pair, get_subnets, get_vpc_id, save_infra_info

ec2_client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

SSH_PORT = 22


def create_ubuntu_instances(
    instance_type:str, 
    min_count:int, 
    max_count:int, 
    key_name:str, 
    subnet_id:str, 
    security_groups:"list[str]",
    tags:"dict[str, str]"
):
    """
    Create max_count instances, and at least min_count instances if not possible, with instance_type specifying the type
    of machine to be created and security_groups specifying the security groups of each instance. The operating system
    will be ubuntu.
    They will be located in subnet whose id is subnet_id.

    @param instance_type:str            type of instance, specifies the available CPU, memory, etc. ex. t2.micro
    @param min_count:int                create at least this many instances
    @param max_count:int                try to create this many instances
    @param key_name:str                 the name of the key pair used to connect to the instances
    @param subnet_id                    subnet where the machines will be located
    @param security_groups:list[str]    security groups ids to be applied ['sg-id1', 'sg-id2']
    @param tags:dict[str, str]          tags to put on instances

    @return                             response containing the instance IDs and other data 
    """
    print("Creating instances of type: ", instance_type)
    instances = ec2.create_instances(
        ImageId='ami-08c40ec9ead489470',
        MinCount=min_count,
        MaxCount=max_count,
        InstanceType=instance_type,
        KeyName=key_name,
        SubnetId=subnet_id,
        SecurityGroupIds=security_groups,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': key,
                        'Value': value
                    }
                    for key, value in tags.items()
                ]
            }
        ]
    )

    i = 0
    for instance in instances:
        ec2.create_tags(Resources=[instance.id], Tags=[
            {
                'Key': 'Name',
                'Value': instance_type.replace('.','-') + '-' + str(i)
            },
        ])
        i += 1

    print("done\n")
    return instances


if __name__ == '__main__':
    vpc_id = get_vpc_id()

    subnets = get_subnets(vpc_id)
    subnet1_id = subnets[0]['SubnetId']

    # Necessary information to teardown infra
    infra_info = InfraInfo(
        instances_ids=[],
        security_groups_ids=[], 
    )
    try:  
        
        security_group = create_security_group('lab2-sg', "Lab2", vpc_id, [SSH_PORT], [])
        infra_info.security_groups_ids.append(security_group.id)

        key_pair = get_key_pair('log8415-lab2-key')
        instance = create_ubuntu_instances("m4.large", 1, 1, key_pair['KeyName'], subnet1_id, [security_group.id], {'lab': 'lab2'})[0]
        infra_info.instances_ids.append(instance.id)

        print("Waiting for instance to be in a running state")
        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=[instance.id])
        instance.reload()
        print("done\n")

        print("Storing instance public ip and private key for ssh")
        with open(os.path.join(sys.path[0], 'public_ip.txt'), 'w') as f:
            f.write(instance.public_ip_address)

        with open(os.path.join(sys.path[0], 'pkey.pem'), 'w') as f:
            f.write(key_pair['KeyMaterial'])

        print("done\n")

    except:
        raise
    finally:
        # Save it to a file for later use
        save_infra_info(infra_info, os.path.join(sys.path[0], 'infra_info'))

    print("Infrastructure setup complete")