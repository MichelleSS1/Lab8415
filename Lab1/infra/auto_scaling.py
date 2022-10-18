import boto3

autoscaling = boto3.client('autoscaling')

def create_autoscaling_group(
    group_name:str,
    min_count:int,
    max_count:int,
    target_group_arn:"list[str]",
    availability_zones:"list[str]",
    template_id:str,
    tags:"dict[str, str]"
):
    """
    Create an auto scaling group.

    @param group_name:str                   name of the auto scaling group to be created
    @param min_count:int                    minimum number of instances
    @param max_count:int                    maximum number of instances
    @param target_group_arn:list[str]       target group to be associated to this auto scaling group
    @param availability_zones:list[str]     availability zones, normally only one
    @param template_id:str                  id of the launch template
    @param tags:dict[str, str]          tags to put on instances

    @return                                 None
    """
    print("Creating auto scaling group", group_name)

    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName=group_name,
        MinSize=min_count,
        MaxSize=max_count,
        DesiredCapacity=max_count,
        LaunchTemplate={ 'LaunchTemplateId': template_id, 'Version': '$Latest'},
        AvailabilityZones=availability_zones,
        TargetGroupARNs=target_group_arn,
        Tags=[
            {
                'ResourceId': group_name,
                'ResourceType': 'auto-scaling-group',
                'Key': key,
                'Value': value,
                'PropagateAtLaunch': True
            }
            for key, value in tags.items()
        ],
    )
    
    print("done\n")

def delete_auto_scaling_group(auto_scaling_group:str):
    """
    Delete an autoscaling group by name.

    @param auto_scaling_group:str       name of the autoscaling group

    @return                             None
    """
    print("Deleting autoscaling group", auto_scaling_group)

    autoscaling.delete_auto_scaling_group(AutoScalingGroupName=auto_scaling_group, ForceDelete=True)