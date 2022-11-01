//package org.apache.hadoop.examples;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
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
            // the idea is, write, for each friend f of n, f --> n TAB friends of n
            // this way, for example, for user u with friends q, w, e and r, the reducer will see
            // the reducer sees:
            // u --> friends of q, ex. [1 3 5 6]
            // u --> friends of w, ex. [7 3 2 6]
            // u --> friends of e, ex. [8 9 8 6]
            // u --> friends of r, ex. [1 9 5 6]
            // this way we see that 6 has 4 mutual friends with u, 5 and 3 has 2, etc. 

            if(userFriends.length == 1){
                // user has not added anyone
                String friendListNull = userFriends[0] + "\t" + "null";
                friendsOfFriend.set(friendListNull);
                context.write(userTxt, friendsOfFriend);
            } else {
                String[] friends = userFriends[1].split(",");
                String friendList = userFriends[0] + "\t" + userFriends[1];
                friendsOfFriend.set(friendList);
                for(String friend:friends) {
                    userTxt.set(friend);
                    context.write(userTxt, friendsOfFriend);
                }
            }
        }
    }
    
    public static class Pair {
        public Integer count;
        public String uid;
        Pair(Integer count, String uid) {
            this.count = count;
            this.uid = uid;
        }
    }
    
    
    public static class SortFriendsReducer extends Reducer<Text,Text,Text,Text> {
        // private IntWritable result = new IntWritable();
        public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {

            // this hashset contains all the people that the user has already added
            // for example, 1--2, 1--3 and 2--3, when processing 2 the program will see that 3 is a mutual friend of 2 and 1
            // this will remove these from suggestions
            HashSet<HashSet<String>> friends = new HashSet<HashSet<String>>();

            // this uses a hashset as a key, the hashset containing set(user, potential suggestedfriend) --> number of mutual friends 
            HashMap<HashSet<String>, Integer> mutualFriendsCount = new HashMap<HashSet<String>, Integer>();

            // this is a hashset with only the user in it
            // the data contained is set("user-number")
            HashSet<String> self = new HashSet<String>();
            String user = key.toString();
            self.add(user);
            friends.add(self);

            Text debug;
            for (Text val : values) {
                String[] friendsOfFriend = val.toString().split("\t");
                String[] potentialFriends = friendsOfFriend[1].split(",");
                HashSet<String> alreadyAdded = new HashSet<String>(){};
                if(friendsOfFriend[0] != "null"){
                    alreadyAdded.add(friendsOfFriend[0]);
                    alreadyAdded.add(user);
                }
                friends.add(alreadyAdded);
                for(String potentialFriend:potentialFriends) {
                    HashSet<String> mutualFriend = new HashSet<String>();
                    mutualFriend.add(user);
                    mutualFriend.add(potentialFriend);
                    if(mutualFriendsCount.containsKey(mutualFriend)) {
                        mutualFriendsCount.put(mutualFriend, mutualFriendsCount.get(mutualFriend) + 1);
                    } else {
                        mutualFriendsCount.put(mutualFriend, 1);
                    }
                }

            }

            for(HashSet<String> friend:friends) {
                mutualFriendsCount.remove(friend);
            }
            
            ArrayList<Pair> ranked = new ArrayList<Pair>(mutualFriendsCount.size());
            for(HashSet<String> mutualFriend:mutualFriendsCount.keySet()) {
                Integer count = mutualFriendsCount.get(mutualFriend);
                mutualFriend.remove(user);
                String uid = mutualFriend.toArray()[0].toString();
                ranked.add(new Pair(count, uid));
            }
            ranked.sort(new Comparator<Pair>() {
                public int compare(Pair left, Pair right) {
                    return right.count - left.count;
                }
            });
            
            int size = ranked.size() < 10 ? ranked.size(): 10;

            String suggested = "";
            // DEBUG
            // Change count.toString() to uid
            for(int i = 0; i < size; i++){
                if(i == 0) {
                    suggested += ranked.get(i).uid;
                } else {
                    suggested += ("," + ranked.get(i).uid);
                }
            }

            Text suggestedWrittable = new Text();
            suggestedWrittable.set(suggested);
            // collect all the users to the next step
            context.write(new Text("lessThan10"), new Text(user + '|' + Integer.valueOf(ranked.size()).toString()));
            // only those that have less than 10 need this step
            if(size < 10) {
                context.write(new Text("lessThan10"), new Text(user + '.' + Integer.valueOf(ranked.size()).toString()));
            } else {
                // if they already have 10, they can be written to directly
                context.write(key, suggestedWrittable);
            }
        }
    }

    public static class SuggestOtherFriendsMapper extends Mapper<Object, Text, Text, Text> {
        public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
            String[] s = value.toString().split("\t");
            context.write(new Text(s[0]), new Text(s[1]));
        }
    }

    // for those who have less than 10, suggest 10 randoms ones.
    // a better algorithm could look for friends of friends of friends
    // or look for the most popular ones
    public static class AddRandomReducer extends Reducer<Text,Text,Text,Text> {
        public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
            ArrayList<Pair> users = new ArrayList<Pair>();
            ArrayList<String[]> lessThan10 = new ArrayList<String[]>();
            for(Text val:values){
                if(key.toString() != "lessThan10") {
                    context.write(key, val);
                } else {
                    String[] ranked = val.toString().split("|");
                    String[] friends = val.toString().split(".");
                    if(friends.length < 2) { // can't split by | so it's the rank
                        users.add(new Pair(Integer.valueOf(ranked[1]), ranked[0]));
                    } else {
                        lessThan10.add(friends);
                    }
                }
            }

            users.sort(new Comparator<Pair>() {
                public int compare(Pair left, Pair right) {
                    return right.count - left.count;
                }
            });

            for(String[] val:lessThan10) {
                String uid = val[0];
                String[] tmp = val[1].split(",");
                HashSet<String> friends = new HashSet<String>();
                for(String f:tmp) {
                    friends.add(f);
                }

                for(Pair usr: users) {
                    if(friends.size() == 10) {
                        break;
                    }
                    if(!friends.contains(usr.uid)) {
                        val[1] += ("," + usr.uid); 
                    }
                }
                context.write(new Text(uid), new Text(val[1]));

            }


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
        job.setReducerClass(SortFriendsReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        
        for (int i = 0; i < otherArgs.length - 1; ++i) {
            FileInputFormat.addInputPath(job, new Path(otherArgs[i]));
        }

        String tmp = otherArgs[otherArgs.length - 1] + "/tmp_output_job1";
        // FileOutputFormat.setOutputPath(job, new Path(otherArgs[otherArgs.length - 1]));
        FileOutputFormat.setOutputPath(job, new Path(tmp));

        job.waitForCompletion(true);
        String out = otherArgs[otherArgs.length - 1];
        Configuration conf2 = new Configuration();
        Job job2 = Job.getInstance(conf2, "AddMoreFriends");
        job2.setJarByClass(MutualFriends.class);
        job2.setMapperClass(SuggestOtherFriendsMapper.class);
        job2.setReducerClass(AddRandomReducer.class);
        job2.setOutputKeyClass(Text.class);
        job2.setOutputValueClass(Text.class);
        FileInputFormat.addInputPath(job2, new Path(tmp));
        FileOutputFormat.setOutputPath(job2, new Path(out + "/job2"));

        

        System.exit(job2.waitForCompletion(true) ? 0 : 1);
    }

}
