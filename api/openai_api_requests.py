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
def investment_generator(user_input, sent_context, main_street):
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
            temperature=0.9,
            response_format={"type": "json_object"},
            max_tokens=16384
        )
        response = chat_completion.choices[0].message.content
        prompt = json.loads(response)
        print(prompt)

        prompt['main_street'] = main_street

        response = json.dumps(prompt)

        return response

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)})


# Arabic "why" generator for location analysis
def generate_location_why_ar(property_type: str, facility_counts: dict, is_good: bool) -> str:
    """
    توليد شرح موجز (1-2 جملة) باللغة العربية لسبب صلاحية أو عدم صلاحية الموقع
    """
    # صياغة وصف المرافق
    facilities_descr = ", ".join(f"{k}: {v}" for k, v in facility_counts.items())
    verdict = "مناسب" if is_good else "غير مناسب"
    prompt = (
        f"أنت خبير في تحليل العقارات.\n"
        f"الموقع يحتوي على المرافق التالية: {facilities_descr}.\n"
        f"نوع العقار المحدد هو '{property_type}'، والوضع الحالي: {verdict}.\n"
        f"اكتب شرحًا موجزًا (جملة إلى جملتين) باللغة العربية يوضح لماذا هذا التقييم منطقي."
    )

    messages = [
        {"role": "system", "content": "أنت مساعد تحليل عقاري محترف ومتقن اللغة العربية."},
        {"role": "user", "content": prompt}
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return "تعذّر توليد الشرح."


def group_services(services: list) -> (str, dict):
    """
    Uses OpenAI to group a list of services by their category.name_en.
    Returns (raw_json_str, parsed_dict).
    """
    # build a short JSON payload for the model
    payload = [
        {
            "id": svc.get("id"),
            "name_en": svc.get("name_en"),
            "address": svc.get("address"),
            "category": svc.get("category", {}).get("name_en")
        }
        for svc in services
    ]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that groups services by category."
        },
        {
            "role": "user",
            "content": (
                "Group the following services by their category.  "
                "Return a JSON object where each key is the category name, "
                "and each value is a list of objects with exactly these fields: id, name_en, address.\n\n"
                + json.dumps(payload, ensure_ascii=False, indent=2)
            )
        }
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
            max_tokens=16384
        )
        raw = resp.choices[0].message.content
        parsed = json.loads(raw)
        return raw, parsed
    except Exception as e:
        print(f"[group_services] error: {e}")
        raise



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

