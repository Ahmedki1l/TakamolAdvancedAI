# import requests
# import json
#
# curl = "https://graph.facebook.com/v20.0/3077951389011407/accounts?access_token=EAAMiWeKt3ykBO3AuvuVGNLSGsGePSizbvJnc6EckJ5YJDjvbNsqOrSyfyijzUBSDt23R0XYHWrByIrcBz4VP3kYtW4NecUGrAsjGcJ2ss4FhBsT5ZAfe7edYZCSdKQmuKU1983LXdzQj8C8heIU2PzMOf9PSgqYPeVZBN5zcG0Ckr7WKWPZACUSa67d3sNRhgGYsWF3wCVMe1ogPgAZDZD"
#
# response = requests.get(curl)
#
# # Parsing the JSON response
# data = json.loads(response.content)
#
# print(response.content)
#
# # Assuming 'data' is always present and contains at least one entry
# # You can extract each header from the first entry in the 'data' list
# access_token = data['data'][0]['access_token']
# category = data['data'][0]['category']
# category_list_id = data['data'][0]['category_list'][0]['id']
# category_list_name = data['data'][0]['category_list'][0]['name']
# name = data['data'][0]['name']
# page_id = data['data'][0]['id']
# tasks = data['data'][0]['tasks']
#
# # Printing variables to verify
# print("Access Token:", access_token)
# print("Category:", category)
# print("Category List ID:", category_list_id)
# print("Category List Name:", category_list_name)
# print("Name:", name)
# print("Page ID:", page_id)
# print("Tasks:", tasks)
#
# # The data you want to post
# payload = {
#     'message': "Hello, this is a post from my script!",  # Your post text
#     'access_token': access_token
# }
#
# # URL to send the POST request to
# url = f"https://graph.facebook.com/{page_id}/feed"
#
# # Sending the POST request
# response = requests.post(url, data=payload)
#
# # Checking the response
# if response.status_code == 200:
#     print("Post was successful!")
#     print(response.json())  # This will show the post ID and other details
# else:
#     print("Failed to post.")
#     print(response.text)  # This will help in debugging if something went wrong

import requests
import json

def get_page_info():
    access_token = "EAAMiWeKt3ykBO3AuvuVGNLSGsGePSizbvJnc6EckJ5YJDjvbNsqOrSyfyijzUBSDt23R0XYHWrByIrcBz4VP3kYtW4NecUGrAsjGcJ2ss4FhBsT5ZAfe7edYZCSdKQmuKU1983LXdzQj8C8heIU2PzMOf9PSgqYPeVZBN5zcG0Ckr7WKWPZACUSa67d3sNRhgGYsWF3wCVMe1ogPgAZDZD"
    url = f"https://graph.facebook.com/v20.0/3077951389011407/accounts?access_token={access_token}"
    response = requests.get(url)
    data = json.loads(response.content)
    return data['data']

def select_page(pages):
    for i, page in enumerate(pages, start=1):
        print(f"{i}. {page['name']} (ID: {page['id']})")
    choice = int(input("Select a page number to post on: ")) - 1
    return pages[choice]

def post_message(page):
    message = input("Enter your message: ")
    payload = {
        'message': message,
        'access_token': page['access_token']
    }
    url = f"https://graph.facebook.com/{page['id']}/feed"
    response = requests.post(url, data=payload)
    return response

# Main Execution
pages = get_page_info()
selected_page = select_page(pages)
response = post_message(selected_page)

# Checking the response
if response.status_code == 200:
    print("Post was successful!")
    print(response.json())  # This will show the post ID and other details
else:
    print("Failed to post.")
    print(response.text)  # This will help in debugging if something went wrong
