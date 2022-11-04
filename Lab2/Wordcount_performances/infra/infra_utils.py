import boto3
import pickle
from dataclasses import dataclass
from ipaddress import IPv4Network


ec2_client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

@dataclass
class InfraInfo:
    """
    Class to store infra details
    """
    instances_ids:"list[str]"
    security_groups_ids:"list[str]"


def get_key_pair(name):
    """
    Returns a key pair.
    """
    ec2_client.delete_key_pair(KeyName=name)
    key_pair = ec2_client.create_key_pair(KeyName=name)

    return key_pair

def get_vpc_id():
    """
    Returns the default Virtual Private Cloud ID.
    """
    vpcs = ec2_client.describe_vpcs()['Vpcs']
    selected_vpc = ''

    if len(vpcs) > 0:
        for vpc in vpcs:
            if vpc['IsDefault']:
                selected_vpc = vpc['VpcId']
                return selected_vpc
    else:
        # Create a vpc if we don't already have one
        selected_vpc = ec2_client.create_vpc(CidrBlock='172.31.0.0/16')['Vpc']['VpcId']

    return selected_vpc

def get_subnets(vpc_id:str):
    """
    Retrieve all subnets in vpc with id vpc_id otherwise make sure we have at least 2 subnets in the vpc and return them

    @param vpc_id:str   Virtual Private Cloud ID where to get/create subnets

    @return             list of dict representing subnets
    """
    subnets = ec2_client.describe_subnets(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )['Subnets']

    if len(subnets) == 0:
        # Create two subnets in vpc if none

        vpc_cidr = ec2_client.describe_vpcs(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Vpcs'][0]['CidrBlock']
        vpc_net = IPv4Network(vpc_cidr)
        vpc_subnets = list(vpc_net.subnets())
        assert len(vpc_subnets) >= 2

        subnets.append(ec2_client.create_subnet(CidrBlock=str(vpc_subnets[0]), VpcId=vpc_id)['Subnet'])
        subnets.append(ec2_client.create_subnet(CidrBlock=str(vpc_subnets[1]), VpcId=vpc_id)['Subnet'])
    elif len(subnets) == 1:
        # Create a 2nd subnet in vpc if only one 

        sn_cidr = subnets[0]['CidrBlock']
        sn_mask = sn_cidr.split("/", 1)[1]
        
        vpc_cidr = ec2_client.describe_vpcs(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Vpcs'][0]['CidrBlock']
        vpc_net = IPv4Network(vpc_cidr)
        # Get subnets in vpc network based on first subnet mask
        vpc_subnets = list(vpc_net.subnets( new_prefix=int(sn_mask) ))
        assert len(vpc_subnets) >= 2

        # Find a cidr different from the first subnet one
        cidr = str(vpc_subnets[0]) if str(vpc_subnets[0]) != sn_cidr else str(vpc_subnets[1])
        subnets.append(ec2_client.create_subnet(CidrBlock=cidr, VpcId=vpc_id)['Subnet'])

    return subnets

def get_ip_policy(port:int):
    """
    Helper function for security group, gets an IP policy that uses the Port=port for TCP. CidrIp = 0.0.0.0/0 means that
    this can receive / send traffic from / to the whole internet (receiving if used for authorize_ingress, sending if 
    used for authorize_egress)

    @param port:int Port that we want to use for TCP

    @return         IP policy with the specified port 
    """
    return {
        'FromPort': port,
        'IpProtocol': 'tcp',
        'IpRanges': [
            {
                'CidrIp': '0.0.0.0/0',
                'Description': 'everything'
            },
        ],
        'ToPort': port,
    }

def create_security_group(group_name:str, description:str, vpc_id:str, listening_ports:"list[int]", dest_ports:"list[int]"):
    """
    Creates a security group for an internet facing application load balancer that can receive traffic and send traffic
    on specified ports.

    @param group_name:str               Name of the security group
    @param description:str              Description of the security group
    @param vpc_id:str                   Virtual Private Cloud ID where to create security_group
    @param listening_ports:"list[int]"  Ports of the load balancer listener; inbound traffic can be sent to these ports
    @param dest_ports:"list[int]"       Ports of the instance listeners; outbound traffic can be sent to these ports

    @return                             Response containing the ID of the security group and other data
    """
    print("Creating security group: ", group_name)

    security_group = ec2.create_security_group(GroupName=group_name, Description=description, VpcId=vpc_id)
    
    if len(listening_ports) > 0:
        # everyone can send us stuff on the following listening ports
        ingress_IpPermissions=[]
        for port in listening_ports:
            ingress_IpPermissions.append(
                get_ip_policy(port)
            )

        security_group.authorize_ingress(
            IpPermissions=ingress_IpPermissions
        )

    if len(dest_ports) > 0:
        # send to every destination on port 80
        egress_IpPermissions=[]
        for port in dest_ports:
            egress_IpPermissions.append(
                get_ip_policy(port)
            )

        security_group.authorize_egress(
            IpPermissions=egress_IpPermissions
        )

    print("done\n")
    return security_group

def delete_security_group(group_id:str):
    """
    Delete a security group from your account.

    @param group_id:str    id of the security group
    @return                 True if successful.
    """
    print("Deleting security group: ", group_id)
    return ec2_client.delete_security_group(GroupId=group_id)

def save_infra_info(infra_info:InfraInfo, path:str):
    """
    Store infrastructure details in a file.

    @param infra_info:InfraInfo   object containing infrastructure details
    @param path:str               file path

    @return                       None
    """
    with open(path, 'wb') as f:
        pickle.dump(infra_info, f, pickle.HIGHEST_PROTOCOL)
    
def get_infra_info(path:str):
    """
    Retrieve infrastructure details from a file.

    @param path:str               file path

    @return                       object of type InfraInfo
    """
    with open(path, 'rb') as f:
        infra_info = pickle.load(f)

    return infra_info
