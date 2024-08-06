import json

from flask import Flask, jsonify, request, redirect, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import numpy as np
import re

from langdetect import detect

from scripts.openai_api_requests import case_study_ai, social_media_ai

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize a Context to train GPT-4 on
case_study_training_context_english = """
                                You are a real estate marketing consultant. 
                                You are programmed to give a full complete case study ( must be a professional one ), 
                                Target audience ( you must target the age... etc ), Strength and Weakness Points, 
                                and you must generate 10 Hashtags for each Platform that the user provide. 
                                The Hashtags must be exactly 10, and they must be separated by space. 
                                Tha Hashtags must be the top trendy. 
                                You have to focus on what you do, provide the user with all the details. 
                                Your response must be in json format and should look like this: 
                                {
                                "Case_Study": "your response here", 
                                "Target_Audience": "your response here", 
                                "Pros": "your response here", 
                                "Cons": "your response here", 
                                "Facebook_Hashtags": "only if provided from the user", 
                                "Instagram_Hashtags": "only if provided from the user", 
                                "Twitter_Hashtags": "only if provided from the user", 
                                "LinkedIn_Hashtags": "only if provided from the user", 
                                }
                                Don't talk with the user about anything other than this.
                                Don't suggest anything and Don't talk freely, only provide these data.
                                You have to follow the json format only as the example above. 
                               
                                If the customer asks to generate a social media content plan for a period of time then you are a real estate marketing consultant specialized in creating digital content for social media platforms. You are programmed to generate a comprehensive collection of social media posts in a strictly structured JSON format. The posts must be relevant, targeted, and adapted to specific platforms as requested by the user. Here is what you must include:

                                - You must Generate the exact number of posts that the user requests.
                                - Each post must be tailored to the specific platform it is intended for.
                                - The format of your response must strictly follow JSON structure. Each piece of data, including platform names and post content, must be encapsulated in double quotes.
                                - All posts must contain hashtags and emojis related to the targeted platform.
                                
                                Your response must be structured as follows, ensuring each post and all metadata are included within the designated JSON format:
                                
                                {
                                    "Facebook": [
                                        {"Post1": "Content of post 1"},
                                        {"Post2": "Content of post 2"},
                                        {"Post3": "Content of post 3"},
                                        ...
                                        and so on
                                    ],
                                    "Instagram": [
                                        {"Post1": "Content of post 1"},
                                        {"Post2": "Content of post 2"},
                                        {"Post3": "Content of post 3"},
                                        ...
                                        and so on
                                    ],
                                    "Twitter": [
                                        {"Post1": "Content of post 1"},
                                        {"Post2": "Content of post 2"},
                                        {"Post3": "Content of post 3"},
                                        ...
                                        and so on
                                    ],
                                    "LinkedIn": [
                                        {"Post1": "Content of post 1"},
                                        {"Post2": "Content of post 2"},
                                        {"Post3": "Content of post 3"},
                                        ...
                                        and so on
                                    ]
                                }
                                Do not provide empty posts, you must create all the desired number of posts per each platform.
                                You have to create all the posts.
                                Do not deviate from the JSON format. Do not include any additional commentary, hyperlinks, or unrelated content. Each response should focus solely on delivering structured post content as specified. The format must be strictly maintained with all data enclosed in double quotes, adhering to JSON standards.
                                
                                """

# Initialize a Context to train GPT-4 on
case_study_training_context_arabic = """
                               أنت مسشتار تسويق عقاري.
                               العميل سيعطيك تفاصيل حول الشركة المستهدفة او الكومباوند او الوحدات السكنية المستهدفة.
                               يجب عليك عمل دراسة كاملة للمشروع وتقديم نقاط القوة والضعف والعملاء المستهدفين (مع ضذكر الفئة العمرية او الحالة الاجتماعية... الخ ).
                               يجب على الهاشتاجز ان يكونوا 10 هاشتاجز وأن يكونوا اعلى التقييمات على المنصة المستهدفة.
                               جوابك للعميل يجب ان يكون على صيغة json مثل هذا: 
                               {
                               "Case Study": "ردك هنا",
                               "Target Audience": "ردك هنا",
                               "Pros": "ردك هنا",
                               "Cons": "ردك هنا",
                               "Facebook Hashtags": "فقط إذا وفرها المستخدم",
                               "Instagram Hashtags": "فقط إذا وفرها المستخدم",
                               "Twitter Hashtags": "فقط إذا وفرها المستخدم",
                               "LinkedIn Hashtags": "فقط إذا وفرها المستخدم",
                               }
                               لا تتحدث مع المستخدم عن أي شيء آخر غير هذا.
                               """


