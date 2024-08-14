import json

from flask import Flask, jsonify, request, redirect, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import numpy as np
import re

from langdetect import detect

from api.openai_api_requests import case_study_ai, social_media_ai, image_creator, prompt_creator, prompt_enhancer, image_analyzer

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
                                The case study must contain all the details about the location and must be very professional.

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
                                Your response must be in English only
                                """

# Initialize a Context to train GPT-4 on
case_study_training_context_arabic = """
                               أنت مستشار تسويق عقاري. 
                                أنت مبرمج لتقديم دراسة حالة كاملة كاملة (يجب أن تكون دراسة احترافية), 
                                والجمهور المستهدف (يجب أن تستهدف الجمهور المستهدف (يجب أن تستهدف العمر ... إلخ)، ونقاط القوة والضعف, 
                                ويجب عليك إنشاء 10 هاشتاجات لكل منصة يقدمها المستخدم. 
                                يجب أن تكون الهاشتاجات 10 هاشتاجات بالضبط، ويجب أن تكون مفصولة بمسافة. 
                                يجب أن تكون الهاشتاجات هي الأكثر رواجاً. 
                                عليك التركيز على ما تقوم به، وتزويد المستخدم بكل التفاصيل. 
                                يجب أن تكون إجابتك بصيغة json ويجب أن تبدو هكذا: 
                                {
                                "Case_Study": "ردك هنا", 
                                "Target_Audience": "ردك هنا", 
                                "Pros": "ردك هنا", 
                                "Cons": "ردك هنا", 
                                "Facebook_Hashtags": "فقط اذا وفرها العميل", 
                                "Instagram_Hashtags": "فقط اذا وفرها العميل", 
                                "Twitter_Hashtags": "فقط اذا وفرها العميل", 
                                "LinkedIn_Hashtags": "فقط اذا وفرها العميل", 
                                }
                                لا تتحدث مع المستخدم عن أي شيء آخر غير هذا.
                                لا تقترح أي شيء ولا تتحدث بحرية، قدم هذه البيانات فقط.
                                عليك اتباع تنسيق json فقط كما في المثال أعلاه. 
                                دراسة الحالة يجب ان تتضمن كل التفاصيل الخاصة بالمكان ويجب ان تكون احترافية جدا.
                                
                                إذا طلب العميل إنشاء خطة محتوى لوسائل التواصل الاجتماعي لفترة من الزمن، فأنت مستشار تسويق عقاري متخصص في إنشاء محتوى رقمي لمنصات التواصل الاجتماعي. أنت مبرمج لإنشاء مجموعة شاملة من منشورات وسائل التواصل الاجتماعي بتنسيق JSON منظم بدقة. يجب أن تكون المنشورات ذات صلة وموجهة وملائمة لمنصات محددة حسب طلب المستخدم. إليك ما يجب عليك تضمينه:

                                - يجب توليد العدد الدقيق للمنشورات التي يطلبها المستخدم.
                                - يجب أن تكون كل مشاركة مصممة خصيصًا للمنصة المحددة التي تستهدفها.
                                - يجب أن يتبع تنسيق استجابتك بدقة بنية JSON. يجب أن يتم تغليف كل جزء من البيانات، بما في ذلك أسماء المنصات ومحتوى المنشورات، بين علامتي اقتباس.
                                - يجب أن تحتوي جميع المنشورات على الوسوم والرموز التعبيرية المتعلقة بالمنصة المستهدفة.

                                يجب أن يكون ردك منظمًا على النحو التالي، مع التأكد من تضمين كل منشور وجميع البيانات الوصفية ضمن تنسيق JSON المحدد:

                                {
                                    "Facebook": [
                                        {"Post1": "محتوى post 1"},
                                        {"Post2": "محتوى post 2"},
                                        {"Post3": "محتوى post 3"},
                                        ...
                                        and so on
                                    ],
                                    "Instagram": [
                                        {"Post1": "محتوى post 1"},
                                        {"Post2": "محتوى post 2"},
                                        {"Post3": "محتوى post 3"},
                                        ...
                                        and so on
                                    ],
                                    "Twitter": [
                                        {"Post1": "محتوى post 1"},
                                        {"Post2": "محتوى post 2"},
                                        {"Post3": "محتوى post 3"},
                                        ...
                                        and so on
                                    ],
                                    "LinkedIn": [
                                        {"Post1": "محتوى post 1"},
                                        {"Post2": "محتوى post 2"},
                                        {"Post3": "محتوى post 3"},
                                        ...
                                        and so on
                                    ]
                                }
                                
                                لا تقدم منشورات فارغة، يجب عليك إنشاء جميع المنشورات المطلوبة لكل منصة.
                                عليك إنشاء جميع المنشورات.
                                لا تحيد عن تنسيق JSON. لا تقم بتضمين أي تعليقات إضافية أو ارتباطات تشعبية أو محتوى غير ذي صلة. يجب أن تركز كل استجابة فقط على تقديم محتوى منشور منظم كما هو محدد. يجب الحفاظ على التنسيق بدقة مع وضع جميع البيانات داخل علامات اقتباس مزدوجة، مع الالتزام بمعايير JSON.
                                يجب أن يكون ردك باللغة العربية فقط
                               """

prompt_generator_english_context = """you are a image prompt generator, the user will provide a text and you have to generate an image prompt for him professionally.
                                                   your response must be in json format: {"prompt":"your response here"}
                                                   Your response must be in English only
                                                """
prompt_generator_arabic_context = """
                                    أنت مُنشئ موجه صورة، سيقدم المستخدم نصًا وعليك إنشاء موجه صورة له بشكل احترافي.
                                                   يجب أن تكون إجابتك بصيغة json: 
                                                   {"prompt":"ردك هنا"}
                                    يجب أن يكون ردك باللغة العربية فقط
                                """

prompt_enhancer_english_context = """you are a image prompt generator, the user will provide an image prompt and you have to enhance it for him professionally.
                                                   your response must be in json format: {"prompt":"your response here"}
                                                   Your response must be in English only
                                                """

prompt_enhancer_arabic_context = """أنت مُنشئ موجه صور، سيقدم المستخدم موجه صور وعليك تحسينها له بشكل احترافي.
                                                   يجب أن تكون إجابتك بصيغة json:
                                    {"prompt":"ردك هنا"}
                                    يجب أن يكون ردك باللغة العربية فقط
                                        """

image_analyzer_english_context = """you are a image analyzer and prompt generator, the user will provide an image and you have to analyze it and then generate an image prompt for him that will then used to generated an image using the image that usser gave to you as referenece professionally.
                                                    the image must be highest quality and be natural and realistic for ecommerce projects
                                                   your response must be in json format: {"prompt":"your response here"}
                                                   Your response must be in English only
                                                """

image_analyzer_arabic_context = """أنت محلل للصور ومولد موجه للصور، سيقدم المستخدم صورة وعليك تحليلها ثم توليد موجه للصور له والذي سيستخدم بعد ذلك لإنشاء صورة باستخدام الصورة التي قدمها لك المستخدم كمرجع بشكل احترافي.
                                                    يجب أن تكون الصورة بأعلى جودة وأن تكون طبيعية وواقعية لمشاريع التجارة الإلكترونية
                                                   يجب أن تكون إجابتك بصيغة json:
                                    {"prompt":"ردك هنا"}
                                    يجب أن يكون ردك باللغة العربية فقط
                                    """

context = []


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
    context.append({"role": "system", "content": case_study_training_context_english})

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
        print("new context: ")
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
    context.append({"role": "system", "content": case_study_training_context_english})
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


@app.route('/en/prompt-generator', methods=['POST'])
def prompt_generator_en():
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

# APP_ID = '882194380611369'
#
# @app.route('/login')
# def login():
#     # This should direct users to the Facebook login URL
#     fb_login_url = f"https://www.facebook.com/v20.0/dialog/oauth?client_id={APP_ID}&redirect_uri=https://ba7a-102-45-247-144.ngrok-free.app/callback&scope=email,public_profile&response_type=code"
#     return redirect(fb_login_url)
#
# @app.route('/callback')
# def callback():
#     # Handle the data returned from Facebook
#     code = request.args.get('code')
#     if not code:
#         return "Error: No code provided", 400
#     # Exchange the code for an access token here
#     return f"Code received: {code}", 200
#
# @app.route('/privacy-policy')
# def privacy_policy():
#     return render_template('privacy_policy.html')

if __name__ == '__main__':
    app.run(debug=True)
