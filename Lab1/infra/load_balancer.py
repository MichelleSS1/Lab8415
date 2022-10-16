import boto3

elb = boto3.client("elbv2")

def create_load_balancer(name:str, security_group_ids:"list[str]", subnet_ids:"list[str]"):
    """
    creates an internet facing application load balancer with Name=name and the security groups specified in security_group_ids
    the subnets used will be by default us-east-1a and us-east-1b as specified in SUBNETS. IpV4 is used for IP.
    
    @param name: str                        the name of the load balancer
    @param security_group_ids: list[str]    the list of security group IDs (['sg-id1', sg-'id2'])
    @param subnet_ids        : list[str]    the list of subnet IDs (['sn-id1', sn-'id2']), length must be 2 or more

    @return:                                response containing the balancer arn and other data
    """
    print("Creating load balancer: ")

    load_balancer = elb.create_load_balancer(
        Name=name,
        Subnets=subnet_ids,
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4',
        SecurityGroups=security_group_ids
    )

    print("done")
    return load_balancer['LoadBalancers'][0]

def attach_target_group_to_load_balancer(load_balancer_arn:str, target_group_arn:str, port:int):
    """
    attaches target group with ARN = target_group_arn to load balancer with ARN = load_balancer_arn
    the load balancer will listen on Port = port
    
    @param load_balancer_arn:str    ARN of the load balancer
    @param target_group_arn:str     ARN of the target group
    @param port:int                 Port on which the listener will listen
    
    @return: response after creating the listener
    """
    print(f"Attaching target group {target_group_arn} to loadbalancer {load_balancer_arn}")

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

def delete_load_balancer(load_balancer_arn:str):
    """
    Deletes the specified load balancer.

    @param load_balancer_arn:str    The name associated with the load balancer.
    @return:dict.
    """
    print("Deleting load balancer ", load_balancer_arn)
    return elb.delete_load_balancer(LoadBalancerArn=load_balancer_arn)

def delete_target_group(target_group_arn:str):
    """
    Deletes the specified target group..

    @param target_group_arn:str    The Amazon Resource Name (ARN) of the target group.
    @return: dict
    """
    print("Deleting target group ", target_group_arn)
    return elb.delete_target_group(TargetGroupArn=target_group_arn)
