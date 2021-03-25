import tess_scraper_functions
import email_functions
import twitter_api_functions

def trademark_watcher():

    tweet_dict, full_list = tess_scraper_functions.run_tess_search()

    email_functions.send_email(full_list)
    twitter_api_functions.tweet_json(tweet_dict)

    return print("All done")
