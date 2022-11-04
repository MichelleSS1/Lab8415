rm -r /home/ruijieli/Desktop/output
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-17.0.4.1.1-1.fc36.x86_64"
export PATH=${JAVA_HOME}/bin:${PATH}
export HADOOP_CLASSPATH=${JAVA_HOME}/lib/tools.jar

/home/ruijieli/Desktop/hadoop-3.3.4/bin/hadoop com.sun.tools.javac.Main MutualFriends.java Pair.java

jar cf tp1.jar *.class

/home/ruijieli/Desktop/hadoop-3.3.4/bin/hadoop jar tp1.jar MutualFriends /home/ruijieli/Desktop/input /home/ruijieli/Desktop/output
