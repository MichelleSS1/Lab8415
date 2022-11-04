import os
import sys
import paramiko
import boto3

ec2 = boto3.resource('ec2')

def run_hadoop_spark_exp():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    with open(os.path.join(sys.path[0], '../infra/ssh_info.txt'), 'r') as f:
        key_pair = ec2.KeyPair(f.readline())
        public_ip = f.readline()

    script = ''
    with open(os.path.join(sys.path[0], 'hadoop_spark_exp.sh'), 'r') as f:
        script = f.read()

    client.connect(hostname=public_ip, port=22, username='ubuntu', pkey=key_pair.key_material)
    _, stdout, stderr = client.exec_command(script)

    return stdout, stderr


if __name__ == '__main__':
    stdout, stderr = run_hadoop_spark_exp()

    print("Experiment results:", stdout, sep='\n\n', end='\n\n')
    print("Error output:", stderr, sep='\n\n')