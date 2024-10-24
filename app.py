import base64
import hashlib
from urllib.parse import urlencode, quote_plus
import json
import os
import threading
from queue import Queue

import requests
from flask import Flask, jsonify, request, redirect, render_template, session, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from redis import Redis
import numpy as np
import re

from langdetect import detect

from api.Automation_Assistant import generate_real_estate_campaign
from api.Automation_Contexts import case_study_training_context_arabic, short_content_context, \
    prompt_generator_english_context, prompt_generator_arabic_context, prompt_enhancer_english_context, \
    prompt_enhancer_arabic_context, image_analyzer_english_context, image_analyzer_arabic_context
from api.Investment_Contexts import investment_arabic_context_residential_building, \
    investment_arabic_context_residential_commercial_building, investment_arabic_context_commercial_building, \
    investment_arabic_context_shopping_mall, investment_arabic_context_villas, investment_arabic_context_villa, \
    investment_arabic_context_residential_compound, investment_arabic_context_administrative_building, \
    investment_arabic_context_hotel, investment_editor_context_ar, investment_arabic_Commercial_residential_tower, investment_arabic_Commercial_and_administrative_tower, investment_arabic_administrative_tower
from api.ideogram_api_requests import generate_image_from_ideogram
from api.openai_api_requests import case_study_ai, social_media_ai, image_creator, prompt_creator, prompt_enhancer, \
    image_analyzer, investment_generator, investment_image_creator, pdf_extractor, short_content_generator, \
    investment_editor, \
    investment_selector, Unreal_Engine_Chat

app = Flask(__name__)
CORS(app)



# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SESSION_KEY_PREFIX'] = 'session:'
# app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379)

# Initialize the session
# Session(app)

socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = 'sadsakdjaslkdjwkqjeqe02=wd22@'

app.config.update(
    SESSION_COOKIE_SECURE=True,  # Set to True if you're using HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevents JavaScript access to cookies
    SESSION_COOKIE_SAMESITE='None'  # Adjust depending on your use case (could be 'None' if cross-origin)
)

task_queue = Queue()
max_concurrent_tasks = 5  # Limit the number of concurrent tasks
semaphore = threading.Semaphore(max_concurrent_tasks)  # Semaphore to control concurrency

def worker():
    while True:
        semaphore.acquire()  # Acquire a semaphore slot
        task = task_queue.get()
        try:
            investment_image_creator(task)
        finally:
            task_queue.task_done()
            semaphore.release()  # Release the semaphore slot when done

# Start worker threads
for _ in range(max_concurrent_tasks):  # Create as many workers as the concurrency limit
    threading.Thread(target=worker, daemon=True).start()











context = []


@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

""" PDF Extractor Endpoint """

@app.route('/ar/pdf-data-extractor', methods=['POST'])
def chat():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'images' not in data:
        return jsonify({"error": "Missing 'images' field"}), 400

    images = data['images']

    # clears the context for a new run
    context.clear()

    # Add user message to context
    context.append({"role": "system", "content": """you will be provided some images and you have to understand it and reply with the data you understood from these images.
                                                    Your response must be in Arabic.
                                                    Guidance:
                                                        -If there are some floor plans then each one is a separate Asset.
                                                        -You have to focus on the number of rooms, number of bathrooms, number of living rooms, you have to get them as they are the heighest periority.
                                                        -Asset_Type Must be in English only and select it from one of these:
                                                                [ Apartment, Villa ]
                                                                
                                                                
                                                    your response should only be in json format and look like this: 
                                                    {
                                                        "Title":"Project title here",
                                                        "Description":"make a full Description here to provide all the details about the location",
                                                        "District":"the district of the project if provided, if not then type 0",
                                                        "City":"the city of the project if provided, if not then type 0",
                                                        "Country":"the country of the project if provided, if not then type 0",
                                                        "Land_Area":"Land Area here if provided, if not then type 0",
                                                        "Project_Assets":[
                                                                            {
                                                                                "Asset_Type":"Write the type of the asset here please",
                                                                                "Title":"Write the title of the asset here like the class of the asset",
                                                                                "No_Of_Units":"search the images for the number of units if it was provided, if not then write 0",
                                                                                "Space":"search the images for the asset Area ( only a number without a unit )",
                                                                                "Finishing":"search the images for the finishing of the asset if provided, if not then type 0",
                                                                                "Floors":"search the images for the number of floors of the assets if it is a duplex or has many floors, if not then type 1",
                                                                                "Rooms": "search the images for the total number of rooms",
                                                                                "Bathrooms" : "search the images for the total number of bathrooms",
                                                                                "Livingrooms":"search the images for the total number of living rooms"
                                                                            },
                                                                            ...
                                                                        ],
                                                    }
        """})

    # Call the chat_with_ai function from the imported module
    try:
        response, parsed_ai_response, new_context = pdf_extractor(images, context)
        print("new context: ", new_context)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


