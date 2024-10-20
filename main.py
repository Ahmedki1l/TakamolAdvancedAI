import requests

# Example usage
access_token = "AAAAAAAAAAAAAAAAAAAAAL8avAEAAAAAX30xVdTIF5EpsAJsjhEtDOlpfQc%3D6zWGZZTise4yihLkVPK5lgsXnWssQJLREAJjb7Q6zl80K4n0Be"

def get_user_id(access_token, username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data['data']['id']  # The 'id' field contains the user_id
    else:
        print("Failed to fetch user ID:", response.text)
        return None

# Example usage
username = "KeepGoing743679"
user_id = get_user_id(access_token, username)


def fetch_tweets(access_token, user_id, max_results=5):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"  # Correct endpoint to fetch user's tweets
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'max_results': max_results,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print(response.json().get('data', []))
        return response.json().get('data', [])
    else:
        print("Failed to fetch tweets:", response.text)  # Logging the error for debugging
        return None

# Fetch replies (comments) for a specific tweet
def fetch_replies(access_token, tweet_id):
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'query': f'conversation_id:{tweet_id}',  # Find tweets in the same conversation
        'tweet.fields': 'author_id,conversation_id',
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Failed to fetch replies for tweet {tweet_id}:", response.text)
        return None

# Reply to a specific tweet
def reply_to_comment(access_token, comment_id, reply_text):
    url = "https://api.twitter.com/2/tweets"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'in_reply_to_tweet_id': comment_id,
        'text': reply_text
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Replied to comment {comment_id}")
    else:
        print(f"Failed to reply to comment {comment_id}:", response.text)

# Main function to fetch tweets and reply to comments
def fetch_tweets_and_reply(access_token, user_id):
    tweets = fetch_tweets(access_token, user_id)
    if tweets:
        for tweet in tweets:
            tweet_id = tweet['id']
            print(f"Fetching replies for tweet {tweet_id}...")
            replies = fetch_replies(access_token, tweet_id)
            if replies:
                for reply in replies:
                    comment_id = reply['id']
                    print(f"Replying to comment {comment_id}")
                    reply_text = "Thanks for your comment!"
                    reply_to_comment(access_token, comment_id, reply_text)



fetch_tweets_and_reply(access_token, user_id)


