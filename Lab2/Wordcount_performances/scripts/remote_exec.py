import os
import sys
from time import sleep
import paramiko
import boto3
import pandas as pd
import matplotlib.pyplot as plt

ec2 = boto3.resource('ec2')

def run_hadoop_spark_exp():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

    with open(os.path.join(sys.path[0], '../infra/public_ip.txt'), 'r') as f:
        public_ip = f.readline()

    pKey_filename = os.path.join(sys.path[0], '../infra/pkey.pem')

    script = ''
    with open(os.path.join(sys.path[0], 'hadoop_spark_exp.sh'), 'r') as f:
        script = f.read()

    all_stderr = []

    print("SSH connection to instance")
    client.connect(hostname=public_ip, port=22, username='ubuntu', key_filename=pKey_filename)

    print("Executing tests via SSH. It may take some time.")
    _, stdout, stderr = client.exec_command(command=script, get_pty=True)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        all_stderr.append(stderr)
        print("done\n")
    else:
        raise Exception("Tests execution didn't succeed")

    print("Collecting hadoop results")
    _, hadoop_res, stderr = client.exec_command('cat ~/hadoop.txt', get_pty=True)
    exit_status = hadoop_res.channel.recv_exit_status()
    if exit_status == 0:
        all_stderr.append(stderr)
        print("done\n")
    else:
        raise Exception("Failed to collect hadoop results")

    print("Collecting spark results")
    _, spark_res, stderr = client.exec_command('cat ~/spark.txt', get_pty=True)
    spark_res.channel.recv_exit_status()
    if exit_status == 0:
        all_stderr.append(stderr)
        print("done\n")
    else:
        raise Exception("Failed to collect spark results")

    print("Collecting hadoop vs linux results")
    _, had_vs_linux, stderr = client.exec_command('cat ~/results.txt', get_pty=True)
    exit_status = had_vs_linux.channel.recv_exit_status()
    if exit_status == 0:
        all_stderr.append(stderr)
        print("done\n")
    else:
        raise Exception("Failed to collect hadoop vs linux results")
    
    stderr_lines = []
    for stderr in all_stderr:
        stderr_lines.extend(stderr.readlines()) 

    return hadoop_res, spark_res, had_vs_linux, stderr_lines


if __name__ == '__main__':
    hadoop_res, spark_res, had_vs_linux, stderr = run_hadoop_spark_exp()

    hadoop_res_lines = hadoop_res.readlines()
    with open(os.path.join(sys.path[0], '../hadoop.txt'), 'w') as f:
        f.writelines(hadoop_res_lines)

    spark_res_lines = spark_res.readlines()
    with open(os.path.join(sys.path[0], '../spark.txt'), 'w') as f:
        f.writelines(spark_res_lines)

    had_vs_linux_lines = had_vs_linux.read()
    with open(os.path.join(sys.path[0], '../hadoop_vs_linux.txt'), 'w') as f:
        f.write(had_vs_linux_lines)

    hadoop_scores = []
    spark_scores = []

    print("Experiment results:\n")

    print("Hadoop vs Linux:")
    print(had_vs_linux_lines)

    print("Hadoop:")
    for line in hadoop_res_lines:
        print(line)
        hadoop_scores.append(float(line))

    print("Spark:")
    for line in spark_res_lines:
        print(line)
        spark_scores.append(float(line))

    print("Error output:\n")
    for line in stderr:
        print(line)

    assert len(hadoop_scores) == len(spark_scores)
    
    print("Making plots from results\n")
    result = pd.DataFrame({'hadoop': hadoop_scores, 'spark': spark_scores})

    # Create the graph
    fig, axs = plt.subplots(nrows=1, ncols=3, sharey=True)

    # Define variables x, y for the graph
    x = range(1, len(hadoop_scores) + 1)
    y1 = result['hadoop']     
    y2 = result['spark']

    axs[0].set_title('Hadoop')   
    axs[0].plot(x, y1, 'o-')

    axs[1].set_title('Spark')
    axs[1].plot(x, y2, 'o-')

    axs[2].set_title('Average')   
    axs[2].plot(['Hadoop', 'Spark'], [y1.mean(), y2.mean()], 'o-')

    fig.suptitle('Execution time')
    fig.supylabel('Time (s)')
    fig.supxlabel('Experiment')

    # Save plot and show it 
    plt.savefig(os.path.join(sys.path[0], f'../execution_time.png'), bbox_inches='tight')

    # Close the figure window
    plt.close(fig)

    print("done\n")