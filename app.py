import base64
import hashlib
from urllib.parse import urlencode, quote_plus
import json
import os

import requests
from flask import Flask, jsonify, request, redirect, render_template, session, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import numpy as np
import re

from langdetect import detect

from api.openai_api_requests import case_study_ai, social_media_ai, image_creator, prompt_creator, prompt_enhancer, image_analyzer, investment_generator

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = os.urandom(24)

# Initialize a Context to train GPT-4 on
case_study_training_context_english = """
                                You are a real estate marketing consultant. 
                                You are programmed to give a full complete case study (ROI) ( must be a professional one ), 
                                Target audience ( you must target the age... etc ), Strength and Weakness Points, 
                                and you must generate 10 Hashtags for each Platform that the user provide. 
                                The Hashtags must be exactly 10, and they must be separated by space. 
                                Tha Hashtags must be the top trendy. 
                                You have to focus on what you do, provide the user with all the details. 
                                You must provide how much payment for the social media plan that the user should pay and how, give him a full strategy. 
                                Your response must be in json format and should look like this: 
                                {
                                "Case_Study": "your response here", 
                                "Target_Audience": "your response here", 
                                "Pros": {
                                        "1":"your response here",
                                        "2":"your response here",
                                        ...    
                                        }, 
                                "Cons": {
                                        "1":"your response here",
                                        "2":"your response here",
                                        ...    
                                        },
                                "Social_Media_Strategy: " your response here , 
                                "Facebook_Hashtags": "only if provided from the user", 
                                "Instagram_Hashtags": "only if provided from the user", 
                                "Twitter_Hashtags": "only if provided from the user", 
                                "LinkedIn_Hashtags": "only if provided from the user", 
                                }
                                Don't talk with the user about anything other than this.
                                Don't suggest anything and Don't talk freely, only provide these data.
                                You have to follow the json format only as the example above. 
                                The case study must contain all the details about the location and must be very professional.
                                the study must be very long and very helpful for the owner of the project.

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
                                أنت مبرمج لتقديم دراسة حالة كاملة كاملة (ROI) (يجب أن تكون دراسة احترافية), 
                                والجمهور المستهدف (يجب أن تستهدف الجمهور المستهدف (يجب أن تستهدف العمر ... إلخ)، ونقاط القوة والضعف, 
                                ويجب عليك إنشاء 10 هاشتاجات لكل منصة يقدمها المستخدم. 
                                يجب أن تكون الهاشتاجات 10 هاشتاجات بالضبط، ويجب أن تكون مفصولة بمسافة. 
                                يجب أن تكون الهاشتاجات هي الأكثر رواجاً. 
                                عليك التركيز على ما تقوم به، وتزويد المستخدم بكل التفاصيل. 
                                عليك أن تعطي العميل القيمة التي يجب أن يدفعها في السوشيال ميديا بلان, أعطه خطة كاملة
                                يجب أن تكون إجابتك بصيغة json ويجب أن تبدو هكذا: 
                                {
                                "Case_Study": "ردك هنا", 
                                "Target_Audience": "ردك هنا", 
                                "Pros": {
                                        "1":"ردك هنا",
                                        "2":"ردك هنا",
                                        ...    
                                        },
                                "Cons": {
                                        "1":"ردك هنا",
                                        "2":"ردك هنا",
                                        ...    
                                        }, 
                                "Social_Media_Strategy: " your response here ", 
                                "Facebook_Hashtags": "فقط اذا وفرها العميل", 
                                "Instagram_Hashtags": "فقط اذا وفرها العميل", 
                                "Twitter_Hashtags": "فقط اذا وفرها العميل", 
                                "LinkedIn_Hashtags": "فقط اذا وفرها العميل", 
                                }
                                لا تتحدث مع المستخدم عن أي شيء آخر غير هذا.
                                لا تقترح أي شيء ولا تتحدث بحرية، قدم هذه البيانات فقط.
                                عليك اتباع تنسيق json فقط كما في المثال أعلاه. 
                                دراسة الحالة يجب ان تتضمن كل التفاصيل الخاصة بالمكان ويجب ان تكون احترافية جدا.
                                الدراسة يجب أنت تكون طويلة جدا ومفيدة جدا لصاحب المشروع.
                                
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

investment_english_context = """
                            You are a helpful Investment Consultant, you will be provided a location and land space, 
                            You must provide an investment case study. 
                            your response must be in JSON format and look like this example: 
                            {
                                "investment_analysis_report": {
                                    "introduction": "This detailed investment analysis evaluates the feasibility and profitability of developing a high-end single-family residential project in Al Narges District, Riyadh. The analysis includes both sale and rental strategies, examining current market dynamics, cost projections, and revenue potentials.",
                                    "project_details": {
                                        "location": "Al Narges District, Riyadh",
                                        "total_land_area": "2000 sqm",
                                        "project_type": "Single-Family Residential Development",
                                        "zoning_regulations": "Residential R3, allowing for up to (suggest a number of floors here) stories"
                                    },
                                    "development_parameters": {
                                        "build_coverage_ratio": "60%",
                                        "effective_build_area": "total_land_area * build_coverage_ratio = 2000 * 0.60",
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
                                            "cost_per_sqm": "SR 5,700",
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
                                "تقرير_تحليل_الاستثمار": {
                                    "مقدمة": "هذا التحليل الاستثماري المفصل يقيم جدوى وربحية تطوير مشروع سكني فردي فاخر في حي النرجس بالرياض. يشمل التحليل استراتيجيات البيع والإيجار، مع النظر في ديناميكيات السوق الحالية وتقديرات التكاليف والإمكانيات الإيرادية.",
                                    "تفاصيل_المشروع": {
                                        "الموقع": "حي النرجس، الرياض",
                                        "مساحة_الأرض_الإجمالية": "2000 متر مربع",
                                        "نوع_المشروع": "تطوير سكني فردي",
                                        "تنظيمات_التخطيط": "سكني R3، يسمح ببناء حتى (اقترح عددا من الطوابق هنا) طوابق"
                                    },
                                    "معايير_التطوير": {
                                        "نسبة_البناء": "60%",
                                        "مساحة_البناء_الفعالة": "مساحة_الأرض_الإجمالية * نسبة_البناء = 2000 * 0.60",
                                        "نتيجة_مساحة_البناء_الفعالة": "1200 متر مربع",
                                        "الطوابق_المقترحة": "(اقترح عددا هنا)",
                                        "مجموع_مساحة_البناء": "مساحة_البناء_الفعالة * الطوابق_المقترحة = 1200 * الطوابق_المقترحة",
                                        "نتيجة_مجموع_مساحة_البناء": "(نتيجة الحساب السابق)",
                                        "نطاق_حجم_الوحدات": "109-150 متر مربع",
                                        "الوحدات_المقترحة": "مجموع_مساحة_البناء / متوسط_حجم_الوحدة = 3600 / 125",
                                        "نتيجة_الوحدات_المقترحة": "28 وحدة"
                                    },
                                    "توقعات_التمويل": {
                                        "تكلفة_شراء_الأرض": {
                                            "تكلفة_لكل_متر_مربع": "5700 ريال سعودي",
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
                                            "نسبة_هامش_الربح_الإجمالي": "هامش_الربح_الإجمالي / إيرادات_محتملة_من_البيع * 100 = 1110000 / 18000000 * 100",
                                            "نتيجة_نسبة_هامش_الربح_الإجمالي": "6.17%"
                                        },
                                        "توقعات_الإيرادات_من_الإيجار": {
                                            "الإيجار_الشهري_المتوقع_لكل_متر_مربع": "50 ريال سعودي",
                                            "الإيجار_السنوي_الكلي": "مجموع_مساحة_البناء * الإيجار_الشهري_المتوقع_لكل_متر_مربع * 12 = 3600 * 50 * 12",
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
                            }

                            
                            لجميع الحسابات، يرجى تقديم ما يتم حسابه ومن ماذا.

                            الأسعار لكل موقع هي:
                            الرياض:
                            حي النرجس: 5700 ريال
                            حي النزهة: 5795 ريال
                            حي العارض: 4508 ريال
                            حي صلاح الدين: 5126 ريال
                            حي الملقا: 8334 ريال
                            حي الياسمين: 6995 ريال
                            حي الورود: 4981 ريال
                            حي الملك عبدالله: 5203 ريال
                            حي الرحمانية: 5367 ريال
                            حي الواحة: 6008 ريال
                            حي البوادي: 3021 ريال
                            حي الصالحية: 1548 ريال
                            حي الفلاح: 4633 ريال
                            حي الحمدانية: 1736 ريال
                            حي الرياض: 1001 ريال
                            حي السامر: 2430 ريال
                            
                            جدة:
                            حي المرسى: 2010 ريال
                            حي الفيصلية: 3819 ريال
                            حي أبحر الشمالية: 2552 ريال
                            حي اللؤلؤ: 2323 ريال
                            حي الصفا: 3398 ريال
                            
                            يجب أن تكون استجابتك باللغة العربية فقط.



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
        image_prompt = investment_generator(user_input, investment_english_context)
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



""" Publishing APIs """


#Twitter
CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')
REDIRECT_URI = 'https://takamol-advanced-ai-mu.vercel.app/twitter-callback'

def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8').replace('=', '')

def generate_code_challenge(verifier):
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('utf-8')).digest()).decode('utf-8').replace('=', '')

@app.route('/twitter-login')
def twitter_login():
    code_verifier = generate_code_verifier()
    session['code_verifier'] = code_verifier
    code_challenge = generate_code_challenge(code_verifier)
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    session['state'] = state
    params = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'scope': 'tweet.read tweet.write users.read',
    'state': state,
    'code_challenge': code_challenge,
    'code_challenge_method': 'S256'
}
    url = f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
    return redirect(url)

@app.route('/twitter-callback')
def twitter_callback():
    code = request.args.get('code')
    returned_state = request.args.get('state')
    if returned_state != session.pop('state', None):
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
    response = requests.post("https://api.twitter.com/2/oauth2/token", headers=headers, data=urlencode(data))
    if response.status_code != 200:
        return jsonify(error="Failed to retrieve access token", details=response.json()), 400
    session['access_token'] = response.json().get('access_token')
    session['user_id'] = response.json().get('user_id')
    return redirect('/post-tweet')


@app.route('/post-tweet', methods=['POST'])  # Ensure the method is POST
def post_tweet():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is missing"}), 401

    # Check if the request contains JSON data
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()  # Get the JSON data
    tweet_text = data.get('text')  # Extract the tweet text

    # Validate tweet text
    if not tweet_text:
        return jsonify({"error": "No tweet text provided"}), 400

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {'text': tweet_text}  # Use the text from the request
    response = requests.post("https://api.twitter.com/2/tweets", headers=headers, json=payload)

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
linkedIn_REDIRECT_URI = 'https://takamol-advanced-ai-mu.vercel.app/linkedin-callback'

@app.route('/linkedin-login')
def login():
    state = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    session['linkedin-state'] = state
    linkedin_auth_url = "https://www.linkedin.com/oauth/v2/authorization?response_type=code"
    linkedin_auth_url += f"&client_id={linkedIn_CLIENT_ID}"
    linkedin_auth_url += f"&redirect_uri={linkedIn_REDIRECT_URI}"
    linkedin_auth_url += f"&state={state}"
    linkedin_auth_url += "&scope=profile%20email%20openid%20w_member_social"
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
        scope = token_response.json().get('scope')
        session['linkedin_access_token'] = access_token

        try:
            # Fetch and store the user's URN
            profile_url = 'https://api.linkedin.com/v2/userinfo'
            profile_headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = requests.get(profile_url, headers=profile_headers)
            profile_response.raise_for_status()
            session['linkedin_urn'] = profile_response.json().get('sub')

            return redirect(url_for('post'))
        except requests.exceptions.RequestException as e:
            return jsonify({'error': str(e), 'details': 'Failed to get user profile'}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e), 'details': 'Failed to get access token'}), 400

@app.route('/linkedin-post')
def post():
    if 'linkedin_access_token' not in session or 'linkedin_urn' not in session:
        return redirect(url_for('linkedin-login'))
    access_token = session['linkedin_access_token']
    user_urn = session['linkedin_urn']
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
                    "text": "Hello, LinkedIn world from Flask!"
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
    app.run(debug=True)
