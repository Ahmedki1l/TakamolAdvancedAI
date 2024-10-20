import json

from flask import jsonify
from openai import OpenAI
import numpy as np
import re
from langdetect import detect
import datetime
from dotenv import load_dotenv
import os
from PIL import Image
import io
import base64
import threading

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

# Function to add a new message and get response from the model
first_headers = ['Case Study', 'Target Audience', 'Pros', 'Cons', 'Facebook Hashtags', 'Instagram Hashtags',
                 'Twitter Hashtags', 'LinkedIn Hashtags']
second_headers = ['Posts']


def pdf_extractor(images, context):
    # Append the user input to the context
    prompt = {
        "role": "user",
        "content": [
            {
                "type": "text", "text": "Understand these images and provide me with the details from it."
            },
        ],
    }

    if len(images) > 0:
        if len(images[0]) > 0:
            for image in images:
                prompt["content"].append({
                    "type": "image_url",
                    "image_url": {"url": image}
                })

    context.append(prompt)
    print(context)
    full_response = ''
    parsed_ai_response = ''
    # Call the API without streaming
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=context,
            max_tokens=16384,
            response_format={"type": "json_object"},
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


def short_content_generator(user_input, context):
    # Append the user input to the context
    prompt = {
        "role": "user",
        "content": user_input,
        "instruction": "Respond in JSON format with the following fields: Short, Medium, Long."
    }
    context.append(prompt)
    full_response = ''
    parsed_ai_response = ''
    # Call the API without streaming
    try:
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
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


def investment_editor(user_input, context):
    # Append the user input to the context
    prompt = {
        "role": "user",
        "content": user_input,
    }

    context.append(prompt)
    full_response = ''
    parsed_ai_response = ''
    # Call the API without streaming
    try:
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            max_tokens=16384
        )

        # Fetching the response assuming it is structured as instructed
        print("chat_completion: ", chat_completion)
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

def investment_selector(user_input):
    context = []
    context.clear()

    system = {
        "role":"system",
        "content":"""
                    أنت أداة استكشاف نوع العقار الذي يريده العميل.
                    العميل سوف يرسل لك برومبت مثل هذه:
                    كومباوند عمارات سكنية في حي الياسمين في الرياض.
                    عليك أن تفهم نوع العقار الذي يريده العميل و ردك يجب أن يكون بصيغة JSON كالتالي:
                    {
                        "مبنى_سكني":"False",
                        "مبنى_تجاري":"False",
                        "مبنى_تجاري_سكني":"False",
                        "مول_تجاري":"False",
                        "كومباوند_فلل":"False",
                        "فيلا":"False",
                        "كومباوند_سكني":"True",
                        "مبنى_إداري":"False",
                        "فندق":"False"
                    }
                    إرشادات:
                    الفلل لا تعني فيلا.
                    النوع الصحيح للعقار يجب أن يحمل قيمة True و الباقي يجب أن يحمل قيمة False.
                    يجب أن يكون اختيار واحد فقط هو الذي يحمل قيمة True.
                    يجب أن يكون هناك قيمة واحدة تحمل True.
                    لا يجب أن تكون جميع القيم تحمل قيمة False, عليك أن تفهم ماذا يريد العميل وتقوم بإخبارنا به 
                  """
    }
    context.append(system)

    # Append the user input to the context
    prompt = {
        "role": "user",
        "content": user_input,
        "instruction": "Respond in JSON format with the following fields: Short, Medium, Long."
    }
    context.append(prompt)
    full_response = ''
    parsed_ai_response = ''
    # Call the API without streaming
    try:
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
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

    return full_response

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
            temperature=0.3,
            response_format={"type": "json_object"},
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
            temperature=0.3,
            response_format={"type": "json_object"},
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


def image_creator(prompt):
    try:
        # Generate an image using the DALL-E model from OpenAI
        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            style="vivid",
            n=1,
        )

        image_url = response.data[0].url
        print(image_url)
        return image_url
    except Exception as e:
        print(f"An error occurred while creating an image: {str(e)}")
        return None


# Semaphore to limit to 5 concurrent tasks
semaphore = threading.Semaphore(5)


def investment_image_creator(prompt):
    # Acquire a semaphore slot
    with semaphore:
        try:
            # Generate an image using the DALL-E model from OpenAI
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="hd",
                style="vivid",
                n=1,
            )

            image_url = response.data[0].url
            print(image_url)
            return image_url
        except Exception as e:
            print(f"An error occurred while creating an image: {str(e)}")
            return None


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


image_location = "C:/Users/LapTop/Desktop/Residential-building.webp"


def image_analyzer(images, sent_context):
    try:
        context = [{"role": "system", "content": sent_context},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What are in these images? Is there any difference between them?",
                    },
                    *[
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        } for image_url in images
                    ]
                ]
            }
        ]

        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=300
        )
        response = chat_completion.choices[0].message.content
        prompt = json.loads(response)
        print(prompt)
        return response
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)})


# image_analyzer(base64_image)

# image_variations("use this image as a reference image and apply this prompt: A breathtaking luxurious residential compound, masterfully designed to seamlessly integrate with its meticulously landscaped gardens and parks. The scene is vibrant with lush greenery and an array of colorful flowers, crafting a picturesque and inviting environment. Residents are depicted engaging in leisurely morning walks and serene evening strolls along gracefully winding walking paths. The architecture of the homes exemplifies a harmonious blend of elegance and comfort, fostering a tranquil and welcoming atmosphere. Charming elements such as intricately designed benches, towering trees offering shade, and thoughtfully planned community spaces that promote relaxation and social interaction are included, all illuminated by warm, golden sunlight, enhancing the idyllic setting.")
#
#
# def generate_description(image_path):
#     """Generate a description of the image using Google Cloud Vision API."""
#     client = vision.ImageAnnotatorClient()
#     with io.open(image_path, 'rb') as image_file:
#         content = image_file.read()
#
#     image = vision.Image(content=content)
#     response = client.label_detection(image=image)
#
#     description = ', '.join([label.description for label in response.label_annotations])
#     return description
#
# # Usage
# description = generate_description("C:/Users/LapTop/Desktop/Residential-building.webp")
# print(description)


def prompt_creator(text, sent_context):
    try:
        context = [{"role": "system", "content": sent_context},
                   {"role": "user", "content": text}]
        print(context)
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=16384
        )
        response = chat_completion.choices[0].message.content
        prompt = json.loads(response)
        print(prompt)
        return response
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)})


def prompt_enhancer(text, sent_context):
    try:
        context = [{"role": "system", "content": sent_context},
                   {"role": "user", "content": text}]
        print(context)
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=16384
        )
        response = chat_completion.choices[0].message.content
        prompt = json.loads(response)
        print(prompt)
        return response
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)})


# Investments Website APIs
def investment_generator(user_input, sent_context):
    try:
        context = [
            {
                "role": "system",
                "content": sent_context
            },
            {
                "role": "user",
                "content": user_input
            }
        ]

        print(context)
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=16384
        )
        response = chat_completion.choices[0].message.content
        prompt = json.loads(response)
        print(prompt)
        return response

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)})




# Unreal Engine APIs

def Unreal_Engine_Chat(user_input, context):
    # Append the user input to the context
    prompt = {
        "role": "user",
        "content": user_input,
        "instruction": "Respond in JSON format with the following field: Text"
    }
    context.append(prompt)
    full_response = ''
    parsed_ai_response = ''
    # Call the API without streaming
    try:
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
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
