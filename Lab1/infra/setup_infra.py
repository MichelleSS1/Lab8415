import os
import sys
from time import sleep
import boto3
from load_balancer import attach_target_group_to_listener, create_forward_listener, create_load_balancer
from log8415_utils.infra_utils import InfraInfo, create_security_group, filters_from_tags, get_key_pair_name, get_subnets, get_vpc_id, save_infra_info, wait_for_flask
from instance import create_target_group, create_launch_template, get_instances_ids, stopped_instances_ids
from auto_scaling import create_autoscaling_group

elb = boto3.client("elbv2")
ec2_client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

SSH_PORT = 22
HTTP_PORT = 80


def setup_launch_templates(infra_info:InfraInfo): 
    """
    Create launch templates for both target groups.

    @param infra_info:InfraInfo     object that will hold infrastructure information

    @returns                        templates ids, object containing infrastructure information
    """
    user_data = ''
    with open(os.path.join(sys.path[0], 'start_flask_app.sh')) as f:
        user_data = f.read()
    
    user_data_gp1 = user_data.replace('<target_group>', '1')
    user_data_gp2 = user_data.replace('<target_group>', '2')

    key_name = get_key_pair_name() 

    sec_group = create_security_group("instances_sec_group", "Security group Lab1", vpc_id, [HTTP_PORT, SSH_PORT], [])
    infra_info.security_groups_ids.append(sec_group.id)
    
    template1_id = create_launch_template(
        "template1", 
        "m4.large", 
        key_name, 
        user_data_gp1, 
        [sec_group.id],
    )
    infra_info.launch_templates_ids.append(template1_id)

    template2_id = create_launch_template(
        "template2", 
        "t2.large", 
        key_name, 
        user_data_gp2, 
        [sec_group.id],
    )
    infra_info.launch_templates_ids.append(template2_id)

    return infra_info, template1_id, template2_id


def setup_load_balancer(vpc_id:str, subnet_ids:"list[str]", infra_info:InfraInfo):
    """
    Create target groups, load balancer, listener and connect them.

    @param vpc_id:str             id of the Virtual Private Cloud
    @param subnet_ids:list[str]   subnets where the load balancer will access target groups

    @returns                      object containing infrastructure information, load balancer dns name
    """
    target1_arn = create_target_group("target-group-1", vpc_id)
    infra_info.target_groups_arn.append(target1_arn)

    target2_arn = create_target_group("target-group-2", vpc_id)
    infra_info.target_groups_arn.append(target2_arn)
    
    elb_sec_group = create_security_group("lb_sec_group", "securituy group for ELB", vpc_id, [HTTP_PORT], [HTTP_PORT])
    infra_info.security_groups_ids.append(elb_sec_group.id)
    
    load_balancer = create_load_balancer("lab1-load-balancer", [elb_sec_group.id], subnet_ids)
    load_balancer_arn = load_balancer['LoadBalancerArn']
    infra_info.load_balancers_arn.append(load_balancer_arn)

    listener_arn = create_forward_listener(load_balancer_arn, HTTP_PORT, target1_arn, target2_arn)

    rule_arn = attach_target_group_to_listener(listener_arn, target1_arn, '/cluster1', priority=1)
    infra_info.rules_arn.append(rule_arn)

    rule_arn = attach_target_group_to_listener(listener_arn, target2_arn, '/cluster2', priority=2)
    infra_info.rules_arn.append(rule_arn)

    print("Waiting for load balancer to be available")
    sleep(60)
    waiter = elb.get_waiter('load_balancer_available')
    waiter.wait(LoadBalancerArns=[load_balancer_arn])
    print("done\n")

    return infra_info, load_balancer['DNSName']


if __name__ == '__main__':
    vpc_id = get_vpc_id()

    subnets = get_subnets(vpc_id)
    subnet1_id = subnets[0]['SubnetId']
    subnet2_id = subnets[1]['SubnetId']

    availability_zone1 = subnets[0]['AvailabilityZone']
    availability_zone2 = subnets[1]['AvailabilityZone']

    load_balancer_dns_name = ''

    # Necessary information to teardown infra
    infra_info = InfraInfo(
        launch_templates_ids=[],
        auto_scaling_groups=[],
        security_groups_ids=[], 
        instances_tags={},
        target_groups_arn=[], 
        load_balancers_arn=[],
        rules_arn=[]
    )
    try:  
        infra_info, template1_id, template2_id = setup_launch_templates(infra_info)

        elb_sec_group, load_balancer_dns_name = setup_load_balancer(
            vpc_id,
            [subnet1_id, subnet2_id], 
            infra_info
        )

        tags = {'Purpose': 'log8415_lab1'}
        infra_info.instances_tags.update(tags)

        create_autoscaling_group(
            "group1",
            4, 
            5,
            [infra_info.target_groups_arn[0]],
            [availability_zone1],
            template1_id,
            tags
        )
        infra_info.auto_scaling_groups.append("group1")

        create_autoscaling_group(
            "group2",
            4, 
            5,
            [infra_info.target_groups_arn[1]],
            [availability_zone2],
            template2_id,
            tags
        )
        infra_info.auto_scaling_groups.append("group2")
        
        print("Waiting for instances to be in a running state")
        sleep(120)

        filters = filters_from_tags(infra_info.instances_tags)
        instances_ids = get_instances_ids(filters)
        instances_ids_to_wait = [id for id in instances_ids if id not in stopped_instances_ids(instances_ids)]

        waiter = ec2_client.get_waiter('instance_running')
        waiter.wait(InstanceIds=instances_ids_to_wait)

        instances = [ec2.Instance(id) for id in instances_ids_to_wait]
        wait_for_flask(instances)

        print("done\n")

    except:
        raise
    finally:
        # Save it to a file for later use
        save_infra_info(infra_info, os.path.join(sys.path[0], 'infra_info'))

        # Write load balancer dns name to a file for later use
        if len(load_balancer_dns_name) > 0:
            with open(os.path.join(sys.path[0], 'lb_dns_name.txt'), 'w') as f:
                f.write(load_balancer_dns_name)

    print("Infrastructure setup complete")