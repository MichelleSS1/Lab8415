import os
import sys
import paramiko
import boto3

ec2 = boto3.resource('ec2')

def run_hadoop_spark_exp():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    with open(os.path.join(sys.path[0], '../infra/public_ip.txt'), 'r') as f:
        public_ip = f.readline()

    pKey_filename = os.path.join(sys.path[0], '../infra/pkey.pem')

    script = ''
    with open(os.path.join(sys.path[0], 'test.sh'), 'r') as f:
        script = f.read()

    print("SSH connection to instance")
    client.connect(hostname=public_ip, port=22, username='ubuntu', key_filename=pKey_filename)
    print("Executing command via SSH")
    _, _, stderr1 = client.exec_command(script)
    _, stdout, stderr2 = client.exec_command('cat ~/results.txt')
    print("done\n\n")

    return stdout, stderr1.write(stderr2)


if __name__ == '__main__':
    stdout, stderr = run_hadoop_spark_exp()

    print("Experiment results:\n")
    for line in stdout:
        print(line)

    print("Error output:\n")
    for line in stderr:
        print(line)
