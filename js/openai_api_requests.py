import json

from openai import OpenAI
import numpy as np
import re
from langdetect import detect
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

# Function to add a new message and get response from the model
first_headers = ['Case Study', 'Target Audience', 'Pros', 'Cons', 'Facebook Hashtags', 'Instagram Hashtags',
                'Twitter Hashtags', 'LinkedIn Hashtags']
second_headers = ['Posts']


def case_study_ai(user_input, context):
    # Append the user input to the context
    prompt = {
        "role": "user",
        "content": user_input,
        "instruction": "Respond in JSON format with the following fields: Case Study, Target Audience, Pros, Cons, and relevant Hashtags."
    }
    context.append(prompt)
    full_response = ''
    parsed_ai_response = ''
    # Call the API without streaming
    try:
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.1,
            response_format={"type":"json_object"},
            max_tokens=16384
        )

        # Fetching the response assuming it is structured as instructed
        full_response = chat_completion.choices[0].message.content
        print("Raw AI response:", full_response)

        # Attempt to parse the response to ensure it is valid JSON
        parsed_ai_response = json.loads(full_response)
        print("Parsed AI response:", parsed_ai_response)

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return full_response, parsed_ai_response, context


def social_media_ai(user_input, context):
    # Append the user input to the context
    context.append({"role": "user", "content": user_input})
    full_response = ''
    parsed_ai_response = ''
    # Call the API without streaming
    try:
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.1,
            response_format={"type":"json_object"},
            max_tokens=16384
        )
        # Fetching the response assuming it is structured as instructed
        full_response = chat_completion.choices[0].message.content
        print("Raw AI response:", full_response)

        # Attempt to parse the response to ensure it is valid JSON
        parsed_ai_response = json.loads(full_response)
        print("Parsed AI response:", parsed_ai_response)

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return full_response, parsed_ai_response, context


