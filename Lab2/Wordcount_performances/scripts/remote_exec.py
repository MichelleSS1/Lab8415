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

    print("SSH connection to instance")
    client.connect(hostname=public_ip, port=22, username='ubuntu', key_filename=pKey_filename)

    print("Executing tests via SSH. It may take some time.")
    _, _, stderr1 = client.exec_command(command=script, get_pty=True)
    sleep(15)

    _, hadoop_res, stderr2 = client.exec_command('cat ~/hadoop.txt')
    _, spark_res, stderr3 = client.exec_command('cat ~/spark.txt')

    print("done\n")

    stderr = stderr1.readlines() + stderr2.readlines() + stderr3.readlines()

    return hadoop_res, spark_res, stderr


if __name__ == '__main__':
    hadoop_res, spark_res, stderr = run_hadoop_spark_exp()

    
    with open(os.path.join(sys.path[0], '../hadoop.txt'), 'w') as f:
        f.writelines(hadoop_res)

    with open(os.path.join(sys.path[0], '../spark.txt'), 'w') as f:
        f.writelines(spark_res)

    hadoop_scores = []
    spark_scores = []

    print("Experiment results:\n")

    print("Hadoop:")
    for line in hadoop_res:
        print(line)
        hadoop_scores.append(float(line))

    print("Spark:")
    for line in spark_res:
        print(line)
        spark_scores.append(float(line))

    print("Error output:\n")
    for line in stderr:
        print(line)

    print("Making plots from results")
    result = pd.DataFrame({'hadoop': hadoop_scores, 'spark': spark_scores})

    # Create the graph
    fig, axs = plt.subplots(nrows=1, ncols=3, sharey=True)

    # Define variables x, y for the graph
    x = range(1, 4)
    y1 = result['hadoop']     
    y2 = result['spark']

    axs[0].set_title('Hadoop')   
    axs[0].plot(x, y1, 'o-')

    axs[1].set_title('Spark')
    axs[1].plot(x, y2, 'o-')

    axs[2].set_title('Average')   
    axs[2].plot(['Hadoop', 'Spark'], [y1.mean(), y2.mean()], 'o-')

    axs[0].set_ylabel('Time (s)')
    
    fig.suptitle('Execution time')

    # Save plot and show it 
    plt.savefig(os.path.join(sys.path[0], f'../execution_time.png'), bbox_inches='tight')

    # Close the figure window
    plt.close(fig)
    
    print("done\n")