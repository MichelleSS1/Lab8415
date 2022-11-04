#!/bin/bash

# Inspired by wordcount.py

rm -f ~/results.txt
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
for i in $(seq 1 3);
do
  { time python3 -c "
import findspark
import shutil
import os
from pyspark.sql import SparkSession
spark = SparkSession.builder.master('local').appName('FirstProgram').getOrCreate()
sc=spark.sparkContext
text_file = sc.textFile('Datasets/*.txt')
counts = text_file.flatMap(lambda line: line.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda x, y: x + y)
if os.path.exists('output/${file}_spark_res/'):
  shutil.rmtree('output/${file}_spark_res/')
counts.saveAsTextFile('output.txt')
sc.stop()
spark.stop()
  " > /dev/null 2>&1 ; } 2>&1 | awk '/real/{print $2}' | awk '{gsub(/0m/, "")}1' | awk '{gsub(/s/, "")}1' >> ~/spark.txt;
done;
