import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)

# وظيفة لتحليل المشروع العقاري وتوليد الاستراتيجيات الإعلانية
def generate_real_estate_campaign(user_input):
    user_prompt = f"""
    {user_input}

    قم بتحليل هذا المشروع وتحديد الجمهور المستهدف للمنصات المطلوبة في الأعلى. يجب أن تشمل المخرجات تقسيم الجمهور حسب الفئة العمرية، الدخل، الموقع الجغرافي، والاهتمامات. أيضًا، يجب أن تشمل الاستراتيجيات الإعلانية الموصى بها لكل منصة مع نوع الإعلانات الأنسب.

    تأكد من تقديم النتائج في صيغة JSON مع الحفاظ على هذا الترتيب:
    1. فيسبوك: الفئة العمرية، الدخل، الموقع الجغرافي، الاهتمامات، السلوك، نوع الإعلانات، الأهداف.
    2. إنستغرام: الفئة العمرية، الدخل، الاهتمامات، السلوك، نوع الإعلانات، الأهداف.
    3. لينكد إن: الفئة المستهدفة، الدخل، الاهتمامات، نوع الإعلانات، الأهداف.
    4. جوجل: الكلمات المفتاحية، نوع الإعلانات، الأهداف.
    """

    system_prompt = f""" أنت أفضل media buyer متخصص. يجب عليك أن تلبي إحتياجات العميل على أكمل وجه ممكن."""

    context = [{"role": "system", "content": system_prompt},{"role": "user", "content": user_prompt}]
    response = ''
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=context,
            max_tokens=16384,
            response_format={"type": "json_object"},
        )

        # Fetching the response assuming it is structured as instructed
        response = chat_completion.choices[0].message.content
        print("Raw AI response:", response)

        # Attempt to parse the response to ensure it is valid JSON
        parsed_ai_response = json.loads(response)
        print("Parsed AI response:", parsed_ai_response)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return response

# وظيفة لتنظيم المخرجات في صيغة JSON
def organize_campaign_output(project_name, location, platforms, assets, insights):
    output = {
        "project_name": project_name,
        "location": location,
        "platforms": platforms,
        "assets": assets,
        "insights": json.loads(insights)
    }
    return json.dumps(output, ensure_ascii=False, indent=4)

# البيانات الخاصة بالمشروع
# project_name = "شقق النخبة الفاخرة"
# location = "الرياض، المملكة العربية السعودية"
# platforms = ["فيسبوك", "إنستغرام", "لينكد إن", "جوجل"]
# assets = {
#     "عدد غرف النوم": 4,
#     "عدد غرف المعيشة": 2,
#     "المساحة": "250 متر مربع",
#     "المزايا الفاخرة": ["مسبح خاص", "نادي رياضي مجهز", "مواد بناء عالية الجودة", "أمن وحراسة 24/7", "قريبة من المدارس الدولية والمراكز التجارية", "إطلالة بانورامية على المدينة"]
# }
#
# # الحصول على المخرجات من OpenAI
# insights = generate_real_estate_campaign(project_name, location, platforms, assets)
#
# # تنظيم المخرجات في صيغة JSON
# campaign_output = organize_campaign_output(project_name, location, platforms, assets, insights)
#
# print(campaign_output)