""" Automation Endpoints """
@app.route('/shortcontent', methods=['POST'])
def short_content():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']

    # clears the context for a new run
    context.clear()

    # Add user message to context
    context.append({"role": "system", "content": short_content_context})

    # Call the chat_with_ai function from the imported module
    try:
        response, parsed_ai_response, new_context = short_content_generator(user_input, context)
        print("new context: ")
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/en/chat/casestudy', methods=['POST'])
def case_study_chat_en():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']

    # clears the context for a new run
    context.clear()

    # Add user message to context
    context.append({"role": "system", "content": case_study_training_context_arabic})

    # Call the chat_with_ai function from the imported module
    try:
        response, parsed_ai_response, new_context = case_study_ai(user_input, context)
        print("new context: ")
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/chat/casestudy', methods=['POST'])
def case_study_chat_ar():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']

    # clears the context for a new run
    context.clear()

    # Add user message to context
    context.append({"role": "system", "content": case_study_training_context_arabic})

    # Call the chat_with_ai function from the imported module
    try:
        response, parsed_ai_response, new_context = case_study_ai(user_input, context)

        try:
            target_audience_response = generate_real_estate_campaign(user_input)

            parsed_ai_response["Target_Audience"] = target_audience_response["Target_Audience"]
            parsed_ai_response["Market_Strategy"] = target_audience_response["Market_Strategy"]
            parsed_ai_response["Performance_Metrics"] = target_audience_response["Performance_Metrics"]
            parsed_ai_response["ROI_Calculation"] = target_audience_response["ROI_Calculation"]
            parsed_ai_response["Strategic_Insights"] = target_audience_response["Strategic_Insights"]
            parsed_ai_response["Recommendations"] = target_audience_response["Recommendations"]
            parsed_ai_response["Post_Frequency"] = target_audience_response["Post_Frequency"]

            response = json.dumps(parsed_ai_response)

            print(response)

        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500

        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/en/chat/socialmediaplan', methods=['POST'])
def social_media_chat_en():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    history = data['history']
    previousPrompt = data['previousPrompt']

    # clears the context for a new run
    context.clear()
    context.append({"role": "system", "content": case_study_training_context_arabic})
    context.append({"role": "user", "content": previousPrompt})
    context.append({"role": "assistant", "content": history})


    # Call the chat_with_ai function from the imported module
    try:
        response, parsed_ai_response, new_context = social_media_ai(user_input, context)
        print("new context: ")
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/chat/socialmediaplan', methods=['POST'])
def social_media_chat_ar():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    print(request)
    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    history = data['history']
    previousPrompt = data['previousPrompt']

    # clears the context for a new run
    context.clear()
    context.append({"role": "system", "content": case_study_training_context_arabic})
    context.append({"role": "user", "content": previousPrompt})
    context.append({"role": "assistant", "content": history})


    # Call the chat_with_ai function from the imported module
    try:
        response, parsed_ai_response, new_context = social_media_ai(user_input, context)
        print("new context: ")
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/image', methods=['POST'])
def image_generator():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    try:
        image_url = image_creator(user_input)
        return jsonify({"url": image_url}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/image2', methods=['POST'])
def investment_image_generator():
    data = request.get_json()
    prompt = data.get('input')
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Start the image generation in a new thread
    result_holder = []
    thread = threading.Thread(target=lambda: result_holder.append(investment_image_creator(prompt)))
    thread.start()
    thread.join()  # Wait for the thread to finish

    image_url = result_holder[0]
    if image_url.startswith("Error"):
        return jsonify({"error": image_url}), 500
    else:
        return jsonify({"image_url": image_url}), 200

@app.route('/image-model-2', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt')

    # Call the separate function
    result = generate_image_from_ideogram(prompt)

    if result:
        return jsonify({"data": result}), 200
    else:
        return jsonify({"error": "Error generating image"}), 500


@app.route('/en/prompt-generator', methods=['POST'])
def prompt_generator_en():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    print(request)

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)
    try:
        image_prompt = prompt_creator(user_input, prompt_generator_english_context)
        return image_prompt, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/prompt-generator', methods=['POST'])
def prompt_generator_ar():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)
    try:
        image_prompt = prompt_creator(user_input, prompt_generator_arabic_context)
        return image_prompt, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/en/prompt-enhancer', methods=['POST'])