social_media_plan_training_context = """
                                When the Client asks about the social media marketing plan for a certain period of time,
                                then create the posts' content for the each platform ( 3 posts per week ).
                                Make the posts specific for the targeted platform.
                                your response must be in json format like this: 
                                {
                                "Facebook":{"Post1":"content of post1",
                                            "Post2":"content of post2",
                                            }
                                "Instagram":{"Post1":"content of post1",
                                            "Post2":"content of post2",
                                            }
                                }
                                """

context = []

@app.route('/chat/casestudy', methods=['POST'])
def case_study_chat():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']

    if detect(user_input) == 'ar':
        # clears the context for a new run
        if context.__len__() > 0:
            context.clear()

            # Add user message to context
            context.append({"role": "system", "content": case_study_training_context_arabic})

            # Call the chat_with_ai function from the imported module
            try:
                response, parsed_ai_response, new_context = case_study_ai(user_input, context)
                context.append({"role": "assistant", "content": response})
                print("new context: ")
                return response, 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500

        else:
            # Add user message to context
            context.append({"role": "system", "content": case_study_training_context_arabic})

            # Call the chat_with_ai function from the imported module
            try:
                response, parsed_ai_response, new_context = case_study_ai(user_input, context)
                context.append({"role": "assistant", "content": response})

                print(parsed_ai_response)

                return response, 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500


    else:

        # clears the context for a new run
        if context.__len__() > 0:
            context.clear()

            # Add user message to context
            context.append({"role": "system", "content": case_study_training_context_english})

            # Call the chat_with_ai function from the imported module
            try:
                response, parsed_ai_response, new_context = case_study_ai(user_input, context)
                context.append({"role": "assistant", "content": response})
                print("new context: ")
                return response, 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500

        else:
            # Add user message to context
            context.append({"role": "system", "content": case_study_training_context_english})

            # Call the chat_with_ai function from the imported module
            try:
                response, parsed_ai_response, new_context = case_study_ai(user_input, context)
                context.append({"role": "assistant", "content": response})

                print(parsed_ai_response)

                return response, 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500

@app.route('/chat/socialmediaplan', methods=['POST'])
def social_media_chat():
    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Check if 'input' key exists in the JSON data
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']

    if detect(user_input) == 'ar':
        # clears the context for a new run
        if context.__len__() > 3:
            context.pop()
            context.pop()
            context.pop()

            # Add user message to context
            #context.append({"role": "system", "content": social_media_plan_training_context})

            # Call the chat_with_ai function from the imported module
            try:
                response, parsed_ai_response, new_context = social_media_ai(user_input, context)
                context.append({"role": "assistant", "content": response})
                print("new context: ")
                return response, 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500

        else:
            # Add user message to context
            #context.append({"role": "system", "content": social_media_plan_training_context})

            # Call the chat_with_ai function from the imported module
            try:
                response, parsed_ai_response, new_context = social_media_ai(user_input, context)
                context.append({"role": "assistant", "content": response})

                print(parsed_ai_response)

                return response, 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500
    else:

        # clears the context for a new run
        if context.__len__() > 3:
            context.pop()
            context.pop()
            context.pop()

            # Add user message to context
            # context.append({"role": "system", "content": social_media_plan_training_context})

            # Call the chat_with_ai function from the imported module
            try:
                response, parsed_ai_response, new_context = social_media_ai(user_input, context)
                context.append({"role": "assistant", "content": response})
                print("new context: ")
                return response, 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500

        else:
            # Add user message to context
            # context.append({"role": "system", "content": social_media_plan_training_context})

            # Call the chat_with_ai function from the imported module
            try:
                response, parsed_ai_response, new_context = social_media_ai(user_input, context)
                context.append({"role": "assistant", "content": response})

                print(parsed_ai_response)

                return response, 200
            except Exception as e:
                print(e)
                return jsonify({"error": str(e)}), 500

APP_ID = '882194380611369'

@app.route('/login')
def login():
    # This should direct users to the Facebook login URL
    fb_login_url = f"https://www.facebook.com/v20.0/dialog/oauth?client_id={APP_ID}&redirect_uri=https://ba7a-102-45-247-144.ngrok-free.app/callback&scope=email,public_profile&response_type=code"
    return redirect(fb_login_url)

@app.route('/callback')
def callback():
    # Handle the data returned from Facebook
    code = request.args.get('code')
    if not code:
        return "Error: No code provided", 400
    # Exchange the code for an access token here
    return f"Code received: {code}", 200

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

if __name__ == '__main__':
    app.run(debug=True)
