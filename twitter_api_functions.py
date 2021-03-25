import tweepy
from datetime import date, datetime, timedelta
import json
import os
import mark_functions
import tess_scraper_functions
import email_functions
from tess_scraper_functions import days_ago


consumer_key = '***'
consumer_secret = '***'
access_token = '***'
access_token_secret = '***'


def OAuth():
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            return auth
        except Exception as e:
            return None

oauth = OAuth()
api = tweepy.API(oauth)

def post_tweet(tweet_content):

    oauth = OAuth()
    api = tweepy.API(oauth)

    api.update_status(tweet_content)

    return None

def tweet_json(tweet_dictionary):

    search_date, file_date = email_functions.get_date()

    #create file name
    path = os.getcwd()
    tweet_file = "Tweet Tess (" + file_date + ").json"

    tweet_filename = os.path.join(path, tweet_file)

    with open (tweet_filename, "w") as f:
        json.dump(tweet_dictionary, f, indent=2)

    return tweet_filename, tweet_dictionary

def tweet_dictionary(tweet_dict):

    file_path, tweet_dictionary = tweet_json(tweet_dict)

    dict_len = len(tweet_dict) #Number of entries in the tweet_dictionary

    #for keys in tweet_dict:

    ## NEEd to work on this function. WIll implement to run through a list of tweets and schedule out each one to be tweeted through the following days between 9am and 9pm
    return None

#Create json files

#populate json file

#schedule?
