# MapReduce with Hadoop on AWS
## Running Hadoop

In this lab assignment, you will get hands-on experience running MapReduce on Hadoop and Spark using AWS

Installing Java
```bash
cd ~ || exit;
apt-get update
apt install default-jre -y
apt install default-jdk -y
```

Installing Hadoop

```bash
wget "https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz"
tar -xf hadoop-3.3.4.tar.gz  -C /usr/local/
mv /usr/local/hadoop-* /usr/local/hadoop
```

Setup Hadoop environment variables
```bash
echo "export JAVA_HOME=/usr/lib/jvm/default-java" >> ~/.profile
echo "export PATH=\$HADOOP_HOME/bin:\$PATH"  >>  ~/.profile;
echo "export JAVA_HOME=/usr/lib/jvm/default-java" >> "$HADOOP_HOME"/etc/hadoop/hadoop-env.sh;
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> "$HADOOP_HOME"/etc/hadoop/hadoop-env.sh;
source ~/.profile
```

Setting up HDFS configuration
```bash
touch ~/start-dfs;
{
    echo "export HDFS_NAMENODE_USER=\"root\""
    echo "export HDFS_DATANODE_USER=\"root\""
    echo "export HDFS_SECONDARYNAMENODE_USER=\"root\""
    echo "export YARN_RESOURCEMANAGER_USER=\"root\""
    echo "export YARN_NODEMANAGER_USER=\"root\""  
} >>  ~/.profile;

source ~/.profile;
```

Starting Hadoop
```bash
"$HADOOP_HOME"/sbin/start-dfs.sh;
hdfs dfs -mkdir -p input;
```

Install git and clone Datasets
```bash
apt install git -y;
git clone https://github.com/MichelleSS1/Lab8415.git;
```

Create a JAR file and Executing WordCount
```bash
hadoop com.sun.tools.javac.Main ./WordCount.java;
jar cf wordcount.jar WordCount*.class;

hadoop fs -cp ./pg4300.txt ~/input;
time hadoop jar wordcount.jar WordCount ./input/ ./output
```


## Perform with Linux 

Compute the word frequency of a text with Linux, using Linux commands and pipes with this command:
```bash
time cat pg4300.txt | tr ' ' '\n' | sort | uniq -c >> output.txt
```


## Running Spark
We have based our WordCount.py from the official Spark Repo:
<https://github.com/apache/spark/blob/master/examples/src/main/python/wordcount.py>



Get the spark dependencies
```bash
apt-get update
apt-get install python3-pip  -y
pip install pyspark
```

Example of spark command
```bash
time /usr/local/bin/spark-submit wordCount.py Datasets/input1.txt
```