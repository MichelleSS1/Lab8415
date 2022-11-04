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

# Install git and clone Datasets
git clone https://github.com/MichelleSS1/Lab8415.git;

cd Lab8415/Lab2/Wordcount_performances || exit;
git checkout lab2;

# Create a JAR file
hadoop com.sun.tools.javac.Main ./WordCount.java;
jar cf wordcount.jar WordCount*.class;


# Installation of Spark dependencies
sudo apt-get update;
sudo apt install python3-pip -y;
pip install pyspark;

# Run performance tests
./scripts/test_script.sh
