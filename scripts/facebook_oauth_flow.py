import requests
import webbrowser
from urllib.parse import urlencode

APP_ID = '882194380611369'
APP_SECRET = 'e7af0505e0080e35d58720f18c872909'
REDIRECT_URI = 'https://www.yourwebsite.com/callback'  # This must match the one set in the Facebook App

def get_access_token(code):
    url = f"https://graph.facebook.com/v13.0/oauth/access_token"
    params = {
        'client_id': APP_ID,
        'client_secret': APP_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': code,
    }
    response = requests.get(url, params=params)
    return response.json()['access_token']

def get_user_id(access_token):
    url = f"https://graph.facebook.com/v13.0/me"
    params = {'access_token': access_token}
    response = requests.get(url, params=params)
    return response.json()['id']

def authenticate_user():
    params = {
        'client_id': APP_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'email,public_profile',  # Add other permissions as needed
        'response_type': 'code'
    }
    login_url = f"https://www.facebook.com/v13.0/dialog/oauth?{urlencode(params)}"
    webbrowser.open(login_url)
    print("Please enter the full redirect URL you were redirected to: ")
    redirected_url = input()
    code = redirected_url.split('code=')[1]
    return get_access_token(code)

# Get the access token after user login
access_token = authenticate_user()
user_id = get_user_id(access_token)

print(f"User ID: {user_id}")
# Proceed with fetching page info and posting messages using this access token and user ID
