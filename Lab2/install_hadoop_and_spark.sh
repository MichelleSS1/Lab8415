#!/bin/bash

# Source : https://dzone.com/articles/getting-hadoop-and-running

# Installing Java
cd ~ || exit;
apt install -y default-jdk;
apt install default-jre -y;
apt install default-jdk -y;

# 2. Export the JAVA_HOME environment variable
echo "export JAVA_HOME=/usr/lib/jvm/default-java"  >>  ~/.profile;

# Installing Hadoop
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz;
tar -xf hadoop-3.3.4.tar.gz -C /usr/local/;

# Setup Hadoop environment variables
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> ~/.profile;
echo "export PATH=\$HADOOP_HOME/bin:\$PATH"  >>  ~/.profile;
echo "export JAVA_HOME=/usr/lib/jvm/default-java" >> "$HADOOP_HOME"/etc/hadoop/hadoop-env.sh;
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> "$HADOOP_HOME"/etc/hadoop/hadoop-env.sh;

source ~/.profile;

# Setup Hadoop property elements

head -n -3 "$HADOOP_HOME"/etc/hadoop/core-site.xml > tmp.txt && mv tmp.txt "$HADOOP_HOME"/etc/hadoop/core-site.xml;
echo "<configuration><property><name>hadoop.tmp.dir</name><value>/var/lib/hadoop</value></property></configuration>" >> "$HADOOP_HOME"/etc/hadoop/core-site.xml;

head -n -4 "$HADOOP_HOME"/etc/hadoop/hdfs-site.xml > tmp.txt && mv tmp.txt "$HADOOP_HOME"/etc/hadoop/hdfs-site.xml;
echo "<configuration><property><name>dfs.replication</name><value>1</value></property></configuration>" >> "$HADOOP_HOME"/etc/hadoop/hdfs-site.xml;


# Setting Up SSH
apt install -y ssh;

ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa;
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys;
chmod 0600 ~/.ssh/authorized_keys;

mkdir /var/lib/hadoop;
chmod 777 /var/lib/hadoop;

# Formatting the HDFS Filesystem
hdfs namenode -format;

# Setting up HDFS configuration
touch ~/start-dfs;
{
    echo "export HDFS_NAMENODE_USER=\"root\""
    echo "export HDFS_DATANODE_USER=\"root\""
    echo "export HDFS_SECONDARYNAMENODE_USER=\"root\""
    echo "export YARN_RESOURCEMANAGER_USER=\"root\""
    echo "export YARN_NODEMANAGER_USER=\"root\""  
} >>  ~/.profile;

source ~/.profile;

# Starting Hadoop
"$HADOOP_HOME"/sbin/start-dfs.sh;

# Creating Input
hdfs dfs -mkdir -p input;

# Install git and clone Datasets
apt install git -y;
git clone https://github.com/MichelleSS1/Lab8415.git;

cd Lab2 || exit;

# Create a JAR file
hadoop com.sun.tools.javac.Main ./WordCount.java;
jar cf wordcount.jar WordCount*.class;

# Executing Wordcount
hadoop fs -cp ./pg4300.txt ~/input;
hadoop jar wordcount.jar WordCount ./input/ ./output


# Installation of Spark dependencies
apt-get update;
apt install python3-pip -y;
pip install pyspark findspark;
