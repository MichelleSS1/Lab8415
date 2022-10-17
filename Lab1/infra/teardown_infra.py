import os
import sys
from time import sleep
from instance import terminate_instances, get_instances_ids
from load_balancer import delete_load_balancer, delete_rule, delete_target_group
from utils import delete_security_group, filters_from_tags, get_infra_info


def teardown_infra(infra_info_path:str):
    """
    Teardown infra using information saved at infra_info_path.

    @param infra_info_path:str    path of a file containing a pickled InfraInfo object 

    @return                       None
    """
    print("Starting teardown")

    infra_info = get_infra_info(infra_info_path)

    for rule_arn in infra_info.rules_arn:
        delete_rule(rule_arn)

    for lb_arn in infra_info.load_balancers_arn:
        delete_load_balancer(lb_arn)
    sleep(60)

    for tg_arn in infra_info.target_groups_arn:
        delete_target_group(tg_arn)

    # Get instances dynamically
    if (len(infra_info.instances_tags) > 0):
        filters = filters_from_tags(infra_info.instances_tags)
        instances_ids = get_instances_ids(filters)

        terminate_instances(instances_ids)
    
    for sec_gp in infra_info.security_groups_ids:
        try:
            delete_security_group(sec_gp)
        except:
            sleep(60)
            delete_security_group(sec_gp)

    print("Teardown complete")


if __name__ == '__main__':
    teardown_infra(os.path.join(sys.path[0], 'infra_info'))