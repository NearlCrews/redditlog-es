# redditlog-es v1.0

from datetime import datetime, timedelta, date
import time
import praw
from elasticsearch import Elasticsearch

##### Begin configuration values.
# Bot username and password.
configRedditUser = ''
configRedditPass = ''
# Create the secret OATH values. Instructions on Reddit.
configRedditClientId = ''
configRedditClientSecret = ''
# Bot owner. This is typically your username. Don't add the u/ in front of the name.
configBotOwner = ''
# Subreddit to monitor, e.g. Michigan. Please note that the account needs mod permissions for the mod log.
configRedditTargetSubreddit = ''
# Details for Elasticsearch, e.g. 'host.domain.lan' and '9200'. 
configElasticsearchHost = ''
configElasticsearchPort = ''
##### End configuration values. 

print(f'Configuration has been read.\n')

# Create the Reddit object.
reddit = praw.Reddit(
    username=configRedditUser,
    password=configRedditPass,
    client_id=configRedditClientId,
    client_secret=configRedditClientSecret,
    user_agent='RedditToES managed by u/{}'.format(configBotOwner)
)

# Create the streams.
try:
  commentStream = reddit.subreddit(configRedditTargetSubreddit).stream.comments(pause_after=-1)
  modStream = reddit.subreddit(configRedditTargetSubreddit).mod.stream.log(pause_after=-1)
  submissionStream = reddit.subreddit(configRedditTargetSubreddit).stream.submissions(pause_after=-1)
except Exception as error:
  print(error)

print(f'Reddit object and streams have been initialized.\n')

# Enable Elasticsearch
elasticsearchClient = Elasticsearch([{'host':configElasticsearchHost,'port':configElasticsearchPort}])

while True:
  try:
  
  # This block is for dealing with comments.
  
    for comment in commentStream:
      if comment is None:
        break
      try:
        categoryValue = "commentStream"
        eventTime = time.strftime('%A, %Y-%m-%d %l:%M:%S %p', time.localtime(comment.created_utc))
        thisComment = { 
          "category": str(categoryValue),
          "eventTime": str(eventTime),
          "redditUser": str(comment.author),
          "subreddit": str(comment.subreddit_name_prefixed),
          "postTitle": str(comment.link_title),
          "postPermalink": str(comment.link_permalink),
          "redditUserComment": str(comment.body),
          "timestamp": int(comment.created_utc * 1000)
        }
        print("!COMMENT!")
        try:
          print(thisComment)
          elasticsearchIndex = "redditlog-es-" + datetime.now().strftime("%Y.%m.%d")
          elasticsearchInsert = elasticsearchClient.index(index=elasticsearchIndex, body=thisComment)
        except Exception as error:
          print(error)
      except Exception as error:
        print(error)
        continue

  
  # This block is for dealing with mod logs.
  
    for modlog in modStream:
      if modlog is None:
        break
      try:
        categoryValue = "modlogStream"
        eventTime = time.strftime('%A, %Y-%m-%d %l:%M:%S %p', time.localtime(modlog.created_utc))
        thisModEvent = {
          "category": str(categoryValue),
          "modDesc": str(modlog.description),
          "redditUserComment": str(modlog.target_body),
          "eventTime": str(eventTime),
          "subreddit": str(modlog.subreddit_name_prefixed),
          "postTitle": str(modlog.target_title),
          "postPermalink": str(modlog.target_permalink),
          "modDetails": str(modlog.details),
          "modAction": str(modlog.action),
          "redditUser": str(modlog.target_author),
          "redditMod": str(modlog._mod),
          "timestamp": int(modlog.created_utc * 1000)
        }
        print("!MODEVENT!")
        try:
          print(thisModEvent)
          elasticsearchIndex = "redditlog-es-" + datetime.now().strftime("%Y.%m.%d")
          elasticsearchInsert = elasticsearchClient.index(index=elasticsearchIndex, body=thisModEvent)
        except Exception as error:
          print(error)
      except Exception as error:
        print(error)
        continue
  
  # This block is for dealing with submissions.

    for submission in submissionStream:
      if submission is None:
        break
      try:
        categoryValue = "submissionStream"
        eventTime = time.strftime('%A, %Y-%m-%d %l:%M:%S %p', time.localtime(submission.created_utc))
        thisSubmission = {
          "category": str(categoryValue),
          "eventTime": str(eventTime),
          "redditUser": str(submission.author),
          "subreddit": str(submission.subreddit_name_prefixed),
          "submissionTitle": str(submission.title),
          "submissionPermalink": str(submission.permalink),
          "submissionDomain": str(submission.domain),
          "submissionUrl": str(submission.url),
          "timestamp": int(submission.created_utc * 1000)
        }
        print("!SUBMISSION!")
        try:
          print(thisSubmission)
          elasticsearchIndex = "redditlog-es-" + datetime.now().strftime("%Y.%m.%d")
          elasticsearchInsert = elasticsearchClient.index(index=elasticsearchIndex, body=thisSubmission)
        except Exception as error:
          print(error)
      except Exception as error:
        print(error)
        continue

  except Exception as error:
    print(error)
    # Wait a while and try again.
    print("Error in main loop. Will try again in 5 minutes.")
    time.sleep(300)
    try:
      commentStream = reddit.subreddit(configRedditTargetSubreddit).stream.comments(pause_after=-1)
      modStream = reddit.subreddit(configRedditTargetSubreddit).mod.stream.log(pause_after=-1)
      submissionStream = reddit.subreddit(configRedditTargetSubreddit).stream.submissions(pause_after=-1)
    except:
      print("Stream initialization failed.")
    continue
