from time import sleep
from infra.instance import terminate_instances
from infra.load_balancer import delete_load_balancer, delete_target_group
from infra.utils import delete_security_group, get_infra_info


def teardown_infra(infra_info_path:str):
    """
    Teardown infra using information saved at infra_info_path.

    @param infra_info_path:str    path of a file containing a pickled InfraInfo object 

    @return                       None
    """
    print("Starting teardown")

    infra_info = get_infra_info(infra_info_path)

    for lb_arn in infra_info.load_balancers_arn:
        delete_load_balancer(lb_arn)

    for tg_arn in infra_info.target_groups_arn:
        delete_target_group(tg_arn)

    terminate_instances(infra_info.instances_ids)

    for sec_gp in infra_info.security_groups_ids:
        delete_security_group(sec_gp)

    # Just to have more time for teardown ?
    sleep(60)

    print("Teardown complete")


if __name__ == '__main__':
    teardown_infra('./infra_info')