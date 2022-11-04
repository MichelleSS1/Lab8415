#!/bin/bash

# Source : https://dzone.com/articles/getting-hadoop-and-running

# Installing Java
cd ~ || exit;
sudo apt install default-jre -y;
sudo apt install default-jdk -y;

# 2. Export the JAVA_HOME environment variable
echo "export JAVA_HOME=/usr/lib/jvm/default-java"  >>  ~/.profile;

# Installing Hadoop
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz;
tar -xf hadoop-3.3.4.tar.gz;

# Setup Hadoop environment variables
echo "export HADOOP_HOME=~/hadoop-3.3.4" >> ~/.profile;
echo "export PATH=\$HADOOP_HOME/bin:\$PATH"  >>  ~/.profile;
echo "export JAVA_HOME=/usr/lib/jvm/default-java" >> "$HADOOP_HOME"/etc/hadoop/hadoop-env.sh;
echo "export HADOOP_HOME=~/hadoop-3.3.4" >> "$HADOOP_HOME"/etc/hadoop/hadoop-env.sh;

source ~/.profile;

# Setup Hadoop property elements

head -n -3 "$HADOOP_HOME"/etc/hadoop/core-site.xml > tmp.txt && mv tmp.txt "$HADOOP_HOME"/etc/hadoop/core-site.xml;
echo "<configuration><property><name>hadoop.tmp.dir</name><value>/var/lib/hadoop</value></property></configuration>" >> "$HADOOP_HOME"/etc/hadoop/core-site.xml;

head -n -4 "$HADOOP_HOME"/etc/hadoop/hdfs-site.xml > tmp.txt && mv tmp.txt "$HADOOP_HOME"/etc/hadoop/hdfs-site.xml;
echo "<configuration><property><name>dfs.replication</name><value>1</value></property></configuration>" >> "$HADOOP_HOME"/etc/hadoop/hdfs-site.xml;


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
sudo apt install git -y;
git clone https://github.com/MichelleSS1/Lab8415.git;

cd Lab8415/Lab2/Wordcount_performances || exit;
git checkout lab2;

# Create a JAR file
hadoop com.sun.tools.javac.Main ./WordCount.java;
jar cf wordcount.jar WordCount*.class;


# Installation of Spark dependencies
sudo apt-get update;
sudo apt install python3-pip -y;
pip install pyspark findspark;

# Run performance tests
./scripts/testing_script.sh