def prompt_enhancement_en():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)

    try:
        image_prompt = prompt_enhancer(user_input, prompt_enhancer_english_context)
        return image_prompt, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/prompt-enhancer', methods=['POST'])
def prompt_enhancement_ar():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)

    try:
        image_prompt = prompt_enhancer(user_input, prompt_enhancer_arabic_context)
        return image_prompt, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/en/image-analyzer', methods=['POST'])
def image_analysis_en():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)

    try:
        image_prompt = image_analyzer(user_input, image_analyzer_english_context)
        return image_prompt, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/image-analyzer', methods=['POST'])
def image_analysis_ar():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)

    try:
        image_prompt = image_analyzer(user_input, image_analyzer_arabic_context)
        return image_prompt, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500



""" Investment Endpoints """
@app.route('/investment/image-analyzer', methods=['POST'])
def investment_image_analysis():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)

    try:
        image_prompt = image_analyzer(user_input, image_analyzer_arabic_context)
        return image_prompt, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/en/investment', methods=['POST'])
def ai_investment_en():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                            you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                            your response should be in JSON format and look like this: 
                            {
                                "flag": "True (if it is for a main street) or False (otherwise)
                            }
                            
                            your response should be True or False only. 
                            You should analyze all the images carefully and understand them correctly and then respond.
    
                            """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_residential_building)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment', methods=['POST'])
def ai_investment_ar():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                your response should be in JSON format and look like this: 
                                {
                                    "flag": "True (if it is for a main street) or False (otherwise)
                                }

                                your response should be True or False only. 
                                You should analyze all the images carefully and understand them correctly and then respond.

                                """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_residential_building)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-residential-building', methods=['POST'])
def ai_investment_ar_residential_building():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_residential_building)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-residential-commercial-building', methods=['POST'])
def ai_investment_ar_residential_commercial_building():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 2, and convert back to string
        price = str(float(price) * 2)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_residential_commercial_building)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-commercial-building', methods=['POST'])
def ai_investment_ar_commercial_building():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_commercial_building)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-shopping-mall', methods=['POST'])
def ai_investment_ar_shopping_mall():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_shopping_mall)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-villas', methods=['POST'])
def ai_investment_ar_villas():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_villas)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-villa', methods=['POST'])
def ai_investment_ar_villa():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_villa)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-residential-compound', methods=['POST'])
def ai_investment_ar_residential_compound():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_residential_compound)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-administrative-building', methods=['POST'])
def ai_investment_ar_administrative_building():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_administrative_building)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-hotel', methods=['POST'])
def ai_investment_ar_hotel():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_context_hotel)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-selector', methods=['POST'])
def ai_investment_ar_selector():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)

    # Dictionary to map keys to their corresponding functions
    ai_investment_contexts = {
        "مبنى_سكني": investment_arabic_context_residential_building,
        "مبنى_تجاري": investment_arabic_context_commercial_building,
        "مبنى_تجاري_سكني": investment_arabic_context_residential_commercial_building,
        "مول_تجاري": investment_arabic_context_shopping_mall,
        "كومباوند_فلل": investment_arabic_context_villas,
        "فيلا": investment_arabic_context_villa,
        "كومباوند_سكني": investment_arabic_context_residential_compound,
        "مبنى_إداري": investment_arabic_context_administrative_building,
        "فندق": investment_arabic_context_hotel,
        "برج_تجاري_سكني" : investment_arabic_Commercial_residential_tower,
        "برج_تجاري_إداري" : investment_arabic_Commercial_and_administrative_tower,
        "برج_إداري" : investment_arabic_administrative_tower
    }

    try:
        selector_response = investment_selector(user_input)
        Json_Data = json.loads(selector_response)
        for key, value in Json_Data.items():
            if value == "True":
                investment_response = investment_generator(user_input, ai_investment_contexts[key])
                return investment_response, 200


    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/ar/investment-editor', methods=['POST'])
def investment_editor_ar():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    history = data['history']

    # Convert the 'history' dictionary to a string
    history_str = json.dumps(history, ensure_ascii=False, indent=4)  # Convert to a formatted string
    user_input_str = json.dumps(user_input, ensure_ascii=False, indent=4)  # Convert to a formatted string

    # Add history_str and user_input with a blank line between them
    input = "الدراسة السابقة: " + history_str + "\n\n" + "لقد قمت بهذا التعديل: " + user_input_str + "أريدك أن تقوم بتطبيق هذا التعديل في الدراسة التي ارفقتها في الأعلى"

    print(input)

    # clears the context for a new run
    context.clear()
    context.append({"role": "system", "content": investment_editor_context_ar})


    # Call the chat_with_ai function from the imported module
    try:
        response, parsed_ai_response, new_context = investment_editor(input, context)
        print("new context: ")
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/ar/investment_Commercial_residential_tower', methods=['POST'])
def ai_investment_Commercial_residential_tower():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_Commercial_residential_tower)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    