def property_type_recommendation(analysis_data):
    """
    تحليل ذكي لتوصية نوع العقار الأمثل بناءً على البيانات الشاملة
    """
    context = []
    context.clear()

    system_prompt = {
        "role": "system",
        "content": """أنت خبير عقاري متخصص في تحليل المواقع وتوصية أفضل أنواع العقارات بناءً على البيانات الشاملة.
        
        تنسيق الرد المطلوب (JSON):
        {
            "recommendedType": "نوع العقار الموصى به (من القائمة أدناه)",
            "confidence": 85,
            "reasoning": "شرح مفصل للأسباب والمنطق وراء التوصية",
            "alternatives": ["بديل 1", "بديل 2", "بديل 3"],
            "marketInsights": "رؤى سوقية وتحليل اقتصادي",
            "zoningAnalysis": "تحليل رخصة الأرض وأهميتها"
        }
        
        مهمتك:
        1. تحليل البيانات المقدمة (الموقع، السكان، المرافق، الطرق، بيانات السوق)
        2. مقارنة نوع العقار الحالي مع التصنيف المطلوب في رخصة الأرض
        3. تقديم توصية ذكية لنوع العقار الأمثل
        4. شرح الأسباب والمنطق وراء التوصية
        
        أنواع العقارات المتاحة:
        - مبنى سكني
        - مبنى تجاري سكني
        - مبنى تجاري إداري
        - مبنى تجاري
        - مول تجاري
        - فلل
        - فيلا
        - مجمع سكني
        - مبنى إداري
        - فندقي
        - برج تجاري سكني
        - برج تجاري إداري
        - برج إداري
        
        يجب أن يكون ردك منظم ومهني باللغة العربية ويحتوي على:
        - نوع العقار الموصى به (يجب أن يكون من الأنواع المذكورة أعلاه بالضبط)
        - مستوى الثقة في التوصية (0-100)
        - شرح مفصل للأسباب
        - بدائل أخرى مناسبة (من الأنواع المذكورة أعلاه)
        - رؤى سوقية
        
        ملاحظات مهمة:
        - استخدم الأسماء العربية بالضبط كما هي مذكورة أعلاه
        - إذا كان التصنيف المطلوب في رخصة الأرض مختلف عن نوع العقار الحالي، اشرح أهمية رخصة الأرض ومدى ملاءمتها للموقع
        - ركز على تحليل الكثافة السكانية والمرافق المتاحة لتحديد أفضل نوع عقار
        - خذ في الاعتبار بيانات السوق والمعاملات الأخيرة في المنطقة
        
        استخدم البيانات التالية في تحليلك:
        - موقع الأرض والإحداثيات
        - التصنيف المطلوب في رخصة الأرض
        - نوع العقار الحالي
        - الكثافة السكانية والتركيبة الديموغرافية
        - المرافق القريبة وتوزيعها
        - شبكة الطرق والاتصال
        - بيانات السوق والمعاملات
        - درجة الملاءمة الحالية"""
    }
    
    context.append(system_prompt)

    # تحضير البيانات للتحليل
    user_prompt = f"""
    قم بتحليل البيانات التالية وتقديم توصية ذكية لنوع العقار الأمثل:
    
    تحليل رخصة الأرض:
    - التصنيف المطلوب في رخصة الأرض: {analysis_data.get('location', {}).get('zoning')}
    - نوع العقار الحالي: {analysis_data.get('location', {}).get('currentPropertyType')}
    
    إذا كان التصنيف المطلوب في رخصة الأرض مختلف عن النوع الحالي، قم بتحليل:
    1. مدى أهمية رخصة الأرض للموقع
    2. لماذا رخصة الأرض أكثر ملاءمة
    3. الفوائد الاقتصادية والاستثمارية لرخصة الأرض
    
    معلومات الموقع والأرض:
    - الإحداثيات: {analysis_data.get('location', {}).get('latitude')}, {analysis_data.get('location', {}).get('longitude')}
    - رقم القطعة: {analysis_data.get('location', {}).get('parcelNumber')}
    - رقم المخطط: {analysis_data.get('location', {}).get('planNumber')}
    - رخصة الأرض: {analysis_data.get('location', {}).get('zoning')}
    - نوع العقار الحالي: {analysis_data.get('location', {}).get('currentPropertyType')}
    
    لوائح البناء:
    - نوع الاستخدام: {analysis_data.get('buildingCode', {}).get('landuse')}
    - الارتفاع: {analysis_data.get('buildingCode', {}).get('height')}
    - نسبة البناء: {analysis_data.get('buildingCode', {}).get('far')}
    
    البيانات الديموغرافية:
    - إجمالي السكان: {analysis_data.get('demographics', {}).get('totalPopulation')}
    - السكان الذكور: {analysis_data.get('demographics', {}).get('malePopulation')}
    - السكان الإناث: {analysis_data.get('demographics', {}).get('femalePopulation')}
    - المساحة بالكيلومتر المربع: {analysis_data.get('demographics', {}).get('areaKm2')}
    
    المرافق القريبة:
    {json.dumps(analysis_data.get('facilities', {}), ensure_ascii=False, indent=2)}
    
    شبكة الطرق:
    {json.dumps(analysis_data.get('roads', []), ensure_ascii=False, indent=2)}
    
    بيانات السوق:
    {json.dumps(analysis_data.get('marketData', {}), ensure_ascii=False, indent=2)}
    
    درجة الملاءمة الحالية: {analysis_data.get('currentScore')}
    
    قم بتحليل هذه البيانات بعمق وقدم توصية شاملة ومبررة.
    """

    prompt = {
        "role": "user",
        "content": user_prompt
    }
    
    context.append(prompt)
    
    full_response = ''
    parsed_ai_response = ''
    
    try:
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=4096
        )

        full_response = chat_completion.choices[0].message.content
        print("Raw AI response:", full_response)

        parsed_ai_response = json.loads(full_response)
        print("Parsed AI response:", parsed_ai_response)

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {str(e)}")
        # إرجاع رد افتراضي في حالة الخطأ
        parsed_ai_response = {
            "recommendedType": "غير محدد",
            "confidence": 0,
            "reasoning": "حدث خطأ في تحليل البيانات",
            "alternatives": [],
            "marketInsights": "تعذر تحليل بيانات السوق",
            "zoningAnalysis": "تعذر تحليل رخصة الأرض"
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        parsed_ai_response = {
            "recommendedType": "غير محدد",
            "confidence": 0,
            "reasoning": "حدث خطأ في تحليل البيانات",
            "alternatives": [],
            "marketInsights": "تعذر تحليل بيانات السوق",
            "zoningAnalysis": "تعذر تحليل رخصة الأرض"
        }

    return full_response, parsed_ai_response, context

def land_best_use_conclusion(analysis_data):
    """
    تحليل احترافي لاختيار أفضل استخدام للأرض وكتابة ملخص نهائي يخدم المطور العقاري.
    """
    context = []
    context.clear()

    system_prompt = {
        "role": "system",
        "content": """
أنت مستشار تطوير عقاري محترف. مهمتك تحليل بيانات الأرض وتقديم توصية نهائية واضحة ومباشرة للمطور العقاري حول أفضل استخدام للأرض، مع ملخص احترافي يساعده في اتخاذ القرار. يجب أن يشمل الملخص:
- أفضل استخدام للأرض (Best Use) بشكل محدد.
- مبررات الاختيار (لماذا هذا النوع هو الأنسب؟).
- تحليل السوق والطلب.
- جدوى اقتصادية مبسطة.
- مخاطر أو تحديات محتملة (إن وجدت).
- توصية تنفيذية مباشرة.

صيغة الرد المطلوبة (JSON):
{
  "best_use": "نص قصير يحدد أفضل استخدام",
  "conclusion": "ملخص نهائي احترافي يخاطب المطور العقاري ويحتوي على جميع النقاط أعلاه"
}
اكتب الملخص بلغة احترافية واضحة ومقنعة.
        """
    }
    context.append(system_prompt)

    user_prompt = f"""
هذه بيانات الأرض:
{json.dumps(analysis_data, ensure_ascii=False, indent=2)}

حلل البيانات وقدم الرد بالصيغة المطلوبة فقط.
    """

    prompt = {
        "role": "user",
        "content": user_prompt
    }
    context.append(prompt)

    full_response = ''
    parsed_ai_response = ''

    try:
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.3,
            response_format={"type": "json_object"},
            max_tokens=1024
        )

        full_response = chat_completion.choices[0].message.content
        parsed_ai_response = json.loads(full_response)

    except json.JSONDecodeError as e:
        parsed_ai_response = {
            "best_use": "غير محدد",
            "conclusion": "حدث خطأ في تحليل البيانات."
        }
    except Exception as e:
        parsed_ai_response = {
            "best_use": "غير محدد",
            "conclusion": f"حدث خطأ: {str(e)}"
        }

    return full_response, parsed_ai_response, context
