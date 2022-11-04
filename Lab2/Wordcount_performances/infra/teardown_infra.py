import os
import sys
import boto3
from time import sleep
from instance import terminate_instances
from log8415_utils.infra_utils import delete_security_group, get_infra_info


ec2_client = boto3.client('ec2') 

def terminate_instances(instance_ids:"list[str]"):
    """
    Shuts down one or more instances. This operation is idempotent; if you terminate an instance more than once, each call succeeds.

    @param instance_ids:list    One or more instance IDs.
    @return: dict
    """
    print("Terminating instances")
    response = ec2_client.terminate_instances(InstanceIds=instance_ids)
    
    # Wait for instances to terminate
    waiter = ec2_client.get_waiter('instance_terminated')
    waiter.wait(InstanceIds=instance_ids)

    return response


def teardown_infra(infra_info_path:str):
    """
    Teardown infra using information saved at infra_info_path.

    @param infra_info_path:str    path of a file containing a pickled InfraInfo object 

    @return                       None
    """
    print("Starting teardown")

    infra_info = get_infra_info(infra_info_path)

    terminate_instances(infra_info.instances_ids)
    sleep(60)
    
    for sec_gp in infra_info.security_groups_ids:
        try:
            delete_security_group(sec_gp)
        except:
            sleep(60)
            delete_security_group(sec_gp)

    print("Teardown complete")


if __name__ == '__main__':
    teardown_infra(os.path.join(sys.path[0], 'infra_info'))
