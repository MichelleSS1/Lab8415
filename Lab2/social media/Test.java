import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

import org.w3c.dom.Text;

public class Test {

    public static class FriendOfFriendsMapper  {
        
        // private final static IntWritable one = new IntWritable(1);
        // private Text userTxt = new Text();
        // private Text friendsOfFriend = new Text();
        
        public void map() throws IOException, InterruptedException {
            // String adjacence = value.toString();
            // String adjacence = Files.readString(Paths.get("soc-LiveJournal1Adj.txt"));
            String adjacence = "Files";
            // adjacence.replace("\r", "");

            String[] userFriends = adjacence.split("\r");
            Map<String, String[]> userToFriendsList = new HashMap<String, String[]>();
            Map<String, String> userToFriendsString = new HashMap<String, String>();

            ArrayList<String> users = new ArrayList<String>();

            for(int i = 0; i < userFriends.length; i++) {
                String[] userAndFriends = userFriends[i].split("\t");
                String[] friends;
                try {
                    friends = userAndFriends[1].split(",");
                } catch (Exception e) {
                    friends = new String[] {};
                }
                users.add(userAndFriends[0]);

                if(userAndFriends.length == 1) {
                    userAndFriends = new String[] {userAndFriends[0], ""};
                }
    
                userToFriendsString.put(userAndFriends[0], userAndFriends[1]);
    
                userToFriendsList.put(userAndFriends[0], friends);
            }
            
            for (String user:users) {
                String[] friends = userToFriendsList.get(user);
                if(user.length() < 2){
                    System.out.println(user);
                }
                for(String friend:friends) {
                    // send to reducer: key = user; value = friends of friend
                    // userTxt.set(user);
                    String toSend = userToFriendsString.get(friend);
                    // toSend += ("\t" + friend);
                    
                    // toSend = users.length;

                    // System.out.println(toSend.substring(toSend.length() - 2, toSend.length() - 2));
                    // System.out.println(toSend.toString() );
                    // System.out.println(friend);
                    // friendsOfFriend.set(toSend);
                    // context.write(userTxt, friendsOfFriend);
                }
            }
            HashSet<String> h = new HashSet<String>();
            h.add("esdfsdf");
            System.out.println(h.toArray()[0].toString());
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
    
    
    public static class SortFriendsReducer {
        // private IntWritable result = new IntWritable();
        // // key = user; values = friend of friends \t 
        // public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
        //     HashSet<HashSet<String>> friends = new HashSet<HashSet<String>>();
        //     HashMap<HashSet<String>, Integer> mutualFriendsCount = new HashMap<HashSet<String>, Integer>();
        //     HashSet<String> self = new HashSet<String>();
        //     String user = key.toString();
        //     self.add(user);
        //     friends.add(self);
        //     String[] mutualFriendList;
        //     Text t = new Text();
        //     t.set("never went here");

 
        //     // for each list of mutual friends
        //     for (Text val : values) {
        //         String[] friendsOfFriend = val.toString().split("\t");
        //         try {
        //             Boolean b = (friendsOfFriend[0] == null);
        //             t.set(val.toString());
        //         } catch(Exception e) {
        //             t.set("friendsOfFriend went wrong");
        //         }
        //         // if the first value is "" (empty string), this person does not have any friends.
        //         if(friendsOfFriend[0] == "") {

        //         } else {
        //             mutualFriendList = friendsOfFriend[0].split(",");
        //             for(String mutualFriend:mutualFriendList) {
        //                 HashSet<String> pair = new HashSet<String>();
        //                 pair.add(user); 
        //                 pair.add(mutualFriend); 
        //                 if(mutualFriendsCount.containsKey(pair)) {
        //                     mutualFriendsCount.put(pair, mutualFriendsCount.get(pair) + 1);

        //                 } else {
        //                     mutualFriendsCount.put(pair, 1);
        //                 }
        //             }
        //         }
        //         // add the friend and user to the set
        //         try {
        //             HashSet<String> friend = new HashSet<String>();
        //             friend.add(user);
        //             friend.add(friendsOfFriend[1]);
        //             friends.add(friend);
        //         } catch(Exception e) {
        //         }
        //     }

        //     for(HashSet friend: friends){
        //         mutualFriendsCount.remove(friend);
        //     }
        //     ArrayList<Pair> friendAndCountedMutualFriends = new ArrayList<Pair>();
        //     for(HashSet<String> usrPair:mutualFriendsCount.keySet()) {
        //         friendAndCountedMutualFriends.add(
        //             new Pair(mutualFriendsCount.get(usrPair), usrPair)
        //         );
        //     }
        //     friendAndCountedMutualFriends.sort(new Comparator<Pair>() {
        //         public int compare(Pair left, Pair right)  {
        //             return right.count - left.count; // The order depends on the direction of sorting.
        //         }
        //     });

        //     context.write(key, t);
        // }
    }

    public static void main(String[] args) throws Exception {
        new Test.FriendOfFriendsMapper().map();
        // Configuration conf = new Configuration();
        // String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        // if (otherArgs.length < 2) {
        //     System.err.println("Usage: wordcount <in> [<in>...] <out>");
        //     System.exit(2);
        // }
        // Job job = Job.getInstance(conf, "MutualFriends");

        // job.setJarByClass(MutualFriends.class);
        // job.setMapperClass(FriendOfFriendsMapper.class);
        // job.setCombinerClass(SortFriendsReducer.class);
        // job.setReducerClass(SortFriendsReducer.class);
        // job.setOutputKeyClass(Text.class);
        // job.setOutputValueClass(Text.class);
        
        // for (int i = 0; i < otherArgs.length - 1; ++i) {
        //     FileInputFormat.addInputPath(job, new Path(otherArgs[i]));
        // }
        // FileOutputFormat.setOutputPath(job, new Path(otherArgs[otherArgs.length - 1]));

        // System.exit(job.waitForCompletion(true) ? 0 : 1);
    }

}
