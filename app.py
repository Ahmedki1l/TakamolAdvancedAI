import base64
import hashlib
from urllib.parse import urlencode, quote_plus
import json
import os
import threading
from queue import Queue

import requests
from flask import Flask, jsonify, request, redirect, render_template, session, url_for
from flask_session import Session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from redis import Redis
import numpy as np
import re

from langdetect import detect

from api.openai_api_requests import case_study_ai, social_media_ai, image_creator, prompt_creator, prompt_enhancer, \
    image_analyzer, investment_generator, investment_image_creator, pdf_extractor, short_content_generator, investment_editor

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

# Initialize a Context to train GPT-4 on
case_study_training_context_english = """
                                You are a real estate marketing consultant. 
                                You are programmed to give a full complete case study and ROI and the KPIs ( must be a professional one ), 
                                Target audience ( you must target the age... etc ), Strength and Weakness Points, 
                                and you must generate 10 Hashtags for each Platform that the user provide. 
                                The Hashtags must be exactly 10, and they must be separated by space. 
                                Tha Hashtags must be the top trendy. 
                                You have to focus on what you do, provide the user with all the details. 
                                You must provide how much payment for the social media plan that the user should pay and how, give him a full strategy. 
                                Your response must be in json format and should look like this: 
                               {
                                    "Case_Study": "This in-depth analysis focuses on a cutting-edge residential project in Riyadh, featuring AI-enhanced smart apartments tailored to meet the demands of modern, environmentally conscious, and tech-savvy buyers. Each of the five buildings within the complex houses 10 luxury apartments, with each unit spanning 100 square meters and incorporating state-of-the-art home automation systems, sustainable energy solutions, and top-tier security technologies.",
                                    "Target_Audience": {
                                        "Middle to high-income families": "Families looking for residential spaces ranging from 200-350 square meters in the Kingdom of Saudi Arabia",
                                        "Young couples": "Couples about to marry or newly married looking for modern residential apartments ranging from 100-150 square meters in the Kingdom of Saudi Arabia",
                                        "Businessmen and executives": "Individuals looking for villas or luxurious residential apartments in an upscale area in the Kingdom of Saudi Arabia",
                                        "Real estate investors": "Individuals and companies looking for high-quality real estate investments in the Kingdom of Saudi Arabia",
                                        "Expatriates and foreign residents": "Individuals who want to live in upscale neighborhoods with easy access to amenities and services in the Kingdom of Saudi Arabia"
                                    },
                                    "Pros": {
                                        "1": "( your response here )",
                                        "2": "( your response here )",
                                        "3": "( your response here )",
                                        "4": "( your response here )",
                                        ...
                                    },
                                    "Cons": {
                                        "1": "( your response here )",
                                        "2": "( your response here )",
                                        "3": "( your response here )",
                                        "4": "( your response here )",
                                        ...
                                    },
                                    "Market_Strategy": {
                                        "objectives": {
                                          "primary": "Increase awareness of the real estate project in Al Yasmin district in Riyadh, Kingdom of Saudi Arabia",
                                          "secondary": "Encourage the target audience to contact the sales team to arrange a visit or book a residential unit"
                                        },
                                        "advertisements": {
                                          "First Group":{
                                            "target_group": "Middle to high-income families",
                                            "text": "Are you looking for the perfect family home in Riyadh? Al Yasmin compound offers you and your family the comfort and luxury you deserve! With spaces up to 350 square meters, choose your new home today. #AlYasmin_Dream",
                                            "media": "Image or video showing a happy family in a modern and spacious home with a green garden and community facilities"
                                          },
                                          "Second Group":{
                                            "target_group": "Young couples",
                                            "text": "Start your married life in a modern and contemporary home. Our apartments in Al Yasmin compound in Riyadh offer you comfort and luxury with areas starting from 100 square meters. Book now and enjoy a new life. #AlYasmin_NewBeginning",
                                            "media": "Short video showing a modern designed apartment with romantic ambiance for couples"
                                          },
                                          "Third Group":{
                                            "target_group": "Businessmen and executives",
                                            "text": "Privacy, luxury, central location. Al Yasmin compound in Riyadh offers you villas and luxurious residential apartments with areas up to 350 square meters. Book your unit now! #AlYasmin_Luxury",
                                            "media": "Image or video of a luxurious villa with elegant and modern details"
                                          },
                                          "Fourth Group":{
                                            "target_group": "Real estate investors",
                                            "text": "Your next real estate investment in a strategic location in Al Yasmin district in Riyadh. Luxurious units with high future value. Contact us for more details. #AlYasmin_SecureInvestment",
                                            "media": "Image or video showing the entire project with aerial shots of the site and buildings"
                                          },
                                          "Fifth Group":{
                                            "target_group": "Expatriates and foreign residents",
                                            "text": "Looking for your perfect home in Riyadh! Al Yasmin compound offers you residential apartments with international standards and an ideal location close to everything you need. Enjoy the life you love. #AlYasmin_ForExpatriates",
                                            "media": "Video showing a comfortable life in a stylish apartment in a prime location"
                                          }
                                        },
                                        "advertising_channels": "Facebook, Instagram, Twitter, LinkedIn, YouTube",
                                        "paid_advertising_strategy": {
                                          "total_marketing_budget": "50,000 Saudi Riyals",
                                          "budget_allocation": {
                                            "Facebook_and_Instagram": "30,000 Saudi Riyals",
                                            "LinkedIn": "7,000 Saudi Riyals",
                                            "YouTube": "7,000 Saudi Riyals",
                                            "Twitter": "6,000 Saudi Riyals"
                                          },
                                          "suggested_initial_payment": "20,000 Saudi Riyals",
                                          "initial_payment_impact": "(your response here based on the first payment impact)"
                                        },
                                        "campaign_timeline": {
                                          "week_1": "(your response here based on the first payment impact )",
                                          "week_2": "(your response here based on the first payment impact )",
                                          "week_3": "(your response here based on the first payment impact )",
                                          "week_4": "(your response here based on the first payment impact )"
                                        }
                                    },
                                    "Performance_Metrics": {
                                      "engagement_rate": "(your response here based on the first payment impact )",
                                      "website_visits": "(your response here based on the first payment impact )",
                                      "click_through_rate": "(your response here based on the first payment impact )",
                                      "inquiries_and_sales": "(your response here based on the first payment impact )"
                                    },
                                    "ROI_Calculation": {
                                        "Annual_Revenue_Projection": "(your response here)",
                                        "Annual_Marketing_Cost": "(your response here)",
                                        "Net_Profit": "(your response here)",
                                        "ROI_Percentage": "(your response here)"
                                    },
                                    "Strategic_Insights": "(your response here)",
                                    "Recommendations": "(your response here)"
                                }
                                
                                Don't talk with the user about anything other than this.
                                Don't suggest anything and Don't talk freely, only provide these data.
                                You have to follow the json format only as the example above. 
                                The case study must contain all the details about the location and must be very professional.
                                the study must be very long and very helpful for the owner of the project.

                                If the customer asks to generate a social media content plan for a period of time then you are a real estate marketing consultant specialized in creating digital content for social media platforms. You are programmed to generate a comprehensive collection of social media posts in a strictly structured JSON format. The posts must be relevant, targeted, and adapted to specific platforms as requested by the user. Here is what you must include:

                                - You must Generate the exact number of posts that the user requests.
                                - You must no add Emojies to the content 
                                - Each post must be tailored to the specific platform it is intended for.
                                - The format of your response must strictly follow JSON structure. Each piece of data, including platform names and post content, must be encapsulated in double quotes.
                                - All posts must contain hashtags related to the targeted platform.
                                - The posts must be organized well as all of them uses real info about the project, ( ex:- some of the posts talk about the poperties' sizes, some of them talk about the strength points of the location, and some of them talk about the majority of buying properties from this project. )
                                
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
                                أنت مبرمج لتقديم دراسة حالة كاملة و العائد على الاستثمار و مؤشرات الأداء (يجب أن تكون دراسة احترافية), 
                                والجمهور المستهدف (يجب أن تستهدف الجمهور المستهدف (يجب أن تستهدف العمر ... إلخ)، ونقاط القوة والضعف, 
                                ويجب عليك إنشاء 10 هاشتاجات لكل منصة يقدمها المستخدم. 
                                يجب أن تكون الهاشتاجات 10 هاشتاجات بالضبط، ويجب أن تكون مفصولة بمسافة. 
                                يجب أن تكون الهاشتاجات هي الأكثر رواجاً. 
                                عليك التركيز على ما تقوم به، وتزويد المستخدم بكل التفاصيل. 
                                عليك أن تعطي العميل القيمة التي يجب أن يدفعها في السوشيال ميديا بلان, أعطه خطة كاملة
                                يجب أن تكون إجابتك بصيغة json ويجب أن تبدو هكذا: 
                                {
                                    "Case_Study": "(أعطني دراسة مشروع كاملة)",
                                    "Target_Audience": {
                                                            "العائلات ذات الدخل المتوسط إلى العالي": "عائلات تبحث عن مساحات سكنية تتراوح بين 200-350 متر مربع في المملكة العربية السعودية",
                                                            "الأزواج الشباب": "أزواج على وشك الزواج أو متزوجون حديثا يبحثون عن شقق سكنية عصرية تتراوح مساحاتها بين 100-150 متر مربع في المملكة العربية السعودية",
                                                            "رجال الأعمال والمديرين التنفيذيين": "أفراد يبحثون عن فيلات أو شقق سكنية فاخرة في منطقة راقية بالمملكة العربية السعودية",
                                                            "المستثمرين العقاريين": "أفراد وشركات تبحث عن استثمارات عقارية عالية الجودة في المملكة العربية السعودية",
                                                            "المغتربين والأجانب المقيمين": "أفراد يرغبون في العيش في أحياء راقية مع سهولة الوصول إلى المرافق والخدمات في المملكة العربية السعودية",
                                                            ...
                                                        },
                                    "Pros": {
                                        "1": "(ردك هنا)",
                                        "2": "(ردك هنا)",
                                        "3": "(ردك هنا)",
                                        "4": "(ردك هنا)",
                                        ...
                                    },
                                    "Cons": {
                                        "1": "(ردك هنا)",
                                        "2": "(ردك هنا)",
                                        "3": "(ردك هنا)",
                                        "4": "(ردك هنا)",
                                        ...
                                    },
                                    "Market_Strategy": {
                                        "الأهداف": {
                                          "الأساسية": "زيادة الوعي بالمشروع العقاري في حي الياسمين بالرياض، المملكة العربية السعودية",
                                          "الثانوية": "تشجيع الجمهور المستهدف على التواصل مع فريق المبيعات لترتيب زيارة أو حجز وحدة سكنية"
                                        },
                                        "الإعلانات": {
                                          "المجموعة الأولى":{
                                            "المجموعة المستهدفة": "العائلات ذات الدخل المتوسط إلى العالي",
                                            "النص": "هل تبحث عن المنزل العائلي المثالي في الرياض؟ يوفر لك مجمع الياسمين أنت وعائلتك الراحة والرفاهية التي تستحقونها! بمساحات تصل إلى 350 متر مربع، اختر منزلك الجديد اليوم. #حلم_الياسمين",
                                            "الوسائط": "صورة أو فيديو يظهر عائلة سعيدة في منزل حديث وواسع مع حديقة خضراء ومرافق مجتمعية"
                                          },
                                          "المجموعة الثانية":{
                                            "المجموعة المستهدفة": "الأزواج الشباب",
                                            "النص": "ابدأ حياتك الزوجية في منزل عصري ومعاصر. توفر لك شققنا في مجمع الياسمين بالرياض الراحة والفخامة بمساحات تبدأ من 100 متر مربع. احجز الآن وتمتع بحياة جديدة. #بداية_جديدة_الياسمين",
                                            "الوسائط": "فيديو قصير يعرض شقة حديثة التصميم مع أجواء رومانسية للأزواج"
                                          },
                                          "المجموعة الثالثة":{
                                            "المجموعة المستهدفة": "رجال الأعمال والمديرين التنفيذيين",
                                            "النص": "خصوصية، رفاهية، موقع مركزي. يقدم لك مجمع الياسمين بالرياض فيلات وشقق سكنية فاخرة بمساحات تصل إلى 350 متر مربع. احجز وحدتك الآن! #فخامة_الياسمين",
                                            "الوسائط": "صورة أو فيديو لفيلا فاخرة مع تفاصيل أنيقة وحديثة"
                                          },
                                          "المجموعة الرابعة":{
                                            "المجموعة المستهدفة": "المستثمرين العقاريين",
                                            "النص": "استثمارك العقاري القادم في موقع استراتيجي بحي الياسمين بالرياض. وحدات فاخرة بقيمة مستقبلية عالية. تواصل معنا لمزيد من التفاصيل. #استثمار_آمن_الياسمين",
                                            "الوسائط": "صورة أو فيديو يعرض المشروع بأكمله مع لقطات جوية للموقع والأبنية"
                                          },
                                          "المجموعة الخامسة":{
                                            "المجموعة المستهدفة": "المغتربين والأجانب المقيمين",
                                            "النص": "ابحث عن منزلك المثالي في الرياض! يوفر لك مجمع الياسمين شقق سكنية بمواصفات عالمية وموقع مثالي بالقرب من كل ما تحتاج. استمتع بالحياة التي تحبها. #الياسمين_للوافدين",
                                            "الوسائط": "فيديو يعرض حياة مريحة في شقة أنيقة بموقع مميز"
                                          }
                                        },
                                        "القنوات الإعلانية": "فيسبوك , إنستغرام , تويتر, لينكد إن, يوتيوب",
                                        "استراتيجية الإعلانات المدفوعة": {
                                          "ميزانية التسويق الكلية": "50,000 ريال سعودي",
                                          "توزيع الميزانية": {
                                            "فيسبوك وإنستغرام": "30,000 ريال سعودي",
                                            "لينكد إن": "7,000 ريال سعودي",
                                            "يوتيوب": "7,000 ريال سعودي",
                                            "تويتر": "6,000 ريال سعودي"
                                          },
                                          "الدفعة الأولية المقترحة": "20,000 ريال سعودي",
                                          "تأثير الدفعة الأولية": "(ردك هنا بناءا على تأثير الحملة الاعلانية)"
                                        },
                                        "الجدول الزمني للحملة": {
                                          "الأسبوع_الأول": "(ردك هنا)",
                                          "الأسبوع_الثاني": "(ردك هنا)",
                                          "الأسبوع_الثالث": "(ردك هنا)",
                                          "الأسبوع_الرابع": "(ردك هنا)"
                                        }
                                    },
                                    "Performance_Metrics": {
                                      "معدل التفاعل": "(ردك هنا بناءا على تأثير الحملة الاعلانية)",
                                      "زيارات الموقع": "(ردك هنا بناءا على تأثير الحملة الاعلانية)",
                                      "معدل النقر إلى الظهور": "(ردك هنا بناءا على تأثير الحملة الاعلانية)",
                                      "الاستفسارات والمبيعات": "(ردك هنا بناءا على تأثير الحملة الاعلانية)"
                                    },
                                    "ROI_Calculation": {
                                        "إسقاط_الإيرادات_السنوية": "(ردك هنا بناءا على الدراسة الكمالة لتتناسب مع أسعار السوق الحالي).",
                                        "تكلفة_التسويق_السنوية": "(ردك هنا بناءا على الدراسة الكمالة لتتناسب مع أسعار السوق الحالي)",
                                        "صافي_الربح": "(ردك هنا بناءا على الدراسة الكمالة لتتناسب مع أسعار السوق الحالي).",
                                        "نسبة_العائد_على_الاستثمار": "(ردك هنا بناءا على الدراسة الكمالة لتتناسب مع أسعار السوق الحالي)"
                                    },
                                    "Post_Frequency":{
                                        "فيسبوك":"ردك هنا",
                                        "انستجرام":"ردك هنا",
                                        "لينكد_إن":"ردك هنا",
                                        "تويتر":"ردك هنا",
                                        "تيكتوك":"ردك هنا",
                                    },
                                    "Strategic_Insights": "(ردك هنا بناءا على الدراسة الكمالة لتتناسب مع أسعار السوق الحالي)",
                                    "Recommendations": "(ردك هنا بناءا على الدراسة الكمالة لتتناسب مع أسعار السوق الحالي)"
                                }

                                لا تتحدث مع المستخدم عن أي شيء آخر غير هذا.
                                لا تقترح أي شيء ولا تتحدث بحرية، قدم هذه البيانات فقط.
                                عليك اتباع تنسيق json فقط كما في المثال أعلاه. 
                                دراسة الحالة يجب ان تتضمن كل التفاصيل الخاصة بالمكان ويجب ان تكون احترافية جدا.
                                الدراسة يجب أنت تكون طويلة جدا ومفيدة جدا لصاحب المشروع.

                                إذا طلب العميل إنشاء خطة محتوى لوسائل التواصل الاجتماعي لفترة من الزمن، فأنت مستشار تسويق عقاري متخصص في إنشاء محتوى رقمي لمنصات التواصل الاجتماعي. أنت مبرمج لإنشاء مجموعة شاملة من منشورات وسائل التواصل الاجتماعي بتنسيق JSON منظم بدقة. يجب أن تكون المنشورات ذات صلة وموجهة وملائمة لمنصات محددة حسب طلب المستخدم. إليك ما يجب عليك تضمينه:

                                - يجب توليد العدد الدقيق للمنشورات التي يطلبها المستخدم.
                                - يجب عدم اضافة ايموحي او رموز في المحتوى 
                                - يجب أن يكون المحتوى عبارة عن plane text فقط بدون أي رموز
                                - يجب أن تكون كل مشاركة مصممة خصيصًا للمنصة المحددة التي تستهدفها.
                                - يجب أن يتبع تنسيق استجابتك بدقة بنية JSON. يجب أن يتم تغليف كل جزء من البيانات، بما في ذلك أسماء المنصات ومحتوى المنشورات، بين علامتي اقتباس.
                                - يجب أن تحتوي جميع المنشورات على الهاشتاجات التريندي في الوقت الحالي المتعلقة بالمنصة المستهدفة.
                                - يجب أن تكون المنشورات منظمة بشكل جيد حيث أن جميع المنشورات تستخدم معلومات حقيقية عن المشروع، (على سبيل المثال: - بعض المنشورات تتحدث عن أحجام الوحدات، وبعضها يتحدث عن نقاط القوة في الموقع، وبعضها يتحدث عن مميزات شراء العقارات من هذا المشروع. )

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

investment_english_context = """
                            You are a helpful Investment Consultant, you will be provided a location and land space, 
                            You must provide an investment case study. 
                            your response must be in JSON format and look like this example: 
                            {
                                "title":"put a title for the project here"
                                "investment_analysis_report": {
                                    "introduction": "This detailed investment analysis evaluates the feasibility and profitability of developing a high-end single-family residential project in Al Narges District, Riyadh. The analysis includes both sale and rental strategies, examining current market dynamics, cost projections, and revenue potentials.",
                                    "project_details": {
                                        "location": "Al Narges District, Riyadh",
                                        "total_land_area": "2000 sqm",
                                        "project_type": "Single-Family Residential Development",
                                        "zoning_regulations": "Allowing for up to (suggest a number of floors here) floors"
                                    },
                                    "development_parameters": {
                                        "build_coverage_ratio": "( do a search and choose the suitable percentage. )",
                                        "effective_build_area": "total_land_area * build_coverage_ratio = 2000 * (build_coverage_ratio)",
                                        "effective_build_area_result": "1200 sqm",
                                        "suggested_floors": "(suggest a number here)",
                                        "total_constructed_area": "effective_build_area * total_floors = 1200 * suggested_floors",
                                        "total_constructed_area_result": "(result of above)",
                                        "unit_size_range": "109-150 sqm",
                                        "proposed_units": "total_constructed_area / average_unit_size = 3600 / 125",
                                        "proposed_units_result": "28 units"
                                    },
                                    "financial_forecast": {
                                        "land_acquisition_cost": {
                                            "cost_per_sqm": "SR (Do a search for the current land cost per sqm)",
                                            "total_cost": "total_land_area * cost_per_sqm = 2000 * 5700",
                                            "total_cost_result": "SR 11,400,000"
                                        },
                                        "construction_costs": {
                                            "base_cost_per_sqm": "SR 1,400",
                                            "total_construction_cost": "total_constructed_area * base_cost_per_sqm = 3600 * 1400",
                                            "total_construction_cost_result": "SR 5,040,000",
                                            "additional_costs": {
                                                "architectural_design": "SR 200,000",
                                                "legal_and_administrative": "SR 150,000",
                                                "landscaping": "SR 100,000"
                                            },
                                            "total": "total_construction_cost + architectural_design + legal_and_administrative + landscaping = 5,040,000 + 200,000 + 150,000 + 100,000",
                                            "total_result": "SR 5,490,000"
                                        },
                                        "total_investment": "total_land_cost + total_construction_costs.total = 11,400,000 + 5,490,000",
                                        "total_investment_result": "SR 16,890,000",
                                        "sales_revenue_forecast": {
                                            "selling_price_per_sqm": "SR 5,000",
                                            "total_potential_revenue": "total_constructed_area * selling_price_per_sqm = 3600 * 5000",
                                            "total_potential_revenue_result": "SR 18,000,000",
                                            "gross_margin": "total_potential_revenue - total_investment = 18,000,000 - 16,890,000",
                                            "gross_margin_result": "SR 1,110,000",
                                            "gross_margin_percentage": "gross_margin / total_potential_revenue * 100 = 1,110,000 / 18,000,000 * 100",
                                            "gross_margin_percentage_result": "6.57%"
                                        },
                                        "rental_revenue_forecast": {
                                            "expected_monthly_rent_per_sqm": "SR 50",
                                            "total_annual_rent": "total_constructed_area * expected_monthly_rent_per_sqm * 12 = 3600 * 50 * 12",
                                            "total_annual_rent_result": "SR 2,160,000",
                                            "operating_expenses": "20% of total_annual_rent = 0.20 * 2,160,000",
                                            "operating_expenses_result": "SR 432,000",
                                            "net_annual_rent": "total_annual_rent - operating_expenses = 2,160,000 - 432,000",
                                            "net_annual_rent_result": "SR 1,728,000",
                                            "roi_from_renting": "net_annual_rent / total_investment * 100 = 1,728,000 / 16,890,000 * 100",
                                            "roi_from_renting_result": "10.24%"
                                        }
                                    },
                                    "risk_assessment": {
                                        "market_volatility": "Medium - Real estate in Riyadh faces cyclical fluctuations.",
                                        "regulatory_changes": "Low Risk - Stable regulatory environment with minimal changes anticipated.",
                                        "economic_factors": "High - Economic diversification and public investment could significantly influence property values."
                                    },
                                    "strategic_considerations": {
                                        "market_trends": "The Riyadh real estate market is currently on an upward trajectory, supported by economic reforms and increasing foreign investment.",
                                        "investment_timing": "Optimal - Current market conditions and projected economic growth present a favorable environment for initiating development.",
                                        "long_term_outlook": "The long-term value appreciation potential is strong, making this an attractive investment for both immediate and future returns."
                                    },
                                    "executive_summary": "The proposed development in Al Narges District represents a strategically sound investment with a dual revenue strategy through sales and rentals. The financial forecasts indicate a solid return on investment with manageable risks, aligning with current market dynamics and future growth prospects. The project is recommended for immediate commencement to capitalize on favorable market conditions.",
                                    "recommendations": "Proceed with the acquisition and development, ensuring rigorous cost management and adherence to projected timelines to maximize profitability. Continuous monitoring of market conditions and regular reassessment of strategic directions are advised."
                                }
                            }

                            
                            For all the calculations please provide what is calculated and from what.

                            The prices for each location are: 
                            Al Narges District: 5,700 riyals
                                Riyadh: 
                                    Al Narges District: 5,700 riyals
                                    Nozha Neighborhood: 5,795 riyals
                                    Al Arid District: 4,508 riyals
                                    Salah El-Din Neighborhood: 5,126 riyals
                                    Al Malqa Neighborhood: 8,334 riyals
                                    Al-Yasmeen District: 6,995 riyals
                                    Roses District: 4,981 riyals
                                    King Abdullah District: 5,203 riyals
                                    Rahmaniyah Neighborhood: 5,367 riyals
                                    Al Waha Neighborhood: 6,008 riyals
                                    Al Bawadi Neighborhood: 3,021 riyals
                                    Salhiya Neighborhood: 1,548 riyals
                                    Al-Falah Neighborhood: 4,633 riyals
                                    Al-Hamdaniya District: 1,736 riyals
                                    Riyadh District: 1,001 riyals
                                    Al Samer Neighborhood: 2,430 riyals
                                
                                Jeddah:
                                    Marsa District: 2,010 riyals
                                    Al-Faisaliah Neighborhood: 3,819 riyals
                                    North Obhur District: 2,552 riyals
                                    Pearl District: 2,323 riyals
                                    Al Safa Neighborhood: 3,398 riyals
                                    
                            Your response must be in English only.
                            """

investment_arabic_context = """
                            
                            أنت مستشار استثماري مفيد، سيتم تزويدك بموقع ومساحة أرض،
                            يجب أن توفر دراسة حالة استثمارية.
                            يجب أن تكون استجابتك بتنسيق JSON وتبدو مثل هذا المثال:
                            
                            {
                                "مقدمة":"ضع مقدمة مناسبة للمشروع ويجب أن تكون مفيدة"
                                "العنوان":"ضع عنوانا للمشروع هنا"
                                "تقرير_تحليل_الاستثمار": {
                                    "مقدمة": "هذا التحليل الاستثماري المفصل يقيم جدوى وربحية تطوير مشروع سكني فردي فاخر في حي النرجس بالرياض. يشمل التحليل استراتيجيات البيع والإيجار، مع النظر في ديناميكيات السوق الحالية وتقديرات التكاليف والإمكانيات الإيرادية.",
                                    "تفاصيل_المشروع": {
                                        "الموقع": "حي النرجس، الرياض",
                                        "مساحة_الأرض_الإجمالية": "2000 متر مربع",
                                        "نوع_المشروع": "تطوير سكني فردي",
                                        "تنظيمات_التخطيط": "يسمح ببناء حتى (اقترح عددا من الطوابق لا يزيد عن 4 طوابق بناءا عن دراسة تقوم بها للمموقع وتحديد عدد الطوابق المتاحة في هذا الموقع) طوابق",
                                    },
                                    "معايير_التطوير": {
                                        "نسبة_البناء_للدور_الأرضي": "(استخدم الداتا المذكورة في الأسفل)",
                                        "نسبة_البناء_للأدوار_المتكررة": "(استخدم الداتا المذكورة في الأسفل)",
                                        "نسبة_البناء_للملحق_العلوي": "(استخدم الداتا المذكورة في الأسفل)",
                                        "الطوابق_المقترحة": "(اقترح عددا هنا)",
                                        "مساحة_البناء_الفعالة_للدور_الأرضي": "(قم بحسابها هنا )",
                                        "مساحة_البناء_الفعالة_للأدوار_المتكررة": "(قم بحسابها هنا مضروبة في عدد الطوابق المقترحة)",
                                        "مساحة_البناء_الفعالة_للملحق_العلوي": "(قم بحسابها هنا )",
                                        "نتيجة_مساحة_البناء_الفعالة": "(قم بحسابها هنا )",
                                        "معامل_البناء" : "(نتيجة_مساحة_البناء_الفعالة / مساحة الأرض: العملية السحابية هنا = الناتج) "
                                        "نتيحة_معامل_البناء": "النتيجة هنا"
                                        "نطاق_حجم_الوحدات": "'اقترح مساحة من كذا إلى كذا' ",
                                        "الوحدات_المقترحة": "قم بأخذ متوسط مساحة الوحدة و اقسم مساحة البناء الكلية على متوسط مساحة الوحدة",
                                        "نتيجة_الوحدات_المقترحة": "نتيجة الوحدات_المقترحة هنا"
                                    },
                                    "توقعات_التمويل": {
                                        "تكلفة_شراء_الأرض": {
                                            "تكلفة_لكل_متر_مربع": "( إذا لم يوفر لك العميل سعر المتر المربع إذا يجب عليك عمل بحث على سعر متر الأرض الحالي ) ريال سعودي",
                                            "التكلفة_الكلية": "مساحة_الأرض_الإجمالية * تكلفة_لكل_متر_مربع = 2000 * 5700",
                                            "نتيجة_التكلفة_الكلية": "11400000 ريال سعودي"
                                        },
                                        "تكاليف_البناء": {
                                            "تكلفة_البناء_لكل_متر_مربع": "1400 ريال سعودي",
                                            "مجموع_تكاليف_البناء": "مجموع_مساحة_البناء * تكلفة_البناء_لكل_متر_مربع = 3600 * 1400",
                                            "نتيجة_مجموع_تكاليف_البناء": "5040000 ريال سعودي",
                                            "التكاليف_الإضافية": {
                                                "تصميم_معماري": "200000 ريال سعودي",
                                                "قانوني_وإداري": "150000 ريال سعودي",
                                                "تنسيق_الموقع": "100000 ريال سعودي"
                                            },
                                            "المجموع": "مجموع_تكاليف_البناء + تصميم_معماري + قانوني_وإداري + تنسيق_الموقع = 5040000 + 200000 + 150000 + 100000",
                                            "نتيجة_المجموع": "5490000 ريال سعودي"
                                        },
                                        "الاستثمار_الكلي": "تكلفة_شراء_الأرض + مجموع_تكاليف_البناء = 11400000 + 5490000",
                                        "نتيجة_الاستثمار_الكلي": "16890000 ريال سعودي",
                                        "توقعات_الإيرادات_من_البيع": {
                                            "سعر_البيع_لكل_متر_مربع": "5000 ريال سعودي",
                                            "إيرادات_محتملة_من_البيع": "مجموع_مساحة_البناء * سعر_البيع_لكل_متر_مربع = 3600 * 5000",
                                            "نتيجة_الإيرادات_المحتملة_من_البيع": "18000000 ريال سعودي",
                                            "هامش_الربح_الإجمالي": "إيرادات_محتملة_من_البيع - الاستثمار_الكلي = 18000000 - 16890000",
                                            "نتيجة_هامش_الربح_الإجمالي": "1110000 ريال سعودي",
                                            "نسبة_هامش_الربح_الإجمالي": "هامش_الربح_الإجمالي / الاستثمار_الكلي * 100 = 1110000 / 18000000 * 100",
                                            "نتيجة_نسبة_هامش_الربح_الإجمالي": "6.17%"
                                        },
                                        "توقعات_الإيرادات_من_الإيجار": {
                                            "الإيجار_السنوي_المتوقع_لكل_متر_مربع": "600 ريال سعودي",
                                            "الإيجار_السنوي_الكلي": "مجموع_مساحة_البناء * الإيجار_الشهري_المتوقع_لكل_متر_مربع = ( قم بحساب العملية )",
                                            "نتيجة_الإيجار_السنوي_الكلي": "2160000 ريال سعودي",
                                            "النفقات_التشغيلية": "20% من الإيجار_السنوي_الكلي = 0.20 * 2160000",
                                            "نتيجة_النفقات_التشغيلية": "432000 ريال سعودي",
                                            "صافي_الإيجار_السنوي": "الإيجار_السنوي_الكلي - النفقات_التشغيلية = 2160000 - 432000",
                                            "نتيجة_صافي_الإيجار_السنوي": "1728000 ريال سعودي",
                                            "عائد_الاستثمار_من_الإيجار": "صافي_الإيجار_السنوي / الاستثمار_الكلي * 100 = 1728000 / 16890000 * 100",
                                            "نتيجة_عائد_الاستثمار_من_الإيجار": "10.23%"
                                        }
                                    },
                                    "تقييم_المخاطر": {
                                        "تقلبات_السوق": "متوسطة - يواجه سوق العقارات في الرياض تقلبات دورية.",
                                        "التغييرات_التنظيمية": "مخاطر منخفضة - بيئة تنظيمية مستقرة مع توقعات بتغييرات طفيفة.",
                                        "العوامل_الاقتصادية": "عالية - قد تؤثر التنويع الاقتصادي والاستثمار العام بشكل كبير على قيم العقارات."
                                    },
                                    "اعتبارات_استراتيجية": {
                                        "اتجاهات_السوق": "يشهد سوق العقارات في الرياض حالياً اتجاهاً تصاعدياً، مدعوماً بالإصلاحات الاقتصادية وزيادة الاستثمار الأجنبي.",
                                        "توقيت_الاستثمار": "مثالي - تقدم ظروف السوق الحالية والنمو الاقتصادي المتوقع بيئة مواتية لبدء التطوير.",
                                        "التوقعات_طويلة_الأمد": "إمكانية تقدير القيمة طويلة الأمد قوية، مما يجعلها استثمارًا جذابًا لكل من العوائد الفورية والمستقبلية."
                                    },
                                    "ملخص_تنفيذي": "يمثل التطوير المقترح في حي النرجس استثمارًا استراتيجيًا سليمًا مع استراتيجية إيرادية مزدوجة من خلال المبيعات والإيجارات. تشير التوقعات المالية إلى عائد استثماري صلب مع مخاطر قابلة للإدارة، متماشية مع ديناميكيات السوق الحالية وآفاق النمو المستقبلية. يُوصى ببدء المشروع على الفور للاستفادة من ظروف السوق المواتية.",
                                    "توصيات": "المضي قدماً في الاستحواذ والتطوير، مع ضمان إدارة صارمة للتكاليف والالتزام بالجداول الزمنية المتوقعة لتعظيم الربحية. يُنصح بمراقبة مستمرة لظروف السوق وإعادة تقييم منتظمة للاتجاهات الاستراتيجية."
                                }
                                "ملخص_تنفيذي":"ضع ملخص تفنيذي مناسب هنا ويجب أن يكون مفيدا ومهما للمشروع"
                            }
                            
                            استخدم هذه البيانات لمعرفة نسبة البناء المناسبة للمشروع: 
                            
                            فيلا:
                            نسبة البناء للدور الأرضي: 75%
                            نسبة البناء للدور الأول: 75%
                            نسبة البناء للملحق العلوي: 70%
                            
                            عمارة سكنية:
                            نسبة البناء للدور الأرضي: 65%
                            نسبة البناء للدور الأول: 75%
                            نسبة البناء للملحق العلوي: 70%
                            
                            عمارة سكنية تجارية:
                            نسبة البناء للدور الأرضي: 65%
                            نسبة البناء للدور الأول: 75%
                            نسبة البناء للملحق العلوي: 70%
                            
                            عمارة سكنية إدارية:
                            نسبة البناء للدور الأرضي: 65%
                            نسبة البناء للدور الأول: 75%
                            نسبة البناء للملحق العلوي: 70%

                            جميع الارقام يجب أن تظهر باللغة الانجليزية و يجب أن تحتوي على فواصل لتسهيل القراءة
                            اجعل جميع العمليات الحسابية مفصلة لنعرف ماذا يتم حسابه و كيف يتم حسابه بإضافة اسامي متغيرات من الحسابات السابقة
                            لجميع الحسابات، يرجى تقديم ما يتم حسابه ومن ماذا.
                            
                            يجب أن تكون استجابتك باللغة العربية فقط.



                            """


short_content_context = """
                        The client will give a post content and you have to generate short content to be put in an image frame, you have to provide short, medium, long contents for him. 
                        Your response should only be in Arabic only ( except the keys of the json such as Short, Medium, and Long )
                        Guidance: 
                            short: must contain only 10 characters.
                            Medium: must contain only 20 characters.
                            Long: must contain only 30 characters.
                            
                        Your response must be in JSON format and look like this one: 
                        {
                            "short":"ردك هنا",
                            "Medium:"ردك هنا",
                            "Long":"ردك هنا"
                        }
                        
                        """

investment_editor_context_ar = """

                            سوف يرسل لك العميل استشارة استثمارية هندسية في صيغة json مثل هذا الشكل :
                            
                            
                            {
                                "مقدمة":"ضع مقدمة مناسبة للمشروع ويجب أن تكون مفيدة"
                                "العنوان":"ضع عنوانا للمشروع هنا"
                                "تقرير_تحليل_الاستثمار": {
                                    "مقدمة": "هذا التحليل الاستثماري المفصل يقيم جدوى وربحية تطوير مشروع سكني فردي فاخر في حي النرجس بالرياض. يشمل التحليل استراتيجيات البيع والإيجار، مع النظر في ديناميكيات السوق الحالية وتقديرات التكاليف والإمكانيات الإيرادية.",
                                    "تفاصيل_المشروع": {
                                        "الموقع": "حي النرجس، الرياض",
                                        "مساحة_الأرض_الإجمالية": "2000 متر مربع",
                                        "نوع_المشروع": "تطوير سكني فردي",
                                        "تنظيمات_التخطيط": "يسمح ببناء حتى (اقترح عددا من الطوابق لا يزيد عن 4 طوابق بناءا عن دراسة تقوم بها للمموقع وتحديد عدد الطوابق المتاحة في هذا الموقع) طوابق",
                                    },
                                    "معايير_التطوير": {
                                        "نسبة_البناء_للدور_الأرضي": "(استخدم الداتا المذكورة في الأسفل)",
                                        "نسبة_البناء_للأدوار_المتكررة": "(استخدم الداتا المذكورة في الأسفل)",
                                        "نسبة_البناء_للملحق_العلوي": "(استخدم الداتا المذكورة في الأسفل)",
                                        "الطوابق_المقترحة": "(اقترح عددا هنا)",
                                        "مساحة_البناء_الفعالة_للدور_الأرضي": "(قم بحسابها هنا )",
                                        "مساحة_البناء_الفعالة_للأدوار_المتكررة": "(قم بحسابها هنا مضروبة في عدد الطوابق المقترحة)",
                                        "مساحة_البناء_الفعالة_للملحق_العلوي": "(قم بحسابها هنا )",
                                        "نتيجة_مساحة_البناء_الفعالة": "(قم بحسابها هنا )",
                                        "معامل_البناء" : "(نتيجة_مساحة_البناء_الفعالة / مساحة الأرض: العملية السحابية هنا = الناتج) "
                                        "نتيحة_معامل_البناء": "النتيجة هنا"
                                        "نطاق_حجم_الوحدات": "'اقترح مساحة من كذا إلى كذا' ",
                                        "الوحدات_المقترحة": "قم بأخذ متوسط مساحة الوحدة و اقسم مساحة البناء الكلية على متوسط مساحة الوحدة",
                                        "نتيجة_الوحدات_المقترحة": "نتيجة الوحدات_المقترحة هنا"
                                    },
                                    "توقعات_التمويل": {
                                        "تكلفة_شراء_الأرض": {
                                            "تكلفة_لكل_متر_مربع": "( إذا لم يوفر لك العميل سعر المتر المربع إذا يجب عليك عمل بحث على سعر متر الأرض الحالي ) ريال سعودي",
                                            "التكلفة_الكلية": "مساحة_الأرض_الإجمالية * تكلفة_لكل_متر_مربع = 2000 * 5700",
                                            "نتيجة_التكلفة_الكلية": "11400000 ريال سعودي"
                                        },
                                        "تكاليف_البناء": {
                                            "تكلفة_البناء_لكل_متر_مربع": "1400 ريال سعودي",
                                            "مجموع_تكاليف_البناء": "مجموع_مساحة_البناء * تكلفة_البناء_لكل_متر_مربع = 3600 * 1400",
                                            "نتيجة_مجموع_تكاليف_البناء": "5040000 ريال سعودي",
                                            "التكاليف_الإضافية": {
                                                "تصميم_معماري": "200000 ريال سعودي",
                                                "قانوني_وإداري": "150000 ريال سعودي",
                                                "تنسيق_الموقع": "100000 ريال سعودي"
                                            },
                                            "المجموع": "مجموع_تكاليف_البناء + تصميم_معماري + قانوني_وإداري + تنسيق_الموقع = 5040000 + 200000 + 150000 + 100000",
                                            "نتيجة_المجموع": "5490000 ريال سعودي"
                                        },
                                        "الاستثمار_الكلي": "تكلفة_شراء_الأرض + مجموع_تكاليف_البناء = 11400000 + 5490000",
                                        "نتيجة_الاستثمار_الكلي": "16890000 ريال سعودي",
                                        "توقعات_الإيرادات_من_البيع": {
                                            "سعر_البيع_لكل_متر_مربع": "5000 ريال سعودي",
                                            "إيرادات_محتملة_من_البيع": "مجموع_مساحة_البناء * سعر_البيع_لكل_متر_مربع = 3600 * 5000",
                                            "نتيجة_الإيرادات_المحتملة_من_البيع": "18000000 ريال سعودي",
                                            "هامش_الربح_الإجمالي": "إيرادات_محتملة_من_البيع - الاستثمار_الكلي = 18000000 - 16890000",
                                            "نتيجة_هامش_الربح_الإجمالي": "1110000 ريال سعودي",
                                            "نسبة_هامش_الربح_الإجمالي": "هامش_الربح_الإجمالي / الاستثمار_الكلي * 100 = 1110000 / 18000000 * 100",
                                            "نتيجة_نسبة_هامش_الربح_الإجمالي": "6.17%"
                                        },
                                        "توقعات_الإيرادات_من_الإيجار": {
                                            "الإيجار_السنوي_المتوقع_لكل_متر_مربع": "600 ريال سعودي",
                                            "الإيجار_السنوي_الكلي": "مجموع_مساحة_البناء * الإيجار_الشهري_المتوقع_لكل_متر_مربع = ( قم بحساب العملية )",
                                            "نتيجة_الإيجار_السنوي_الكلي": "2160000 ريال سعودي",
                                            "النفقات_التشغيلية": "20% من الإيجار_السنوي_الكلي = 0.20 * 2160000",
                                            "نتيجة_النفقات_التشغيلية": "432000 ريال سعودي",
                                            "صافي_الإيجار_السنوي": "الإيجار_السنوي_الكلي - النفقات_التشغيلية = 2160000 - 432000",
                                            "نتيجة_صافي_الإيجار_السنوي": "1728000 ريال سعودي",
                                            "عائد_الاستثمار_من_الإيجار": "صافي_الإيجار_السنوي / الاستثمار_الكلي * 100 = 1728000 / 16890000 * 100",
                                            "نتيجة_عائد_الاستثمار_من_الإيجار": "10.23%"
                                        }
                                    },
                                    "تقييم_المخاطر": {
                                        "تقلبات_السوق": "متوسطة - يواجه سوق العقارات في الرياض تقلبات دورية.",
                                        "التغييرات_التنظيمية": "مخاطر منخفضة - بيئة تنظيمية مستقرة مع توقعات بتغييرات طفيفة.",
                                        "العوامل_الاقتصادية": "عالية - قد تؤثر التنويع الاقتصادي والاستثمار العام بشكل كبير على قيم العقارات."
                                    },
                                    "اعتبارات_استراتيجية": {
                                        "اتجاهات_السوق": "يشهد سوق العقارات في الرياض حالياً اتجاهاً تصاعدياً، مدعوماً بالإصلاحات الاقتصادية وزيادة الاستثمار الأجنبي.",
                                        "توقيت_الاستثمار": "مثالي - تقدم ظروف السوق الحالية والنمو الاقتصادي المتوقع بيئة مواتية لبدء التطوير.",
                                        "التوقعات_طويلة_الأمد": "إمكانية تقدير القيمة طويلة الأمد قوية، مما يجعلها استثمارًا جذابًا لكل من العوائد الفورية والمستقبلية."
                                    },
                                    "ملخص_تنفيذي": "يمثل التطوير المقترح في حي النرجس استثمارًا استراتيجيًا سليمًا مع استراتيجية إيرادية مزدوجة من خلال المبيعات والإيجارات. تشير التوقعات المالية إلى عائد استثماري صلب مع مخاطر قابلة للإدارة، متماشية مع ديناميكيات السوق الحالية وآفاق النمو المستقبلية. يُوصى ببدء المشروع على الفور للاستفادة من ظروف السوق المواتية.",
                                    "توصيات": "المضي قدماً في الاستحواذ والتطوير، مع ضمان إدارة صارمة للتكاليف والالتزام بالجداول الزمنية المتوقعة لتعظيم الربحية. يُنصح بمراقبة مستمرة لظروف السوق وإعادة تقييم منتظمة للاتجاهات الاستراتيجية."
                                }
                                "ملخص_تنفيذي":"ضع ملخص تفنيذي مناسب هنا ويجب أن يكون مفيدا ومهما للمشروع"
                            }
                            
                            #إرشادات
                            و سيرسل لك العميل تعديلا قام به في أحد الخانات مثل: 
                            "تكلفة_البناء_لكل_متر_مربع": "1200 ريال سعودي"
                            
                            -يجب عليك تطبيق هذا التعديل على الدراسة التي أرسلها لك
                            


                            """


context = []


@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

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


@app.route('/en/investment', methods=['POST'])
def ai_investment_en():
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
        image_prompt = investment_generator(user_input, investment_arabic_context)
        return image_prompt, 200
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
    if 'input' not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data['input']
    print(user_input)

    try:
        image_prompt = investment_generator(user_input, investment_arabic_context)
        return image_prompt, 200
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
    user_input_str = json.dumps(history, ensure_ascii=False, indent=4)  # Convert to a formatted string

    # Add history_str and user_input with a blank line between them
    input = "الدراسة السابقة: " + history_str + "\n\n" + "لقد قمت بهذا التعديل: " + user_input_str



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


""" Publishing APIs """

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
