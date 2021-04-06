# redditlog-es
Stream data into Elasticsearch via PRAW.

# Summary

This is a small and ugly Python script that will grab the comment, submission, and moderator streams via PRAW. It then dumps them into an Elasticsearch database. Why? Because Reddit's search function isn't the best, especially when it comes to moderation duties. This makes searching and statistics much easier. 

# Requirements
- A Reddit username, password, client ID, and client secret. The account should have moderator privileges on the subreddit you're stream since it'll need access to the moderator stream.
- The script uses the [PRAW](https://praw.readthedocs.io/en/latest/) and [Elasticsearch](https://elasticsearch-py.readthedocs.io/en/v7.12.0/) Python modules. You'll need them installed for the script to run.
- An Elasticsearch instance. It doesn't matter where it's hosted as long as you can connect to it.

# Elasticsearch Setup
The output is all in JSON. Elasticsearch should be able to index this without any issues. You'll still need to create the index pattern though, but that's only a few clicks. That being said, you'll need to perform one additional step: create a timestamp field. Easy enough with the dev tools in Elasticsearch:

```
PUT _template/redditlog-es
{
   "index_patterns":[
      "redditlog-es-*"
   ],
   "mappings":{
      "properties":{
         "timestamp":{
            "type":"date"
         }
      }
   }
}
```

# Configuration
There isn't much to the script. The configuration options are defined at the beginning and should be self-explanatory. I used [these instructions](https://support.integromat.com/hc/en-us/articles/360007274793-reddit) to create the client ID and secret for authentication.

# Running the Script
Easy!

`python redditlog-es.py`

That's it. There's rudimentary error-checking built in so it'll reconnect when Reddit eventually goes down. I run the script in a tmux session. 
