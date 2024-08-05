import tweepy
#
api_key="8V3GO8ynqozUnSHWWX5DE1v7E"
api_secret="rRBeoAUORUoENhlPnVTKsmD9lmThqtMhXA0wAYZmbrjk4WL0cI"
bearer_token=r"AAAAAAAAAAAAAAAAAAAAAGnzuwEAAAAAfdHTN2SWofZ2Vp7tE5ik88t99lk%3DrzhLBaEwg2Vlnk8tMSHhWfxwlWm5tQaOK7CDYk7OLwDrVIAx1i"
access_token="1745358503772909568-sYExxeiQzRICHTIigUXwYe3tBd5Izv"
access_token_secret="JxYLeSNT8mgJBAxFfFsjNEewogCahQ7Q6WzF4o1e8idru"
#
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret, )
#
# #auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
# auth = tweepy.OAuth2AppHandler(consumer_key=api_key, consumer_secret=api_secret)
# api = tweepy.API(auth)
#
# # Posting a tweet
# try:
#     response = client.create_tweet(text="Hello Twitter\nThis is the first tweet!")
#     tweet_id = response.data['id']
#     tweet_text = response.data['text']
#     print(f"Tweet ID: {tweet_id}")
#     print(f"Tweet Text: {tweet_text}")
#
#     client.delete_tweet(tweet_id)
#
#     #client.create_tweet(in_reply_to_tweet_id=tweet_id, text="this is a reply to the tweet!")
#
#     # for tweet in api.home_timeline():
#     #     print(tweet.text)
#
# except Exception as e:
#     print(f"Error posting tweet: {e}")
#
# OAuth2_for_twitter = "https://twitter.com/i/oauth2/authorize?response_type=code&client_id=M1M5R3BMVy13QmpScXkzTUt5OE46MTpjaQ&redirect_uri=https://www.example.com&scope=tweet.read%20users.read%20follows.read%20follows.write&state=state&code_challenge=challenge&code_challenge_method=plain"
#

import tweepy

bearer_token="AAAAAAAAAAAAAAAAAAAAAL8avAEAAAAA0mf6AGTdnI5JTeQNqF8tXEfOhEg%3DVcMSFaagfaPZpQsNlWDbAvLsoGCCmcvZOR8MpxQG1hMx4Mc04h"

def getUserFromTwitter(client, username):
    response = client.get_user(username=username)
    print(type(response.data))


client = tweepy.Client(bearer_token=bearer_token)

user = getUserFromTwitter(client, "KeepGoing743679")

print(user)
