import os
import sys
from time import sleep
import boto3
from load_balancer import attach_target_group_to_load_balancer, create_load_balancer
from utils import InfraInfo, create_security_group, get_key_pair_name, get_subnets, get_vpc_id, save_infra_info, wait_for_flask
from instance import create_cluster, create_ubuntu_instances, get_stopped_instances_ids


elb = boto3.client("elbv2")
ec2_client = boto3.client('ec2')
SSH_PORT = 22
HTTP_PORT = 80


def setup_instances(vpc_id:str, subnet1_id:str, subnet2_id:str, infra_info:InfraInfo): 
    """
    Create all instances and clusters.

    @param vpc_id:str               id of the Virtual Private Cloud
    @param subnet1_id:str           subnet where the first group of instances will be located
    @param subnet2_id:str           subnet where the second group of instances will be located
    @param infra_info:InfraInfo     object that will hold infrastructure information

    @returns                        object containing infrastructure information
    """
    user_data = ''
    with open(os.path.join(sys.path[0], './start_flask_app.sh')) as f:
        user_data = f.read()
    
    user_data_gp1 = user_data.replace('<target_group>', '1')
    user_data_gp2 = user_data.replace('<target_group>', '2')

    key_name = get_key_pair_name() 

    sec_group = create_security_group("instances_sec_group", "Security group Lab1", vpc_id, [HTTP_PORT, SSH_PORT], [])
    infra_info.security_groups_ids.append(sec_group.id)
    
    instances_m4 = create_ubuntu_instances(
        "m4.large", 
        4, 
        5, 
        key_name, 
        user_data_gp1, 
        subnet1_id, 
        [sec_group.id]
    )
    instances_t2 = create_ubuntu_instances(
        "t2.large", 
        4, 
        5, 
        key_name, 
        user_data_gp2, 
        subnet2_id, 
        [sec_group.id]
    )
    
    all_instances = instances_m4 + instances_t2
    all_instances_ids = [instance.id for instance in all_instances]

    infra_info.instances_ids.extend(all_instances_ids)

    print("Waiting for all of them to be in a running state")
    sleep(60)
    
    # Remove terminating/stopping instances
    all_instances_ids = [id for id in all_instances_ids if id not in get_stopped_instances_ids(all_instances_ids)]

    running_instances_m4 = []
    running_instances_t2 = []
    instances_m4_ids = []
    instances_t2_ids = []
    
    for instance in instances_m4:
        if instance.id in all_instances_ids:
            instances_m4_ids.append(instance.id)
            running_instances_m4.append(instance)
    for instance in instances_t2:
        if instance.id in all_instances_ids:
            instances_t2_ids.append(instance.id)
            running_instances_t2.append(instance)

    all_instances = running_instances_m4 + running_instances_t2

    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=all_instances_ids)

    # Calls EC2.Client.describe_instances() to update the attributes of the Instance resource.
    print("Reload all instances")
    sleep(60)
    for instance in all_instances:
        instance.reload()
    print("done")

    wait_for_flask(all_instances)
    print("done")

    attach_succeeded1, target1_arn = create_cluster("target-cluster-1", instances_m4_ids, vpc_id)
    attach_succeeded2, target2_arn = create_cluster("target-cluster-2", instances_t2_ids, vpc_id)

    infra_info.target_groups_arn.extend([target1_arn, target2_arn])

    return infra_info

def setup_load_balancer(subnet_ids:list[str], target1_arn:str, target2_arn:str, infra_info:InfraInfo):
    """
    Create load balancer and attach target groups to it.

    @param subnet_ids:list[str]   subnets where the load balancer will access target groups
    @param target1_arn:str        first target group arn
    @param target2_arn:str        second target group arn

    @returns                      object containing infrastructure information, load balancer dns name
    """
    elb_sec_group = create_security_group("lb_sec_group", "securituy group for ELB", [HTTP_PORT], [HTTP_PORT])
    infra_info.security_groups_ids.append(elb_sec_group.id)
    
    load_balancer = create_load_balancer("lab1-load-balancer", [elb_sec_group.id], subnet_ids)
    load_balancer_arn = load_balancer['LoadBalancerArn']
    infra_info.load_balancers_arn.append(load_balancer_arn)

    attach_target_group_to_load_balancer(load_balancer_arn, target1_arn, HTTP_PORT)
    attach_target_group_to_load_balancer(load_balancer_arn, target2_arn, HTTP_PORT)

    return infra_info, load_balancer['DNSName']


if __name__ == '__main__':
    vpc_id = get_vpc_id()

    subnets = get_subnets(vpc_id)
    subnet1_id = subnets[0]['SubnetId']
    subnet2_id = subnets[1]['SubnetId']

    load_balancer_dns_name = ''

    # Necessary information to teardown infra
    infra_info = InfraInfo(security_groups_ids=[], instances_ids=[], target_groups_arn=[], load_balancers_arn=[])

    try:
        infra_info = setup_instances(vpc_id, subnet1_id, subnet2_id, infra_info)
        elb_sec_group, load_balancer_dns_name = setup_load_balancer(
            [subnet1_id, subnet2_id], 
            infra_info.target_groups_arn[0], 
            infra_info.target_groups_arn[1],
            infra_info
        )
    except:
        raise
    finally:
        # Save it to a file for later use
        save_infra_info(infra_info, os.path.join(sys.path[0],'./infra_info'))

        # Write load balancer dns name to a file for later use
        if (len(load_balancer_dns_name) > 0):
            with open(os.path.join(sys.path[0],'./lb_dns_name.txt'), 'w') as f:
                f.write(load_balancer_dns_name)

    # infra_info = InfraInfo(
    #     security_groups_ids=[sec_group.id, elb_sec_group.id],
    #     instances_ids=instances_ids,
    #     target_groups_arn=[target1_arn, target2_arn],
    #     load_balancers_arn=[load_balancer['LoadBalancerArn']]
    # )

    print("Infrastructure setup complete")