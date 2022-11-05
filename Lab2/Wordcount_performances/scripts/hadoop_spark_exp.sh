#!/bin/bash

# Source : https://dzone.com/articles/getting-hadoop-and-running

# Installing Java
cd ~ || exit
sudo apt install default-jre -y
sudo apt install default-jdk -y

# 2. Export the JAVA_HOME environment variable
echo "export JAVA_HOME=/usr/lib/jvm/default-java"  >>  ~/.profile

# Installing Hadoop
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz
tar -xf hadoop-3.3.4.tar.gz

# Setup Hadoop environment variables
echo "export HADOOP_HOME=~/hadoop-3.3.4" >> ~/.profile
echo "export PATH=\$HADOOP_HOME/bin:\$PATH"  >>  ~/.profile
echo "export JAVA_HOME=/usr/lib/jvm/default-java" >> "$HADOOP_HOME"/etc/hadoop/hadoop-env.sh
echo "export HADOOP_HOME=~/hadoop-3.3.4" >> "$HADOOP_HOME"/etc/hadoop/hadoop-env.sh

source ~/.profile

# Install git and clone Datasets
git clone https://github.com/MichelleSS1/Lab8415.git

cd Lab8415/Lab2/Wordcount_performances || exit

# Create a JAR file
hadoop com.sun.tools.javac.Main ./WordCount.java
jar cf wordcount.jar WordCount*.class


# Installation of Spark dependencies
sudo apt-get update
sudo apt install python3-pip -y
pip install pyspark

# Run performance tests

# Creating Input
hdfs dfs -mkdir -p input
hdfs dfs -copyFromLocal pg4300.txt input

# Compute the word frequency of the pg4300 dataset using Hadoop
echo -n "Hadoop - pg4300" >> ~/results.txt
{ 
  time hadoop jar ./wordcount.jar WordCount ./input/ ./output > /dev/null 2>&1 ;
} 2>> ~/results.txt

echo "" >> ~/results.txt

# 2. Compute the word frequency of the pg4300 dataset using Linux
echo -n "Linux - pg4300" >> ~/results.txt
{ 
  time cat ./pg4300.txt | tr ' ' '\n' | sort | uniq -c > /dev/null 2>&1 ;
} 2>> ~/results.txt

echo "" >> ~/results.txt


# Compute WordCount using Hadoop on the datasets 
for i in $(seq 1 3)
do
  { 
    time hadoop jar ./wordcount.jar WordCount ./Datasets/ ./output > /dev/null 2>&1 ; 
  } 2>&1 | awk '/real/{print $2}' | awk '{gsub(/0m/, "")}1' | awk '{gsub(/s/, "")}1' >> ~/hadoop.txt
done


# Compute WordCount using Spark on the datasets
for i in $(seq 1 3)
do
  { time python3 -c "
import findspark
import shutil
from pyspark.sql import SparkSession
spark = SparkSession.builder.master('local').appName('FirstProgram').getOrCreate()
sc=spark.sparkContext
text_file = sc.textFile('Datasets/*.txt')
counts = text_file.flatMap(lambda line: line.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda x, y: x + y)
output = counts.collect()
for (word, count) in output:
  print("%s: %i" % (word, count))
counts.saveAsTextFile('output.txt')
sc.stop()
spark.stop()
  " > /dev/null 2>&1 ; } 2>&1 | awk '/real/{print $2}' | awk '{gsub(/0m/, "")}1' | awk '{gsub(/s/, "")}1' >> ~/spark.txt
done
