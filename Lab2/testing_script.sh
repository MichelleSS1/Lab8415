#!/bin/bash

# Inspired by wordcount.py

# Compute the word frequency of the pg4300 dataset using Hadoop
echo -n "Hadoop - pg4300" >> results.txt;
{ 
  time hadoop jar files/wc.jar WordCount ./input/ ./output 2>1;
} 2>> results.txt;

echo "" >> results.txt;

# 2. Compute the word frequency of the pg4300 dataset using Linux
echo -n "Linux - pg4300" >> results.txt;
{ 
  time cat ./pg4300.txt | tr ' ' '\n' | sort | uniq -c 2>1;
} 2>> results.txt;

echo "" >> results.txt;


# Compute WordCount using Hadoop on the datasets 
echo '---- Hadoop Spark -----' >> results.txt;
for file in $(ls ~/Datasets/)
do
  echo -n $file >> results.txt;
  hadoop fs -rm -r ./input/;
  hadoop fs -rm -r ./output_$file/;
  hdfs dfs -mkdir -p input;
  hadoop fs -cp ~/Datasets/$file ~/input/;
  { time hadoop jar files/wc.jar WordCount ./input/ ./output_$file 2>1; } 2>> results.txt;
  echo "" >> results.txt;
done;



# Compute WordCount using Spark on the datasets
echo '---- Apache Spark -----' >> results.txt;
for file in $(ls ~/Datasets/)
do
  # Remove file extensions
  filename=$(echo $file);
  echo -n $filename >> results.txt;
  { time python3 -c "
import findspark
import shutil
import os
from pyspark.sql import SparkSession
spark = SparkSession.builder.master('local').appName('FirstProgram').getOrCreate()
sc=spark.sparkContext
text_file = sc.textFile('Datasets/${file}')
counts = text_file.flatMap(lambda line: line.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda x, y: x + y)
if os.path.exists('output/${filename}_spark_res/'):
  shutil.rmtree('output/${filename}_spark_res/')
counts.saveAsTextFile('output/${filename}_spark_res/')
sc.stop()
spark.stop()
  "2>1; } 2>> results.txt;
  echo "" >> results.txt;
done;

echo "" >> results.txt;