@app.route('/ar/investment_Commercial_and_administrative_tower', methods=['POST'])
def ai_investment_Commercial_administrative_tower():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_Commercial_and_administrative_tower)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    

@app.route('/ar/investment_administrative_tower', methods=['POST'])
def ai_investment_administrative_tower():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data or 'price' not in data or 'images' not in data:
        return jsonify({"error": "Missing 'input' or 'price' or 'images' field"}), 400

    user_input = data['input']
    price = data['price']
    images = data['images']

    image_analyzer_context = """
                                    you are a image analyzer, your job is to analyze the image and let us know whether it is on a main street or not.
                                    your response should be in JSON format and look like this: 
                                    {
                                        "flag": "True (if it is for a main street) or False (otherwise)
                                    }

                                    your response should be True or False only. 
                                    You should analyze all the images carefully and understand them correctly and then respond.

                                    """

    analyzer_response = image_analyzer(images, image_analyzer_context)

    # Parse analyzer_response as JSON (if it is not already a dictionary)
    try:
        analyzer_response = json.loads(analyzer_response)  # Convert string response to JSON if necessary
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse analyzer response: {str(e)}"}), 500

    # Check if 'flag' is present and True
    if analyzer_response['flag'] == 'True':
        # Convert price to float, multiply by 1.5, and convert back to string
        price = str(float(price) * 1.5)

    if float(price) > 0:
        user_input += f", and the land price for sqm is {price}."

    try:
        response = investment_generator(user_input, investment_arabic_administrative_tower)
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

"""  Unreal Engine Endpoints  """
@app.route('/unreal-engine-chat-v1', methods=['POST'])
def unreal_engine_chat_v1():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' field"}), 400

    # Check if 'input' key exists in the JSON data
    if 'reference' not in data:
        return jsonify({"error": "Missing 'reference' field"}), 400

    prompt = data['prompt']
    reference = data['reference']

    unreal_engine_context = f"""scrape the reference below to respond the user prompts. 
                                you must scrape the reference website and respond based on the data of this website
                                reference: {reference}.
                                your response should be in JSON format only and should look like this: 
                                
                                    "text":"your response here"
                                
                                you must use the same language as the user.
                            """

    # clears the context for a new run
    context.clear()
    context.append({"role": "system", "content": unreal_engine_context})

    # Call the chat_with_ai function from the imported module
    try:
        response, parsed_ai_response, new_context = Unreal_Engine_Chat(prompt, context)
        print("new context: ")
        return response, 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500




""" Publishing Endpoints """

# Domain
Domain_Origin = os.getenv('DOMAIN_ORIGIN')

#Twitter
CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')
REDIRECT_URI = 'https://coral-app-8z265.ondigitalocean.app' + '/twitter-callback'

def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8').replace('=', '')

def generate_code_challenge(verifier):
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('utf-8')).digest()).decode('utf-8').replace('=', '')

@app.route('/twitter-login')
def twitter_login():
    code_verifier = generate_code_verifier()
    session['code_verifier'] = code_verifier
    code_challenge = generate_code_challenge(code_verifier)
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').replace('=', '')
    session['state'] = state
    print(f"Session data after setting state: {session}")
    print('state: ', state)
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'tweet.read tweet.write users.read offline.access',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    url = f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
    return redirect(url)


@app.route('/twitter-callback')
def twitter_callback():
    print(f"Session data in callback: {session}")
    code = request.args.get('code')
    returned_state = request.args.get('state')
    current_state = session.pop('state', None)
    print('returned state: ', returned_state)
    print('current state: ', current_state)

    # Check state
    if returned_state != current_state:
        return jsonify(error="State mismatch"), 400

    headers = {
        'Authorization': f'Basic {base64.urlsafe_b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': session.pop('code_verifier', None)
    }

    # Make a POST request to get the access token
    response = requests.post("https://api.twitter.com/2/oauth2/token", headers=headers, data=urlencode(data))

    if response.status_code != 200:
        return jsonify(error="Failed to retrieve access token", details=response.json()), 400

    print(response.json())

    access_token = response.json().get('access_token')
    refresh_token = response.json().get('refresh_token')

    print(f"access token: {access_token}")

    print(f"Domain Origin: {os.getenv('DOMAIN_ORIGIN')}")

    # Ensure the correct origin is used in the postMessage
    return f"""
    <script>
      window.opener.postMessage(
        {{ type: 'TWITTER_AUTH_SUCCESS', accessToken: '{access_token}', refreshToken: '{refresh_token}'}},
        '{os.getenv('DOMAIN_ORIGIN')}'
      );
      window.close();
    </script>
    """


