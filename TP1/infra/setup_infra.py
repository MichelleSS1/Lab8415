import os
import boto3
import http.client
from infra.load_balancer import attach_target_group_to_load_balancer, create_load_balancer
from infra.utils import InfraInfo, create_security_group, get_key_pair_name, get_subnets, get_vpc_id, save_infra_info, wait_for_flask
from infra.instance import create_cluster, create_ubuntu_instances


elb = boto3.client("elbv2")
ec2_client = boto3.client('ec2')
SSH_PORT = 22
HTTP_PORT = 80


def setup_instances(vpc_id:str, subnet1_id:str, subnet2_id:str): 
    """
    Create all instances and clusters.

    @param vpc_id:str       id of the Virtual Private Cloud
    @param subnet1_id:str   subnet where the first group of instances will be located
    @param subnet2_id:str   subnet where the second group of instances will be located

    @returns                target groups arn
    """
    user_data = ''
    with open('./start_flask_app.sh') as f:
        user_data = f.read()
    
    user_data_gp1 = user_data.replace('<target_group>', '1')
    user_data_gp2 = user_data.replace('<target_group>', '2')

    key_name = get_key_pair_name() 

    sec_group = create_security_group("instances_sec_group", "Security group Lab1", [HTTP_PORT, SSH_PORT], [])
    
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

    print("Wait all of them are in a running state")
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=all_instances_ids)

    wait_for_flask(all_instances)
    print("done")


    # Calls EC2.Client.describe_instances() to update the attributes of the Instance resource.
    print("Reload all instances")
    for instance in all_instances:
        instance.reload()
    print("done")

    attach_succeeded1, target1_arn = create_cluster("target-cluster-1", instances_m4, vpc_id)
    attach_succeeded2, target2_arn = create_cluster("target-cluster-2", instances_t2, vpc_id)

    return sec_group, all_instances_ids, target1_arn, target2_arn

def setup_load_balancer(subnet_ids:list[str], target1_arn:str, target2_arn:str):
    """
    Create load balancer and attach target groups to it.

    @param subnet_ids:list[str]   subnets where the load balancer will access target groups
    @param target1_arn:str        first target group arn
    @param target2_arn:str        second target group arn

    @returns                      load balancer arn
    """
    elb_sec_group = create_security_group("lb_sec_group", "securituy group for ELB", [HTTP_PORT], [HTTP_PORT])
    
    load_balancer = create_load_balancer("lab1-load-balancer", [elb_sec_group.id], subnet_ids)
    load_balancer_arn = load_balancer['LoadBalancerArn']

    attach_target_group_to_load_balancer(load_balancer_arn, target1_arn, HTTP_PORT)
    attach_target_group_to_load_balancer(load_balancer_arn, target2_arn, HTTP_PORT)

    return elb_sec_group, load_balancer


if __name__ == '__main__':
    vpc_id = get_vpc_id()

    subnets = get_subnets(vpc_id)
    subnet1_id = subnets[0]['SubnetId']
    subnet2_id = subnets[1]['SubnetId']

    sec_group, instances_ids, target1_arn, target2_arn = setup_instances(vpc_id, subnet1_id, subnet2_id)
    elb_sec_group, load_balancer = setup_load_balancer([subnet1_id, subnet2_id], target1_arn, target2_arn)

    # Necessary information to teardown infra
    infra_info = InfraInfo(
        security_groups_ids=[sec_group.id, elb_sec_group.id],
        instances_ids=instances_ids,
        target_groups_arn=[target1_arn, target2_arn],
        load_balancers_arn=[load_balancer['LoadBalancerArn']]
    )
    # Save it to a file for later use
    save_infra_info(infra_info, './infra_info')

    # Write load balancer dns name to a file for later use
    with open('./lb_dns_name.txt', 'w') as f:
        f.write(load_balancer['DNSName'])
    
    print("Infrastructure setup complete")