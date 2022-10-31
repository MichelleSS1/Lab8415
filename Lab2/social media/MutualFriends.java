//package org.apache.hadoop.examples;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;


public class MutualFriends {

    public static class FriendOfFriendsMapper extends Mapper<Object, Text, Text, Text>{
        
        // private final static IntWritable one = new IntWritable(1);
        private Text userTxt = new Text();
        private Text friendsOfFriend = new Text();
        
        public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
            String adjacence = value.toString();
            String[] userFriends = adjacence.split("\t");
            userTxt.set(userFriends[0]);
            if(userFriends.length == 1){
                // user has not added anyone
                friendsOfFriend.set("\t" + userFriends[0]);
                context.write(userTxt, friendsOfFriend);
            } else {
                String[] friends = userFriends[1].split(",");
                String friendList = userFriends[1] + "\t" + userFriends[0];
                for(String friend:friends) {
                    userTxt.set(friend);
                    friendsOfFriend.set(friendList);
                    context.write(userTxt, friendsOfFriend);
                }
            }
        }
    }
    
    public static class Pair {
        public Integer count;
        public HashSet<String> pair;
        Pair(Integer count, HashSet<String> pair) {
            this.count = count;
            this.pair = pair;
        }
    }
    
    
    public static class SortFriendsReducer extends Reducer<Text,Text,Text,Text> {
        private IntWritable result = new IntWritable();
        // key = user; values = friend of friends \t 
        public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
            HashSet<HashSet<String>> friends = new HashSet<HashSet<String>>();
            HashMap<HashSet<String>, Integer> mutualFriendsCount = new HashMap<HashSet<String>, Integer>();
            HashSet<String> self = new HashSet<String>();
            String user = key.toString();
            self.add(user);
            friends.add(self);
            String[] mutualFriendList;
 
            // for each list of mutual friends
            for (Text val : values) {
                String[] friendsOfFriend = val.toString().split("\t");
                // if the first value is "" (empty string), this person does not have any friends.
                if(friendsOfFriend[0] == "") {

                } else {
                    mutualFriendList = friendsOfFriend[0].split(",");
                    for(String mutualFriend:mutualFriendList) {
                        HashSet<String> pair = new HashSet<String>();
                        pair.add(user); 
                        pair.add(mutualFriend); 
                        if(mutualFriendsCount.containsKey(pair)) {
                            mutualFriendsCount.put(pair, mutualFriendsCount.get(pair) + 1);

                        } else {
                            mutualFriendsCount.put(pair, 1);
                        }
                    }
                }
                // add the friend and user to the set
                try {
                    HashSet<String> friend = new HashSet<String>();
                    friend.add(user);
                    friend.add(friendsOfFriend[1]);
                    friends.add(friend);
                } catch(Exception e) {
                }
            }

            for(HashSet friend: friends){
                mutualFriendsCount.remove(friend);
            }
            ArrayList<Pair> friendAndCountedMutualFriends = new ArrayList<Pair>();
            for(HashSet<String> usrPair:mutualFriendsCount.keySet()) {
                friendAndCountedMutualFriends.add(
                    new Pair(mutualFriendsCount.get(usrPair), usrPair)
                );
            }
            friendAndCountedMutualFriends.sort(new Comparator<Pair>() {
                public int compare(Pair left, Pair right)  {
                    return right.count - left.count; // The order depends on the direction of sorting.
                }
            });

            // DEBUG
            Text debug = new Text();
            try {
                debug.set(new Integer(friendAndCountedMutualFriends.get(0).count).toString());
            } catch(Exception e) {
                debug.set("");
            }
            context.write(key, debug);
        }
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        if (otherArgs.length < 2) {
            System.err.println("Usage: wordcount <in> [<in>...] <out>");
            System.exit(2);
        }
        Job job = Job.getInstance(conf, "MutualFriends");

        job.setJarByClass(MutualFriends.class);
        job.setMapperClass(FriendOfFriendsMapper.class);
        job.setCombinerClass(SortFriendsReducer.class);
        job.setReducerClass(SortFriendsReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        
        for (int i = 0; i < otherArgs.length - 1; ++i) {
            FileInputFormat.addInputPath(job, new Path(otherArgs[i]));
        }
        FileOutputFormat.setOutputPath(job, new Path(otherArgs[otherArgs.length - 1]));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }

}