@app.route('/post-tweet', methods=['POST'])  # Ensure the method is POST
def post_tweet():

    data = request.get_json()  # Get the JSON data
    tweet_text = data.get('text')  # Extract the tweet text

    access_token = data.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is missing"}), 401

    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    # Validate tweet text
    if not tweet_text:
        return jsonify({"error": "No tweet text provided"}), 400

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {'text': tweet_text}  # Use the text from the request
    response = requests.post("https://api.x.com/2/tweets", headers=headers, json=payload)

    if response.status_code != 201:
        return jsonify({"error": "Failed to post tweet", "details": response.json()}), response.status_code
    return jsonify(response.json()), 200

@app.route('/fetch-and-delete-first-tweet')
def fetch_and_delete_first_tweet():
    access_token = session.get('access_token')
    user_id = session.get('user_id')
    if not access_token:
        return jsonify({"error": "Access token is missing"}), 401
    tweets = fetch_tweets(access_token, user_id, max_results=5)
    if tweets and len(tweets) > 0:
        first_tweet_id = tweets[0]['id']  # Get the ID of the first tweet
        if delete_tweet(first_tweet_id, access_token):
            return jsonify({'success': True, 'message': 'First tweet deleted successfully.'}), 200
        else:
            return jsonify({'success': False, 'error': 'Failed to delete tweet.'}), 400
    else:
        return jsonify({'success': False, 'error': 'No tweets found or failed to fetch tweets.'}), 404

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


def delete_tweet(tweet_id, access_token):
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.delete(url, headers=headers)
    return response.status_code == 200


#linked in

# Constants
linkedIn_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
linkedIn_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
linkedIn_REDIRECT_URI =  'https://coral-app-8z265.ondigitalocean.app' + '/linkedin-callback'

@app.route('/linkedin-login')
def linkedin_login():
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').replace('=', '')
    session['linkedin-state'] = state
    linkedin_auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={linkedIn_CLIENT_ID}"
        f"&redirect_uri={linkedIn_REDIRECT_URI}"
        f"&state={state}"
        "&scope=profile%20email%20openid%20w_member_social"
    )
    return redirect(linkedin_auth_url)

@app.route('/linkedin-callback')
def linkedin_callback():
    error = request.args.get('error')
    if error:
        error_description = request.args.get('error_description')
        return jsonify({'error': error, 'description': error_description}), 400

    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Authorization code not found'}), 400

    returned_state = request.args.get('state')
    if returned_state != session.pop('linkedin-state', None):
        return jsonify(error="Unauthorized"), 401

    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': linkedIn_REDIRECT_URI,
        'client_id': linkedIn_CLIENT_ID,
        'client_secret': linkedIn_CLIENT_SECRET
    }
    token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')
        session['linkedin_access_token'] = access_token

        # Optionally, fetch user's URN or profile data
        try:
            # Fetch and store the user's URN
            profile_url = 'https://api.linkedin.com/v2/userinfo'
            profile_headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = requests.get(profile_url, headers=profile_headers)
            profile_response.raise_for_status()
            session['linkedin_urn'] = profile_response.json().get('sub')
            linkedin_urn = session['linkedin_urn']

            # JavaScript snippet to send the token back to the parent window
            return f"""
            <script>
                window.opener.postMessage(
                    {{ type: 'LINKEDIN_AUTH_SUCCESS', accessToken: '{access_token}', urn: '{linkedin_urn}' }},
                    '{os.getenv('DOMAIN_ORIGIN')}'
                );
                window.close();
            </script>
            """
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e), 'details': 'Failed to get user profile'}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e), 'details': 'Failed to get access token'}), 400

@app.route('/linkedin-post', methods=['POST'])
def post():

    data = request.get_json()  # Get the JSON data
    post_text = data.get('text')
    access_token = data.get('access_token')
    user_urn = data.get('urn')

    if not access_token:
        return redirect(url_for('linkedin-login'))
    post_url = 'https://api.linkedin.com/v2/ugcPosts'
    post_headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    post_data = {
        "author": f"urn:li:person:{user_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    try:
        response = requests.post(post_url, headers=post_headers, json=post_data)
        response.raise_for_status()
        return 'Posted to LinkedIn!'
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 400



if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
