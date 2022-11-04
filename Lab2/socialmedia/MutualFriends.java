// package socialmedia;

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

// import mutualfriends.Utility;

public class MutualFriends {

    public static class FriendOfFriendsMapper extends Mapper<Object, Text, Text, Text>{
        
        // private final static IntWritable one = new IntWritable(1);
        private Text userTxt = new Text();
        private Text friendsOfFriend = new Text();

        /*
         * @param key:object        Not really used
         * @param value:Text        This contains a line in the input file, in the format of userId TAB FriendId,Friend2Id etc.
         *                          Friend1Id,Friend2Id etc. being the list of friends of 1 e.g. 0\t1,2,3,4,5
         * @param context: Context  Used in this method to allow the mapper to communicate with the reducer 
         * 
         * This method takes lines in the format of userID TAB Friend1Id,Friend2Id e.g. 1\t2,3,4,5, and for each friend of userID,
         * it outputs a line in the format of
         * key   = user ID of a friend in the list of friends
         * value = user ID of the user + TAB + list of friends of the user
         * for example, with 1\t2,3,4,5, 1 is the user, 2,3,4,5 are friends of 1, this method will output to the reducer:
         * 
         * key   = 2
         * value = 1\t2,3,4,5
         * 
         * key   = 3
         * value = 1\t2,3,4,5
         * 
         * key   = 4
         * value = 1\t2,3,4,5
         *  
         * key   = 5
         * value = 1\t2,3,4,5
         * 
         * This will then allow the reducer to collect each user, along with all their friends of friends
        */
        public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
            
            String adjacence = value.toString();
            String[] userFriends = adjacence.split("\t");
            userTxt.set(userFriends[0]);

            if(userFriends.length == 1){ // this means that the line is userID\t which will become [userID]
                // user has not added anyone
                String friendListNull = userFriends[0] + "\t" + "null";
                friendsOfFriend.set(friendListNull);
                // output key = userID, value = userID\tnull to the reducer
                context.write(userTxt, friendsOfFriend);
            } else { // length is greater than 1, which means the user has at least 1 friend
                String[] friends = userFriends[1].split(",");
                String friendList = userFriends[0] + "\t" + userFriends[1];
                friendsOfFriend.set(friendList);
                // for each friend in the list of friends of userID
                // output key=friend, value = userID + \t + friendOfUserID
                for(String friend:friends) {
                    userTxt.set(friend);
                    context.write(userTxt, friendsOfFriend);
                }
            }
        }
    }
    
    
    
    public static class SortFriendsReducer extends Reducer<Text,Text,Text,Text> {

        /*
         * @param key:Text                  this is the userID
         * @param values: Iterable<Text>    this is the list of values with userID being the key
         * @param context: Context          Used in this method to allow the reducer to communicate with the output 
         * 
         * this method receives userID, and all the friends of their friends. For example, suppose
         * 
         * the key 4 will then receive, from the mapper:
         * key: 4       value: 5 TAB 2,4,6
         * key: 4       value: 1 TAB 2,3,4
         * 
         * This method will count 2 twice, meaning that 2 and 4 have two mutual friends. It also makes sure that,
         * The values before the TAB will not be counted in the suggestion, as the user 4 has already added 1 and 5
        */
        public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {

            // this hashset contains all the people that the user has already added
            // for example, 1--2, 1--3 and 2--3, when processing 2 (key = 2) the program will see that 3 is a mutual friend of 2 and 1
            // however, since 2 already added 3, 3 will not be suggested as a potential friend for 2 to add
            HashSet<HashSet<String>> friends = new HashSet<HashSet<String>>();

            // this uses a hashset as a key, the hashset containing set(user, potential suggestedfriend) --> number of mutual friends 
            // it needs to be a hashset since the order does not matter e.g. (1,2) and (2,1) are equivalent
            HashMap<HashSet<String>, Integer> mutualFriendsCount = new HashMap<HashSet<String>, Integer>();

            // this is a hashset with only the user in it
            // the data contained is set("user-number")
            HashSet<String> self = new HashSet<String>();
            String user = key.toString();
            self.add(user);
            friends.add(self);
            
            // debug purpose only
            Text debug;
            // debug purpose only


            for (Text val : values) {
                String[] friendsOfFriend = val.toString().split("\t");
                String[] potentialFriends = friendsOfFriend[1].split(",");
                
                HashSet<String> alreadyAdded = new HashSet<String>(){};
                if(friendsOfFriend[0] != "null"){ // if its not null, the person has at least 1 friend
                    alreadyAdded.add(friendsOfFriend[0]);
                    alreadyAdded.add(user);
                }
                friends.add(alreadyAdded);

                for(String potentialFriend:potentialFriends) {
                    // this is the hashset (userID, potential friend)
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
            // remove everyone the user already added
            for(HashSet<String> friend:friends) {
                mutualFriendsCount.remove(friend);
            }
            
            // a list of all the users that have at least 1 mutual friend
            // Pair(potential friend, number of mutual friends)
            ArrayList<Pair> ranked = new ArrayList<Pair>(mutualFriendsCount.size());
            for(HashSet<String> mutualFriend:mutualFriendsCount.keySet()) {
                Integer count = mutualFriendsCount.get(mutualFriend);
                mutualFriend.remove(user);
                String uid = mutualFriend.toArray()[0].toString();
                ranked.add(new Pair(count, uid));
            }

            // sort by number of mutual friends then by user id
            ranked.sort(new Comparator<Pair>() {
                public int compare(Pair left, Pair right) {
                    Integer nbMutual = right.count - left.count;
                    if(nbMutual != 0) {
                        return nbMutual;
                    } else {
                        return Integer.valueOf(left.uid) - Integer.valueOf(right.uid);
                    }
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
            // they don't have any added
            if(suggested.equals("null")) {
                suggested = "";
            }

            Text suggestedWrittable = new Text();
            suggestedWrittable.set(suggested);
            context.write(new Text(user), new Text(suggested));
        }
    
        
    
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        if (otherArgs.length < 2) {
            System.err.println("Usage: MutualFriends <in> [<in>...] <out>");
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

        String out = otherArgs[otherArgs.length - 1];
        // FileOutputFormat.setOutputPath(job, new Path(otherArgs[otherArgs.length - 1]));
        FileOutputFormat.setOutputPath(job, new Path(out));

        

        

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }

}
