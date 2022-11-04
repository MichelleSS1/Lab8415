#!/bin/bash

# Inspired by wordcount.py

# Creating Input
hdfs dfs -mkdir -p input;
hdfs dfs -copyFromLocal pg4300.txt input

# Compute the word frequency of the pg4300 dataset using Hadoop
echo -n "Hadoop - pg4300" >> ~/results.txt;
{ 
  time hadoop jar ./wordcount.jar WordCount ./input/ ./output > /dev/null 2>&1 ;
} 2>> ~/results.txt;

echo "" >> ~/results.txt;

# 2. Compute the word frequency of the pg4300 dataset using Linux
echo -n "Linux - pg4300" >> ~/results.txt;
{ 
  time cat ./pg4300.txt | tr ' ' '\n' | sort | uniq -c > /dev/null 2>&1 ;
} 2>> ~/results.txt;

echo "" >> ~/results.txt;


# Compute WordCount using Hadoop on the datasets 
for i in $(seq 1 3);
do
  { 
    time hadoop jar ./wordcount.jar WordCount ./Datasets/ ./output > /dev/null 2>&1 ; 
  } 2>&1 | awk '/real/{print $2}' | awk '{gsub(/0m/, "")}1' | awk '{gsub(/s/, "")}1' >> ~/hadoop.txt;
done;

# Compute WordCount using Spark on the datasets
BASEDIR=$(dirname "$0")
python3 ${BASEDIR}/spark_exp.py
