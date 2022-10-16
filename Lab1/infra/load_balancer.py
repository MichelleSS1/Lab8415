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
    print("Creating load balancer and listener")

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

def create_forward_listener(load_balancer_arn:str, port:int, target1_arn:str, target2_arn:str):
    """
    Create a listener on load balancer with ARN = load_balancer_arn,
    the listener will be on Port = port and forward to two target groups
    
    @param load_balancer_arn:str    ARN of the load balancer
    @param port:int                 Port on which the listener will listen
    @param target1_arn:str          First target group arn
    @param target2_arn:str          Second target group arn

    @return:                        ARN of the created listener
    """
    print(f"Creating forward listener on load balancer {load_balancer_arn} on port {port}")

    response = elb.create_listener(
        DefaultActions=[
            {
                'Type': 'forward',
                'ForwardConfig': {
                    'TargetGroups': [
                        {
                            'TargetGroupArn': target1_arn,
                            'Weight': 50
                        },
                        {
                            'TargetGroupArn': target2_arn,
                            'Weight': 50
                        },
                    ],
                },
            }
        ],
        LoadBalancerArn=load_balancer_arn,
        Port=port,
        Protocol='HTTP',
    )

    print("done")
    return response['Listeners'][0]['ListenerArn']

def attach_target_group_to_listener(listener_arn:str, target_group_arn:str, path:str, priority:int):
    """
    attaches target group with ARN = target_group_arn to listener with ARN = listener_arn,
    the listener will forward to target group for specified path
    
    @param listener_arn:str         ARN of the listener
    @param target_group_arn:str     ARN of the target group
    @param path:str                 Path on which the listener will forward to target group
    @param priority:int             Rule priority
    
    @return:                        arn of rule created
    """
    print(f"Attaching target group {target_group_arn} to listener {listener_arn}")

    response = elb.create_rule(
        ListenerArn=listener_arn,
        Conditions=[
            {
                'Field': 'path-pattern',
                'PathPatternConfig': {
                    'Values': [
                        path
                    ]
                },
            },
        ],
        Priority=priority,
        Actions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_arn,
            }
        ]
    )

    print("done")
    return response['Rules'][0]['RuleArn']

def delete_load_balancer(load_balancer_arn:str):
    """
    Deletes the specified load balancer.

    @param load_balancer_arn:str    The arn associated with the load balancer.
    @return:dict.
    """
    print("Deleting load balancer ", load_balancer_arn)
    return elb.delete_load_balancer(LoadBalancerArn=load_balancer_arn)

def delete_rule(rule_arn:str):
    """
    Deletes the specified rule.

    @param rule_arn:str             The arn associated with the rule.
    @return:dict.
    """
    print("Deleting rule ", rule_arn)
    return elb.delete_rule(RuleArn=rule_arn)

def delete_target_group(target_group_arn:str):
    """
    Deletes the specified target group..

    @param target_group_arn:str    The Amazon Resource Name (ARN) of the target group.
    @return: dict
    """
    print("Deleting target group ", target_group_arn)
    return elb.delete_target_group(TargetGroupArn=target_group_arn)
