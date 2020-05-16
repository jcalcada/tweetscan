#!/usr/bin/env python
#
#
# This python script is used to monitor the twittersphere for "keywords".  Once it finds one it will send it to PagerDuty
# There is a known issue that if a tweet contains a quote symbol the program fails so we don't use those tweets
#
# Import the necessary package to process data in JSON format
try:
   import json
   import os
except ImportError:
   import simplejson as json

# Import the tweepy library
import tweepy

# Variables that contains the user credentials to access Twitter API
ACCESS_TOKEN = '1244431100-jbuQjnLE36nZeiBouz7xWitYScAPT6WfAYtB1IE'
ACCESS_SECRET = 'bD450XFbJZSziNv9JnJ4hGrXEWY65DiEsCmeuC7tNaHql'
CONSUMER_KEY = 'DSD6BRyycfGPpsZsrBxkUh22D'
CONSUMER_SECRET = 'RJElwqaR4MtIUbDmwFf538je0isx2OXwCx2rOebZFN7Zc3Gpwb'

# Setup tweepy to authenticate with Twitter credentials:

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

global count
count = 0

# Create the api to connect to twitter with your creadentials
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True,compression=True)
print("Authenticated into the twitterver as:"+api.me().name)

class StreamListener(tweepy.StreamListener):
   def on_status(self, status):
     global count
     if '"' in status.text:
        print("Skipping due to quotes:"+status.text)
     else:
        args="\"New PD Tweet: "+status.text.encode('utf-8')+"\""   
        if 0==os.system('pd-send -k 773a1b9a2a8f4b2a8cd57e7dd92f7f59 -t trigger -d \""' + args + '\"" 1>/dev/null'):    
           count += 1
           print("Total Processed: ", count)
        else:
           print("Ooops - a problem occurred: "+args)
           return False

   def on_error(self, status_code):
       if status_code == 420:
           print("status code 420 means this failed")
           return False

stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=["pagerduty"],languages=["en"])
