import os
import sys
from pyspark.sql import SparkSession
import time


spark = SparkSession.builder.master('local').appName('FirstProgram').getOrCreate()
sc = spark.sparkContext

with open('~/spark.txt', 'a+') as f:
    dataset_path = os.path.join(sys.path[0], '../Datasets/*.txt')
    for i in range(3):
        start_time = time.time()

        text_file = sc.textFile(dataset_path)
        counts = text_file.flatMap(lambda line: line.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda x, y: x + y)
        output = counts.collect()

        for (word, count) in output:
            print("%s: %i" % (word, count))

        duration = time.time() - start_time
        f.write(str(duration) + '\n')

sc.stop()
spark.stop()