import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import time
import concurrent.futures
from collections import OrderedDict
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# وظيفة لتحليل المشروع العقاري وتوليد الاستراتيجيات الإعلانية
def generate_real_estate_campaign(user_input):
    user_prompt = f"""
    {user_input}

    قم بتحليل هذا المشروع وتحديد الجمهور المستهدف لجميع المنصات. يجب أن تشمل المخرجات تقسيم الجمهور حسب الفئة العمرية، الدخل، الموقع الجغرافي، والاهتمامات. أيضًا، يجب أن تشمل الاستراتيجيات الإعلانية الموصى بها لكل منصة مع نوع الإعلانات الأنسب.

    استناداً إلى البيانات الحالية للسوق لكل منصة إعلانية (فيسبوك، إنستغرام، لينكد إن، جوجل، تويتر)، قم بإعداد دراسة كاملة تشمل ما يلي:
    1. استراتيجية السوق لكل منصة بناءً على البيانات الحالية(Market_Strategy):
        - فيسبوك: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
        - إنستغرام: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
        - لينكد إن: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
        - جوجل: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
        - تويتر: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).

    2. مؤشرات الأداء الرئيسية (KPIs) المتوقعة بناءً على الاتجاهات الحالية لكل منصة(Performance_Metrics).
    3. التكلفة التسويقية السنوية المتوقعة بناءً على بيانات السوق الحالية(ROI_Calculation).
         - قانون حساب نسبة العائد على الاستثمار (ROI): 
        \[
        \text{{ROI}} = \left( \frac{{\text{{صافي الربح}}}}{{\text{{تكلفة التسويق}}}} \right) \times 100
        \]
        - تأكد من حساب ROI وفقًا لهذا القانون مع إضافة علامة "%" في النهاية.
    4. رؤى استراتيجية بناءً على السوق الحالي، تشمل الفرص والمخاطر(Strategic_Insights).
    5. التوصيات لتحسين الأداء الإعلاني بناءً على ظروف السوق الحالية(Recommendations).
    6. التكرار الأسبوعي الموصى به للمنشورات على كل منصة بناءً على الاتجاهات الحالية(Post_Frequency).

    تأكد من تقديم النتائج في صيغة JSON مع الحفاظ على هذا الترتيب:
    1. فيسبوك: الفئة_العمرية، الدخل، الموقع_الجغرافي، الاهتمامات، السلوك، نوع_الإعلانات، الأهداف.
    2. إنستغرام: الفئة_العمرية، الدخل، الاهتمامات، السلوك، نوع_الإعلانات، الأهداف.
    3. لينكد_إن: الفئة_المستهدفة، الدخل، الاهتمامات، نوع_الإعلانات، الأهداف.
    4. تويتر: الفئة العمرية، الدخل، الاهتمامات، السلوك، نوع الإعلانات، الأهداف.
    5. جوجل: الكلمات_المفتاحية، نوع_الإعلانات، الأهداف.
    6.Market_Strategy.
    7.Performance_Metrics.
    8.ROI_Calculations.
    9.Strategic_Insights.
    10.Recommendations.
    11.Post_Frequency.

    json format:
    {"""
        {
           "Target_Audience": {
              "فيسبوك": {
                 "الفئة_العمرية": "",
                 "الدخل": "",
                 "الموقع_الجغرافي": "",
                 "الاهتمامات": [],
                 "السلوك": [],
                 "نوع_الإعلانات": [],
                 "الأهداف": []
              },
              "إنستغرام": {
                 "الفئة_العمرية": "",
                 "الدخل": "",
                 "الاهتمامات": [],
                 "السلوك": [],
                 "نوع_الإعلانات": [],
                 "الأهداف": []
              },
              "لينكد_إن": {
                 "الفئة_المستهدفة": "",
                 "الدخل": "",
                 "الاهتمامات": [],
                 "نوع_الإعلانات": [],
                 "الأهداف": []
              },
              "تويتر": {
                 "الفئة العمرية": "",
                 "الدخل": "",
                 "الاهتمامات": [],
                 "السلوك": [],
                 "نوع الإعلانات": [],
                 "الأهداف": []
              },
              "جوجل": {
                 "الكلمات_المفتاحية": [],
                 "نوع_الإعلانات": [],
                 "الأهداف": []
              }
           },
           "Market_Strategy": {
                "فيسبوك": {
                    "استراتيجية السوق": "",
                    "التوصيات": "",
                    "النقرات اليومية": "100",
                    "نسبة النقر (CTR)": "0.02",
                    "نسبة التحويل (conversion_rate)": "0.01",
                    "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
                    "التكلفة السنوية": ""
                },
                "إنستغرام": {
                    "استراتيجية السوق": "",
                    "التوصيات": "",
                    "النقرات اليومية": "80",
                    "نسبة النقر (CTR)": "0.03",
                    "نسبة التحويل (conversion_rate)": "0.015",
                    "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
                    "التكلفة السنوية": "",
                },
                "لينكد_إن": {
                    "استراتيجية السوق": "",
                    "التوصيات": "",
                    "النقرات اليومية": "50",
                    "نسبة النقر (CTR)": "0.015",
                    "نسبة التحويل (conversion_rate)": "0.02",
                    "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
                    "التكلفة السنوية": "",
                },
                "تويتر": {
                    "استراتيجية السوق": "",
                    "التوصيات": "",
                    "النقرات اليومية": "70",
                    "نسبة النقر (CTR)": "0.025",
                    "نسبة التحويل (conversion_rate)": "0.01",
                    "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
                    "التكلفة السنوية": "",
                },
                "جوجل": {
                    "استراتيجية السوق": "",
                    "التوصيات": "",
                    "النقرات اليومية": "90",
                    "نسبة النقر (CTR)": "0.04",
                    "نسبة التحويل (conversion_rate)": "0.02",
                    "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
                    "التكلفة السنوية": "",
              }
           },
           "Performance_Metrics": {
              "فيسبوك": ["نسبة التفاعل", "نسبة النقر"],
              "إنستغرام": ["عدد المتابعين", "نسبة التفاعل"],
              "لينكد_إن": ["عدد المشاهدات", "عدد المحادثات"],
              "تويتر": ["عدد الإشارات", "نسبة التفاعل"],
              "جوجل": ["عدد الزيارات", "عدد التفاعل"]
           },
           "ROI_Calculation": {
                "فيسبوك": {
                    "إسقاط_عدد_الزوار_السنوي": "",
                    "إسقاط_عدد_المبيعات_السنوي": "",
                    "إسقاط_الإيرادات_السنوية": "",
                    "تكلفة_التسويق_السنوية": "",
                    "صافي_الربح": "",
                    "نسبة_العائد_على_الاستثمار": ""
                },
                "إنستغرام": {
                    "إسقاط_عدد_الزوار_السنوي": "",
                    "إسقاط_عدد_المبيعات_السنوي": "",
                    "إسقاط_الإيرادات_السنوية": "",
                    "تكلفة_التسويق_السنوية": "",
                    "صافي_الربح": "",
                    "نسبة_العائد_على_الاستثمار": ""
                },
                "لينكد_إن": {
                    "إسقاط_عدد_الزوار_السنوي": "",
                    "إسقاط_عدد_المبيعات_السنوي": "",
                    "إسقاط_الإيرادات_السنوية": "",
                    "تكلفة_التسويق_السنوية": "",
                    "صافي_الربح": "",
                    "نسبة_العائد_على_الاستثمار": ""
                },
                "تويتر": {
                    "إسقاط_عدد_الزوار_السنوي": "",
                    "إسقاط_عدد_المبيعات_السنوي": "",
                    "إسقاط_الإيرادات_السنوية": "",
                    "تكلفة_التسويق_السنوية": "",
                    "صافي_الربح": "",
                    "نسبة_العائد_على_الاستثمار": ""
                },
                "جوجل": {
                    "إسقاط_عدد_الزوار_السنوي": "",
                    "إسقاط_عدد_المبيعات_السنوي": "",
                    "إسقاط_الإيرادات_السنوية": "",
                    "تكلفة_التسويق_السنوية": "",
                    "صافي_الربح": "",
                    "نسبة_العائد_على_الاستثمار": ""
                }
            },
           "Strategic_Insights": {
              "الفرص": "",
              "المخاطر": ""
           },
           "Recommendations": {
              "تحسين الإعلانات": "",
              "زيادة التفاعل": "",
              "استهداف دقيق": ""
           },
           "Post_Frequency": {
              "فيسبوك": "",
              "إنستغرام": "",
              "لينكد_إن": "",
              "تويتر": "",
              "جوجل": ""
           }
        }

    """}
    إرشادات: 
    أعطني فقط البيانات بدون اسم المشروع او أي شئ آخر .. فقط اتبع الترتيب بالأعلى و اعجلها لجميع المنصات """

    system_prompt = f""" أنت أفضل media buyer متخصص. يجب عليك أن تلبي إحتياجات العميل على أكمل وجه ممكن."""

    context = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    parsed_ai_response = ''
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

    return parsed_ai_response


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

# Define prompt templates at the top of the file, after the imports
your_detailed_prompt = """
قم بتحديد:
- الفئات المستهدفة لكل منصة
- الاهتمامات والسلوكيات
- الخصائص الديموغرافية
- أوقات النشاط المثالية
- الكلمات المفتاحية المقترحة
"""

market_strategy_prompt = """
قم بتحديد:
- الرسائل الإعلانية الرئيسية
- نوع المحتوى المناسب
- الميزانية المقترحة
- الجدول الزمني للحملة
"""

roi_calculation_prompt = """
قم بتحليل:
- التكلفة المتوقعة لكل منصة
- العائد المتوقع
- معدل التحويل المتوقع
- فترة استرداد رأس المال
"""


@dataclass
class ContentIdea:
    """Structured representation of a content idea"""
    id: str
    platform: str
    content: str
    progression_hint: str
    metadata: Dict[str, Any] = None

@dataclass
class GeneratedPost:
    """Structured representation of a generated social media post"""
    id: str
    title: str
    platform: str
    original_idea: str
    post_content: str
    progression_hint: str
    post_length: str
    metadata: Dict[str, Any] = None

class ContentGenerationError(Exception):
    """Custom exception for content generation errors"""
    pass
    def generate_content_ideas(
            self,
            platform: str,
            case_study: str,
            campaign_type: str,
            num_ideas: int = 5,
    ) -> List[ContentIdea]:
        """
        Generate interconnected content ideas for a specific platform

        :param platform: Social media platform
        :param case_study: Project details
        :param campaign_type: The campaign type
        :param num_ideas: Number of ideas to generate
        :return: List of content ideas
        """
        self.validate_platform(platform)

        try:
            prompt_method = self.supported_platforms[platform.lower()]['idea_prompt']
            prompt = prompt_method(case_study, num_ideas)

            system_prompt = f"You are a professional real estate marketing expert. Generate exactly {num_ideas} content ideas with a narrative sequence for the {campaign_type} campaign type."
            response = self._generate_ai_response(system_prompt, prompt)

            ideas = []
            for idx, idea_section in enumerate(response.split('\n\n'), 1):
                if idea_section.strip() and len(ideas) < num_ideas:
                    ideas.append(ContentIdea(
                        id=f"{platform}_idea_{idx}",
                        platform=platform,
                        content=idea_section.strip(),
                        progression_hint=f"Step {idx} of the story"
                    ))

            return ideas

        except Exception as e:
            logger.error(f"Error generating ideas for {platform}: {e}")
            raise ContentGenerationError(f"Failed to generate content ideas: {e}")

class ContentGenerator:

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.post_length_config = {
            "short": {
                "min_chars": 50,
                "max_chars": 150,
                "description": "short"
            },
            "medium": {
                "min_chars": 151,
                "max_chars": 300,
                "description": "medium"
            },
            "long": {
                "min_chars": 301,
                "max_chars": 500,
                "description": "long"
            }
        }
        self.supported_platforms = {
            "instagram": {
                "idea_prompt": self._get_instagram_idea_prompt,
                "post_prompt": self._get_instagram_post_prompt
            },
            "facebook": {
                "idea_prompt": self._get_facebook_idea_prompt,
                "post_prompt": self._get_facebook_post_prompt
            },
            "twitter": {
                "idea_prompt": self._get_twitter_idea_prompt,
                "post_prompt": self._get_twitter_post_prompt
            },
            "linkedin": {
                "idea_prompt": self._get_linkedin_idea_prompt,
                "post_prompt": self._get_linkedin_post_prompt
            }
        }

    def validate_platform(self, platform: str):
        if platform.lower() not in self.supported_platforms:
            supported = ", ".join(self.supported_platforms.keys())
            raise ValueError(f"Unsupported platform. Supported platforms: {supported}")


    def generate_content_ideas(
            self,
            platform: str,
            case_study: str,
            campaign_type: str,
            num_ideas: int = 5
    ) -> List[ContentIdea]:
        """
        Generate interconnected content ideas for a specific platform

        :param platform: Social media platform
        :param case_study: Project details
        :param num_ideas: Number of ideas to generate
        :return: List of content ideas
        """
        self.validate_platform(platform)

        try:
            prompt_method = self.supported_platforms[platform.lower()]['idea_prompt']
            prompt = prompt_method(case_study, num_ideas)

            system_prompt = f"You are a professional real estate marketing expert. Generate exactly {num_ideas} content ideas with a narrative sequence for the {campaign_type} campaign type."
            response = self._generate_ai_response(system_prompt, prompt)

            ideas = []
            for idx, idea_section in enumerate(response.split('\n\n'), 1):
                if idea_section.strip() and len(ideas) < num_ideas:
                    ideas.append(ContentIdea(
                        id=f"{platform}_idea_{idx}",
                        platform=platform,
                        content=idea_section.strip(),
                        progression_hint=f"Step {idx} of the story"
                    ))

            return ideas

        except Exception as e:
            logger.error(f"Error generating ideas for {platform}: {e}")
            raise ContentGenerationError(f"Failed to generate content ideas: {e}")
    def generate_posts_for_ideas(self, platform: str, ideas: List[ContentIdea], case_study: str, post_length: str = "medium") -> List[GeneratedPost]:
        self.validate_platform(platform)
        if post_length not in self.post_length_config:
            raise ValueError(f"Invalid post length. Supported lengths: {', '.join(self.post_length_config.keys())}")
        posts = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_idea = {executor.submit(self._generate_post_for_single_idea, platform, idea, case_study, post_length): idea for idea in ideas}
            for future in as_completed(future_to_idea):
                try:
                    post = future.result()
                    posts.append(post)
                except Exception as e:
                    logger.error(f"Error generating post: {e}")
        return posts

    def _generate_post_for_single_idea(self, platform: str, idea: ContentIdea, case_study: str, post_length: str = "medium") -> GeneratedPost:
        try:
            prompt_method = self.supported_platforms[platform.lower()]['post_prompt']
            length_config = self.post_length_config[post_length]
            prompt = prompt_method(case_study, idea.content, length_config["min_chars"], length_config["max_chars"])
            system_prompt = f"""You are a professional real estate marketing expert specialized in creating targeted content.
            Generate content between {length_config["min_chars"]} and {length_config["max_chars"]} characters.
            Do not use any emojis in the content."""
            post_content = self._generate_ai_response(system_prompt, prompt)

            system_prompt_for_title = f"""You are a professional real estate marketing expert specialized in creating targeted content.
                        Generate a very short tite for the provided user prompt.
                        Do not use any emojis in the content."""
            post_title = self._generate_ai_response(system_prompt_for_title, post_content)
            return GeneratedPost(
                id=idea.id,
                title= post_title,
                platform=platform,
                original_idea=idea.content,
                post_content=post_content,
                progression_hint=idea.progression_hint,
                post_length=post_length
            )
        except Exception as e:
            logger.error(f"Error generating post for idea {idea.id}: {e}")
            raise ContentGenerationError(f"Failed to generate post: {e}")

    def _generate_ai_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generate AI response using the new OpenAI API format"""
        try:
            response = client.chat.completions.create(  # Using the client instance directly
                model="gpt-4o-mini-2024-07-18",  # Updated model name
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error in AI response generation: {e}")
            raise ContentGenerationError(f"Failed to generate content: {e}")

    def _get_instagram_idea_prompt(self, case_study: str, number_of_ideas: int) -> str:
        return f"""أنت مختص في التسويق العقاري على الانستجرام.
        قم بإنشاء {number_of_ideas} أفكار إبداعية لمنشورات محتملة مع مراعاة:

        معلومات المشروع:
        {case_study}

        لكل فكرة يرجى تحديد:
        - الهدف التسويقي
        - النقاط الرئيسية للمحتوى
        - نوع المحتوى (صورة، كاروسيل، فيديو قصير)
        - الهاشتاجات المقترحة
        """

    def _get_instagram_post_prompt(self, case_study: str, idea_content: str, min_chars: int, max_chars: int) -> str:
        return f"""أنت مختص في التسويق العقاري على الانستجرام.
        قم بإنشاء منشور بناءً على الفكرة التالية:

        معلومات المشروع:
        {case_study}

        الفكرة:
        {idea_content}

        قواعد إنشاء المحتوى:
        - الطول: بين {min_chars} و {max_chars} حرف
        - الارتباط الوثيق بتفاصيل المشروع
        - هاشتاجات متخصصة
        - دعوة للعمل
        - التركيز على القيمة المضافة
        - عدم استخدام الايموجي
        """

    def _get_facebook_idea_prompt(self, case_study: str, number_of_ideas: int) -> str:
        return f"""أنت مسؤول التسويق لمشروع عقاري على فيسبوك.
        أنشئ {number_of_ideas} أفكار متسلسلة ومكملة للمحتوى.

        معلومات المشروع:
        {case_study}

        لكل فكرة يرجى تحديد:
        - محور المنشور الرئيسي
        - النقاط المميزة للتركيز
        - استراتيجية التفاعل
        - الهاشتاجات المناسبة
        """

    def _get_facebook_post_prompt(self, case_study: str, idea_content: str, min_chars: int, max_chars: int) -> str:
        return f"""أنت مسؤول التسويق لمشروع عقاري على فيسبوك.
        قم بإنشاء منشور بناءً على الفكرة التالية:

        معلومات المشروع:
        {case_study}

        الفكرة:
        {idea_content}

        قواعد مهمة:
        - الطول: بين {min_chars} و {max_chars} حرف
        - ربط المنشور بالمشروع
        - هاشتاجات متسقة
        - دعوة للتفاعل
        - إبراز المميزات
        - عدم استخدام الايموجي
        """

    def _get_twitter_idea_prompt(self, case_study: str, number_of_ideas: int) -> str:
        return f"""أنت خبير التسويق الرقمي على تويتر.
        قم بتوليد {number_of_ideas} أفكار للتغريدات المترابطة.

        معلومات المشروع:
        {case_study}

        لكل فكرة يرجى تحديد:
        - الرسالة الرئيسية
        - النقاط المحورية
        - استراتيجية الاختصار
        - الهاشتاجات المقترحة
        """

    def _get_twitter_post_prompt(self, case_study: str, idea_content: str, min_chars: int, max_chars: int) -> str:
        return f"""أنت خبير التسويق الرقمي على تويتر.
        قم بإنشاء تغريدة بناءً على الفكرة التالية:

        معلومات المشروع:
        {case_study}

        الفكرة:
        {idea_content}

        قواعد مهمة:
        - الطول: بين {min_chars} و {max_chars} حرف
        - لغة موجزة وواضحة
        - إظهار القيمة المميزة
        - هاشتاجات مختصرة
        - إضافة رابط للتواصل
        - عدم استخدام الايموجي
        """

    def _get_linkedin_idea_prompt(self, case_study: str, number_of_ideas: int) -> str:
        return f"""أنت مستشار التسويق العقاري على لينكد إن.
        أنشئ {number_of_ideas} أفكار للمنشورات الاحترافية.

        معلومات المشروع:
        {case_study}

        لكل فكرة يرجى تحديد:
        - البعد الاستثماري
        - النقاط التحليلية
        - الأدلة والإحصائيات
        - التركيز المهني
        """

    def _get_linkedin_post_prompt(self, case_study: str, idea_content: str, min_chars: int, max_chars: int) -> str:
        return f"""أنت مستشار التسويق العقاري على لينكد إن.
        قم بإنشاء منشور احترافي بناءً على الفكرة التالية:

        معلومات المشروع:
        {case_study}

        الفكرة:
        {idea_content}

        قواعد مهمة:
        - الطول: بين {min_chars} و {max_chars} حرف
        - لغة مهنية واحترافية
        - التركيز على القيمة الاستثمارية
        - معلومات دقيقة ومفصلة
        - لغة مقنعة للمستثمرين
        - إضافة معلومات سوقية
        - عدم استخدام الايموجي
        """

def clean_and_parse_json(response_text):
    """Clean the response and ensure it's valid JSON"""
    try:
        # Remove any potential prefixes or suffixes
        text = response_text.strip()
        # Find the first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            text = text[start:end]
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Original response: {response_text}")
        print(f"JSON Error: {str(e)}")
        raise

def create_platform_targeting(project_details):
    """Generate platform-specific targeting strategy"""
    user_prompt = f"""Based on these project details:
    {json.dumps(project_details, ensure_ascii=False)}
    
    Generate a detailed targeting strategy. Return ONLY valid JSON with this structure:
    {{
        "Target_Audience": {{
            "فيسبوك": {{
                "الفئة_العمرية": "25-40",
                "الدخل": "5000-15000 ريال سعودي شهرياً",
                "الموقع_الجغرافي": "",
                "الاهتمامات": [],
                "السلوك": [],
                "نوع_الإعلانات": [],
                "الأهداف": []
            }},
            "إنستغرام": {{ ... }},
            "لينكد_إن": {{ ... }},
            "تويتر": {{ ... }},
            "جوجل": {{ ... }}
        }}
    }}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a digital marketing expert. Respond only with valid JSON."},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return clean_and_parse_json(response.choices[0].message.content)
    except Exception as e:
        print(f"Error in create_platform_targeting: {str(e)}")
        raise

def generate_market_strategy(project_details):
    """Generate detailed market strategy with realistic metrics using ordered dictionaries"""
    user_prompt = f"""Based on these project details:
    {json.dumps(project_details, ensure_ascii=False)}

    Generate a comprehensive marketing strategy with realistic metrics. Return ONLY valid JSON with this structure:
    {{
        "Market_Strategy": {{
            "فيسبوك": {{
                "استراتيجية السوق": "",
                "التوصيات": "",
                "النقرات اليومية": "",
                "نسبة النقر (CTR)": "",
                "نسبة التحويل (conversion_rate)": "",
                "تكلفة التسويق الشهرية": "",
                "التكلفة السنوية": ""
            }},
            "إنستغرام": {{ ... }},
            "لينكد_إن": {{ ... }},
            "تويتر": {{ ... }},
            "جوجل": {{ ... }}
        }},
        "Performance_Metrics": {{
            "فيسبوك": [
                "معدل النقر (1-3%)",
                "معدل التحويل (0.5-2%)",
                "متوسط تكلفة النقرة (2-5 ريال)",
                "معدل التفاعل (2-5%)",
                "عدد المشاهدات الشهرية"
            ],
            "إنستغرام": [
                "معدل المشاركة (2-4%)",
                "معدل الوصول (20-30%)",
                "معدل حفظ المنشورات (1-3%)",
                "معدل زيارة الملف الشخصي (5-10%)",
                "معدل التحويل (0.5-2%)"
            ],
            "لينكد_إن": [
                "معدل النقر (1-2%)",
                "معدل التفاعل المهني (2-4%)",
                "معدل الاستفسارات (3-5%)",
                "جودة العملاء المحتملين",
                "معدل التحويل للمستثمرين (1-3%)"
            ],
            "تويتر": [
                "معدل إعادة التغريد (1-3%)",
                "معدل التفاعل (2-4%)",
                "معدل النقر (1-2%)",
                "معدل الوصول",
                "معدل التحويل (0.3-1%)"
            ],
            "جوجل": [
                "معدل النقر (2-5%)",
                "تكلفة النقرة",
                "معدل التحويل (1-3%)",
                "جودة الزيارات",
                "مدة مشاهدة الصفحة"
            ]
        }},
        "Post_Frequency": {{
            "فيسبوك": "",
            "إنستغرام": "",
            "لينكد_إن": "",
            "تويتر": "",
            "جوجل": ""
        }}
    }}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a marketing strategist. Provide realistic marketing metrics based on real estate industry standards."},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return clean_and_parse_json(response.choices[0].message.content)
    except Exception as e:
        print(f"Error in generate_market_strategy: {str(e)}")
        raise

def calculate_roi_projections(project_details):
    """Calculate realistic ROI projections"""
    # Get assets from project details
    assets = project_details.get('assets', [])

    # Ensure there are assets provided
    if not assets:
        raise ValueError("No assets provided in project details.")

    # Calculate total property price by summing up (price * units) for all assets
    total_property_price = sum(
        float(asset.get('price', 0)) * int(asset.get('units', 1))
        for asset in assets
    )

    # Calculate maximum marketing budget (1% of total property value)
    max_marketing_budget = total_property_price * 0.01

    # Define platforms with their English keys to avoid encoding issues
    platforms = {
        "facebook": "فيسبوك",
        "instagram": "انستغرام",
        "twitter": "تويتر",
        "linkedin": "لينكد_إن",
        "google": "جوجل"
    }

    # Calculate platform budgets
    platform_budgets = {
        platforms["facebook"]: max_marketing_budget * 0.25,  # 25% of budget
        platforms["instagram"]: max_marketing_budget * 0.20,  # 20% of budget
        platforms["google"]: max_marketing_budget * 0.25,     # 25% of budget
        platforms["twitter"]: max_marketing_budget * 0.15,    # 15% of budget
        platforms["linkedin"]: max_marketing_budget * 0.15    # 15% of budget
    }

    user_prompt =f"""You are a real estate financial analyst. 
    Provide realistic ROI calculations based on:
    - Total marketing budget is {"{:,}".format(max_marketing_budget)} SAR
    - Total Property prices are {"{:,}".format(total_property_price)}  SAR"""

    print("Prompt: ", user_prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content":f"""Based on these project details:

Generate realistic ROI projections for a real estate marketing campaign with these specific platform budgets:
{platforms["facebook"]}: {platform_budgets[platforms["facebook"]]} SAR
{platforms["instagram"]}: {platform_budgets[platforms["instagram"]]} SAR
{platforms["google"]}: {platform_budgets[platforms["google"]]} SAR
{platforms["twitter"]}: {platform_budgets[platforms["twitter"]]} SAR
{platforms["linkedin"]}: {platform_budgets[platforms["linkedin"]]} SAR

Consider:
1. Average real estate conversion rates (0.5-2%)
2. Marketing costs MUST match the specified budgets
3. Realistic visitor-to-lead ratios
4. Standard real estate sales cycles

Important Notes###:
- Use the exact marketing costs provided for each platform
- Conversion rates should be 0.5-2% based on each platform
- Use specific numbers, not ranges
- ROI calculations should reflect realistic market conditions
- All numbers must be separated by "," like: 1,000,000
- All Json Must be Strings only###

Return ONLY valid JSON with this structure and use SPECIFIC NUMBERS (not ranges) using these fake total price and marketing budgets examples:
Total Property Prices: 50,000,000 SAR
Maximum Marketing Budget: 500,000 SAR
{{
    "ROI_Calculation": {{
        "فيسبوك": {{
            "إسقاط_عدد_الزوار_السنوي": "50,000 زائر",
            "معدل_التحويل":"0.5",
            "إسقاط_عدد_المبيعات_السنوي": "50,000 * (0.5 / 100 ) = 25 مشتري",
            "إسقاط_الإيرادات_السنوية": "50,000,000 * 25 = 1,250,000,000 ريال سعودي",
            "تكلفة_التسويق_السنوية": "125,000 ريال سعودي",
            "صافي_الربح": "1,250,000,000 - 125,000 = 1,249,875,000 ريال سعودي",
            "نسبة_العائد_على_الاستثمار": "(1,249,875,000 / 50,000,000) * 100 = 2,499.75%"
        }},
        // Similar structure for other platforms
    }}
}}""" },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )

        print(response.choices[0].message.content)

        result = clean_and_parse_json(response.choices[0].message.content)

        print(result)

        # Validate and fix ROI calculations
        for platform_en, platform_ar in platforms.items():
            if platform_ar not in result["ROI_Calculation"]:
                result["ROI_Calculation"][platform_ar] = {
                    "إسقاط_عدد_الزوار_السنوي": "2000",
                    "إسقاط_عدد_المبيعات_السنوي": "1",
                    "إسقاط_الإيرادات_السنوية": str(int(total_property_price)),
                    "تكلفة_التسويق_السنوية": str(int(platform_budgets[platform_ar])),
                    "صافي_الربح": str(int(total_property_price - platform_budgets[platform_ar])),
                    "نسبة_العائد_على_الاستثمار": str(int((total_property_price - platform_budgets[platform_ar]) / platform_budgets[platform_ar] * 100))
                }

            # platform_cost_str = str(result["ROI_Calculation"][platform_ar]["تكلفة_التسويق_السنوية"]).replace(',', '')
            # platform_cost = float(platform_cost_str)
            #
            # if abs(platform_cost - platform_budgets[platform_ar]) > 1:
            #     result["ROI_Calculation"][platform_ar]["تكلفة_التسويق_السنوية"] = "{:,}".format(int(platform_budgets[platform_ar]))

        return result

    except Exception as e:
        print(f"Error in calculate_roi_projections: {str(e)}")
        raise

# def calculate_project_summary(project_details):
#     """Generate project summary with strictly ordered pros and cons"""
#     user_prompt = f"""Based on these project details:
#     {json.dumps(project_details, ensure_ascii=False)}

#     Generate a project summary. Return ONLY valid JSON with this structure:
#     {{
#         "Case_Study": "وصف تفصيلي للمشروع والموقع",
#             "Pros": {{
#             "1": "ميزة رئيسية أولى",
#             "2": "ميزة رئيسية ثانية",
#             "3": "ميزة رئيسية ثالثة",
#             "4": "ميزة رئيسية رابعة",
#             "5": "ميزة رئيسية خامسة"
#         }},
#             "Cons": {{
#             "1": "تحدي رئيسي أول",
#             "2": "تحدي رئيسي ثاني",
#             "3": "تحدي رئيسي ثالث",
#             "4": "تحدي رئيسي رابع"
#         }},
#         "Strategic_Insights": {{
#             "الفرص": "",
#             "المخاطر": ""
#         }},
#         "Recommendations": {{
#             "تحسين الإعلانات": "",
#             "زيادة التفاعل": "",
#             "استهداف دقيق": ""
#         }}
#     }}"""
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini-2024-07-18",
#             messages=[
#                 {"role": "system", "content": "You are a real estate analyst. Provide detailed project analysis."},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.7
#         )
#         return clean_and_parse_json(response.choices[0].message.content)
#     except Exception as e:
#         print(f"Error in calculate_project_summary: {str(e)}")
#         raise

def calculate_project_summary(project_details):
    """Generate project summary with strictly ordered pros and cons"""
    user_prompt = f"""Based on these project details:
    {json.dumps(project_details, ensure_ascii=False)}

    Generate a project summary. Return ONLY valid JSON with this structure:
    {{
        "Case_Study": "وصف تفصيلي للمشروع والموقع",
        "Pros": {{
            "1": "ميزة رئيسية أولى",
            "2": "ميزة رئيسية ثانية",
            "3": "ميزة رئيسية ثالثة",
            "4": "ميزة رئيسية رابعة",
            "5": "ميزة رئيسية خامسة"
        }},
        "Cons": {{
            "1": "تحدي رئيسي أول",
            "2": "تحدي رئيسي ثاني",
            "3": "تحدي رئيسي ثالث",
            "4": "تحدي رئيسي رابع"
        }},
        "Strategic_Insights": {{
            "الفرص": "",
            "المخاطر": ""
        }},
        "Recommendations": {{
            "تحسين الإعلانات": "",
            "زيادة التفاعل": "",
            "استهداف دقيق": ""
        }}
    }}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a real estate analyst. Provide detailed project analysis."},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        # Parse the response and enforce ordering
        content = response.choices[0].message.content
        parsed_content = json.loads(content)
        
        # Create ordered dictionary with desired key order
        ordered_result = OrderedDict([
            ("Case_Study", parsed_content["Case_Study"]),
            ("Pros", parsed_content["Pros"]),
            ("Cons", parsed_content["Cons"]),
            ("Strategic_Insights", parsed_content["Strategic_Insights"]),
            ("Recommendations", parsed_content["Recommendations"])
        ])
        
        return ordered_result
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        raise ContentGenerationError("Invalid JSON response from AI model")
    except Exception as e:
        print(f"Error in calculate_project_summary: {str(e)}")
        raise ContentGenerationError(f"Failed to generate project summary: {str(e)}")


def social_media_content_ai(project_details_json):
    """Generate social media content plan"""
    try:
        project_details = json.loads(project_details_json) if isinstance(project_details_json, str) else project_details_json
        
        user_prompt = f"""Based on this property description:
        {project_details.get('property_description', '')}
        
        Generate a social media content plan. Return ONLY valid JSON with this structure:
        {{
            "facebook_posts": [],
            "facebook_timing": [],
            "facebook_hashtags": [],
            "instagram_posts": [],
            "instagram_timing": [],
            "instagram_hashtags": [],
            "twitter_posts": [],
            "twitter_timing": [],
            "twitter_hashtags": [],
            "general_tips": [],
            "weekly_schedule": {{
                "الأحد": [],
                "الإثنين": [],
                "الثلاثاء": [],
                "الأربعاء": [],
                "الخميس": [],
                "الجمعة": [],
                "السبت": []
            }}
        }}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a social media expert specializing in real estate marketing."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        return clean_and_parse_json(response.choices[0].message.content)
    except Exception as e:
        print(f"Error in social_media_content_ai: {str(e)}")
        raise

# def generate_social_media_content(project_details: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Generate complete social media content strategy
#
#     :param project_details: Dictionary containing project information
#     :return: Dictionary containing generated content strategy
#     """
#     try:
#         generator = ContentGenerator()
#         results = {}
#
#         for platform in project_details.get('platforms', []):
#             # Generate ideas
#             ideas = generator.generate_content_ideas(
#                 platform=platform,
#                 case_study=json.dumps(project_details, ensure_ascii=False),
#                 num_ideas=3
#             )
#
#             # Generate posts from ideas
#             posts = generator.generate_posts_for_ideas(
#                 platform=platform,
#                 ideas=ideas,
#                 case_study=json.dumps(project_details, ensure_ascii=False),
#                 post_length="medium"
#             )
#
#             results[platform] = {
#                 'ideas': [asdict(idea) for idea in ideas],
#                 'posts': [asdict(post) for post in posts]
#             }
#
#         return {
#             "success": True,
#             "data": results
#         }
#
#     except Exception as e:
#         logger.error(f"Error in content generation: {e}")
#         raise ContentGenerationError(f"Failed to generate social media content: {e}")

# Example usage
if __name__ == "__main__":
    test_data = {
        "project_name": "شقق النخبة الفاخرة",
        "location": "الرياض",
        "platforms": ["فيسبوك", "إنستغرام", "تويتر", "لينكد_إن", "جوجل"],
        "assets": {
            "price": "500000",
            "features": [
                "مسبح خاص",
                "نادي رياضي مجهز",
                "أمن وحراسة 24/7",
                "قريبة من المدارس الدولية"
            ]
        }
    }
    
    debug_full_analysis(test_data) # type: ignore

#=======================================================================================
# import json
# import os
# from openai import OpenAI
# from dotenv import load_dotenv
# import time
# import concurrent.futures
# from collections import OrderedDict

# # Load environment variables
# load_dotenv()

# # Initialize OpenAI client
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# # Define prompt templates at the top of the file, after the imports
# your_detailed_prompt = """
# قم بتحديد:
# - الفئات المستهدفة لكل منصة
# - الاهتمامات والسلوكيات
# - الخصائص الديموغرافية
# - أوقات النشاط المثالية
# - الكلمات المفتاحية المقترحة
# """

# market_strategy_prompt = """
# قم بتحديد:
# - الرسائل الإعلانية الرئيسية
# - نوع المحتوى المناسب
# - الميزانية المقترحة
# - الجدول الزمني للحملة
# """

# roi_calculation_prompt = """
# قم بتحليل:
# - التكلفة المتوقعة لكل منصة
# - العائد المتوقع
# - معدل التحويل المتوقع
# - فترة استرداد رأس المال
# """

# def clean_and_parse_json(response_text):
#     """Clean the response and ensure it's valid JSON"""
#     try:
#         # Remove any potential prefixes or suffixes
#         text = response_text.strip()
#         # Find the first '{' and last '}'
#         start = text.find('{')
#         end = text.rfind('}') + 1
#         if start != -1 and end != 0:
#             text = text[start:end]
#         return json.loads(text)
#     except json.JSONDecodeError as e:
#         print(f"Original response: {response_text}")
#         print(f"JSON Error: {str(e)}")
#         raise

# def create_platform_targeting(project_details):
#     """Generate platform-specific targeting strategy"""
#     user_prompt = f"""Based on these project details:
#     {json.dumps(project_details, ensure_ascii=False)}
    
#     Generate a detailed targeting strategy. Return ONLY valid JSON with this structure:
#     {{
#         "Target_Audience": {{
#             "فيسبوك": {{
#                 "الفئة_العمرية": "25-40",
#                 "الدخل": "5000-15000 ريال سعودي شهرياً",
#                 "الموقع_الجغرافي": "",
#                 "الاهتمامات": [],
#                 "السلوك": [],
#                 "نوع_الإعلانات": [],
#                 "الأهداف": []
#             }},
#             "إنستغرام": {{ ... }},
#             "لينكد_إن": {{ ... }},
#             "تويتر": {{ ... }},
#             "جوجل": {{ ... }}
#         }}
#     }}"""
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini-2024-07-18",
#             messages=[
#                 {"role": "system", "content": "You are a digital marketing expert. Respond only with valid JSON."},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.7
#         )
#         return clean_and_parse_json(response.choices[0].message.content)
#     except Exception as e:
#         print(f"Error in create_platform_targeting: {str(e)}")
#         raise

# def generate_market_strategy(project_details):
#     """Generate detailed market strategy with realistic metrics using ordered dictionaries"""
#     user_prompt = f"""Based on these project details:
#     {json.dumps(project_details, ensure_ascii=False)}

#     Generate a comprehensive marketing strategy with realistic metrics. Return ONLY valid JSON with this structure:
#     {{
#         "Market_Strategy": {{
#             "فيسبوك": {{
#                 "استراتيجية السوق": "",
#                 "التوصيات": "",
#                 "النقرات اليومية": "",
#                 "نسبة النقر (CTR)": "",
#                 "نسبة التح��يل (conversion_rate)": "",
#                 "تكلفة التسويق الشهرية": "",
#                 "التكلفة السنوية": ""
#             }},
#             "إنستغرام": {{ ... }},
#             "لينكد_إن": {{ ... }},
#             "تويتر": {{ ... }},
#             "جوجل": {{ ... }}
#         }},
#         "Performance_Metrics": {{
#             "فيسبوك": [
#                 "معدل النقر (1-3%)",
#                 "معدل التحويل (0.5-2%)",
#                 "متوسط تكلفة النقرة (2-5 ريال)",
#                 "معدل التفاعل (2-5%)",
#                 "عدد المشاهدات الشهرية"
#             ],
#             "إنستغرام": [
#                 "معدل المشاركة (2-4%)",
#                 "معدل الوصول (20-30%)",
#                 "معدل حفظ المنشورات (1-3%)",
#                 "معدل زيارة الملف الشخصي (5-10%)",
#                 "معدل التحويل (0.5-2%)"
#             ],
#             "لينكد_إن": [
#                 "معدل النقر (1-2%)",
#                 "معدل التفاعل المهني (2-4%)",
#                 "معدل الاستفسارات (3-5%)",
#                 "جودة العملاء المحتملين",
#                 "معدل التحويل للمستثمرين (1-3%)"
#             ],
#             "تويتر": [
#                 "معدل إعادة التغريد (1-3%)",
#                 "معدل التفاعل (2-4%)",
#                 "معدل النقر (1-2%)",
#                 "معدل الوصول",
#                 "معدل التحويل (0.3-1%)"
#             ],
#             "جوجل": [
#                 "معدل النقر (2-5%)",
#                 "تكلفة النقرة",
#                 "معدل التحويل (1-3%)",
#                 "جودة الزيارات",
#                 "مدة مشاهدة الصفحة"
#             ]
#         }},
#         "Post_Frequency": {{
#             "فيسبوك": "",
#             "إنستغرام": "",
#             "لينكد_إن": "",
#             "تويتر": "",
#             "جوجل": ""
#         }}
#     }}"""
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini-2024-07-18",
#             messages=[
#                 {"role": "system", "content": "You are a marketing strategist. Provide realistic marketing metrics based on real estate industry standards."},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.7
#         )
#         return clean_and_parse_json(response.choices[0].message.content)
#     except Exception as e:
#         print(f"Error in generate_market_strategy: {str(e)}")
#         raise

# def calculate_roi_projections(project_details):
#     """Calculate realistic ROI projections"""
#     # Get property price for calculations
#     property_price = float(project_details.get('assets', {}).get('price', 500000))
    
#     # Calculate maximum marketing budget (10% of property value)
#     max_marketing_budget = property_price * 0.1
    
#     # Define platforms with their English keys to avoid encoding issues
#     platforms = {
#         "facebook": "فيسبوك",
#         "instagram": "انستغرام",
#         "twitter": "تويتر",
#         "linkedin": "لينكد_إن",
#         "google": "جوجل"
#     }
    
#     # Calculate platform budgets
#     platform_budgets = {
#         platforms["facebook"]: max_marketing_budget * 0.25,  # 25% of budget
#         platforms["instagram"]: max_marketing_budget * 0.20,  # 20% of budget
#         platforms["google"]: max_marketing_budget * 0.25,  # 25% of budget
#         platforms["twitter"]: max_marketing_budget * 0.15,  # 15% of budget
#         platforms["linkedin"]: max_marketing_budget * 0.15   # 15% of budget
#     }

#     user_prompt = f'''Based on these project details:
#     Property Price: {property_price} SAR
#     Maximum Marketing Budget: {max_marketing_budget} SAR
    
#     Generate realistic ROI projections for a real estate marketing campaign with these specific platform budgets:
#     {platforms["facebook"]}: {platform_budgets[platforms["facebook"]]} SAR
#     {platforms["instagram"]}: {platform_budgets[platforms["instagram"]]} SAR
#     {platforms["google"]}: {platform_budgets[platforms["google"]]} SAR
#     {platforms["twitter"]}: {platform_budgets[platforms["twitter"]]} SAR
#     {platforms["linkedin"]}: {platform_budgets[platforms["linkedin"]]} SAR
    
#     Consider:
#     1. Average real estate conversion rates (0.5-2%)
#     2. Marketing costs MUST match the specified budgets
#     3. Realistic visitor-to-lead ratios
#     4. Standard real estate sales cycles
    
#     Return ONLY valid JSON with this structure and use SPECIFIC NUMBERS (not ranges):
#     {{
#         "ROI_Calculation": {{
#             "{platforms["facebook"]}": {{
#                 "إسقاط_عدد_الزوار_السنوي": "3000",
#                 "إسقاط_عدد_المبيعات_السنوي": "2",
#                 "إسقاط_الإيرادات_السنوية": "{property_price * 2}",
#                 "تكلفة_التسويق_السنوية": "{platform_budgets[platforms["facebook"]]}",
#                 "صافي_الربح": "{(property_price * 2) - platform_budgets[platforms["facebook"]]}",
#                 "نسبة_العائد_على_الاستثمار": "150"
#             }},
#             // Similar structure for other platforms
#         }}
#     }} 
#     '''

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini-2024-07-18",
#             messages=[
#                 {"role": "system", "content": f"""You are a real estate financial analyst. 
#                 Provide realistic ROI calculations based on:
#                 - Total marketing budget is {max_marketing_budget} SAR
#                 - Use the exact marketing costs provided for each platform
#                 - Conversion rates should be 0.5-2%
#                 - Use specific numbers, not ranges
#                 - ROI calculations should reflect realistic market conditions
#                 - Property price is {property_price} SAR"""},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.7
#         )

#         result = clean_and_parse_json(response.choices[0].message.content)
        
#         # Validate and fix ROI calculations
#         total_marketing_cost = 0
#         for platform_en, platform_ar in platforms.items():
#             if platform_ar not in result["ROI_Calculation"]:
#                 result["ROI_Calculation"][platform_ar] = {
#                     "إسقاط_عدد_الزوار_السنوي": "2000",
#                     "إسقاط_عدد_المبيعات_السنوي": "1",
#                     "إسقاط_الإيرادات_السنوية": str(int(property_price)),
#                     "تكلفة_التسويق_السنوية": str(int(platform_budgets[platform_ar])),
#                     "صافي_الربح": str(int(property_price - platform_budgets[platform_ar])),
#                     "نسبة_العائد_على_الاستثمار": str(int((property_price - platform_budgets[platform_ar]) / platform_budgets[platform_ar] * 100))
#                 }
            
#             platform_cost = float(''.join(filter(str.isdigit, result["ROI_Calculation"][platform_ar]["تكلفة_التسويق_السنوية"])))
#             if abs(platform_cost - platform_budgets[platform_ar]) > 1:  # Allow for minor rounding differences
#                 result["ROI_Calculation"][platform_ar]["تكلفة_التسويق_السنوية"] = str(int(platform_budgets[platform_ar]))
                
#             total_marketing_cost += platform_budgets[platform_ar]

#         return result

#     except Exception as e:
#         print(f"Error in calculate_roi_projections: {str(e)}")
#         raise

        
# # def calculate_project_summary(project_details):
# #     """Generate project summary with strictly ordered pros and cons"""
# #     user_prompt = f"""Based on these project details:
# #     {json.dumps(project_details, ensure_ascii=False)}

# #     Generate a project summary. Return ONLY valid JSON with this structure:
# #     {{
# #         "Case_Study": "وصف تفصيلي للمشروع والموقع",
# #             "Pros": {{
# #             "1": "ميزة رئيسية أولى",
# #             "2": "ميزة رئيسية ثانية",
# #             "3": "ميزة رئيسية ثالثة",
# #             "4": "ميزة رئيسية رابعة",
# #             "5": "ميزة رئيسية خامسة"
# #         }},
# #             "Cons": {{
# #             "1": "تحدي رئيسي أول",
# #             "2": "تحدي رئيسي ثاني",
# #             "3": "تحدي رئيسي ثالث",
# #             "4": "تحدي رئيسي رابع"
# #         }},
# #         "Strategic_Insights": {{
# #             "الفرص": "",
# #             "المخاطر": ""
# #         }},
# #         "Recommendations": {{
# #             "تحسين الإعلانات": "",
# #             "زيادة التفاعل": "",
# #             "استهداف دقيق": ""
# #         }}
# #     }}"""
    
# #     try:
# #         response = client.chat.completions.create(
# #             model="gpt-4o-mini-2024-07-18",
# #             messages=[
# #                 {"role": "system", "content": "You are a real estate analyst. Provide detailed project analysis."},
# #                 {"role": "user", "content": user_prompt}
# #             ],
# #             temperature=0.7
# #         )
# #         return clean_and_parse_json(response.choices[0].message.content)
# #     except Exception as e:
# #         print(f"Error in calculate_project_summary: {str(e)}")
# #         raise

# def calculate_project_summary(project_details):
#     """Generate project summary with strictly ordered pros and cons"""
#     user_prompt = f"""Based on these project details:
#     {json.dumps(project_details, ensure_ascii=False)}

#     Generate a project summary. Return ONLY valid JSON with this structure:
#     {{
#         "Case_Study": "وصف تفصيلي للمشروع والموقع",
#         "Pros": {{
#             "1": "ميزة رئيسية أولى",
#             "2": "ميزة رئيسية ثانية",
#             "3": "ميزة رئيسية ثالثة",
#             "4": "ميزة رئيسية رابعة",
#             "5": "ميزة رئيسية خامسة"
#         }},
#         "Cons": {{
#             "1": "تحدي رئيسي أول",
#             "2": "تحدي رئيسي ثاني",
#             "3": "تحدي رئيسي ثالث",
#             "4": "تحدي رئيسي رابع"
#         }},
#         "Strategic_Insights": {{
#             "الفرص": "",
#             "المخاطر": ""
#         }},
#         "Recommendations": {{
#             "تحسين الإعلانات": "",
#             "زيادة التفاعل": "",
#             "استهداف دقيق": ""
#         }}
#     }}"""
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o-mini-2024-07-18",
#             messages=[
#                 {"role": "system", "content": "You are a real estate analyst. Provide detailed project analysis."},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.7
#         )
        
#         # Parse the response and enforce ordering
#         content = response.choices[0].message.content
#         parsed_content = json.loads(content)
        
#         # Create ordered dictionary with desired key order
#         ordered_result = OrderedDict([
#             ("Case_Study", parsed_content["Case_Study"]),
#             ("Pros", parsed_content["Pros"]),
#             ("Cons", parsed_content["Cons"]),
#             ("Strategic_Insights", parsed_content["Strategic_Insights"]),
#             ("Recommendations", parsed_content["Recommendations"])
#         ])
        
#         return ordered_result
#     except Exception as e:
#         print(f"Error in calculate_project_summary: {str(e)}")
#         raise


# def social_media_content_ai(project_details_json):
#     """Generate social media content plan"""
#     try:
#         project_details = json.loads(project_details_json) if isinstance(project_details_json, str) else project_details_json
        
#         user_prompt = f"""Based on this property description:
#         {project_details.get('property_description', '')}
        
#         Generate a social media content plan. Return ONLY valid JSON with this structure:
#         {{
#             "facebook_posts": [],
#             "facebook_timing": [],
#             "facebook_hashtags": [],
#             "instagram_posts": [],
#             "instagram_timing": [],
#             "instagram_hashtags": [],
#             "twitter_posts": [],
#             "twitter_timing": [],
#             "twitter_hashtags": [],
#             "general_tips": [],
#             "weekly_schedule": {{
#                 "الأحد": [],
#                 "الإثنين": [],
#                 "الثلاثاء": [],
#                 "الأربعاء": [],
#                 "الخميس": [],
#                 "الجمعة": [],
#                 "السبت": []
#             }}
#         }}"""

#         response = client.chat.completions.create(
#             model="gpt-4o-mini-2024-07-18",
#             messages=[
#                 {"role": "system", "content": "You are a social media expert specializing in real estate marketing."},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.7
#         )
        
#         return clean_and_parse_json(response.choices[0].message.content)
#     except Exception as e:
#         print(f"Error in social_media_content_ai: {str(e)}")
#         raise

# # Example usage
# if __name__ == "__main__":
#     test_data = {
#         "project_name": "شقق النخبة الفاخرة",
#         "location": "الرياض",
#         "platforms": ["فيسبوك", "إنستغرام", "تويتر", "لينكد_إن", "جوجل"],
#         "assets": {
#             "price": "500000",
#             "features": [
#                 "مسبح خاص",
#                 "نادي رياضي مجهز",
#                 "أمن وحراسة 24/7",
#                 "قريبة من المدارس الدولية"
#             ]
#         }
#     }
    
#     debug_full_analysis(test_data) # type: ignore




##===================================================================
# import json
# from openai import OpenAI
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# # Access the API key
# api_key = os.getenv('OPENAI_API_KEY')

# client = OpenAI(api_key=api_key)

# # وظيفة لتحليل المشروع العقاري وتوليد الاستراتيجيات الإعلانية
# def generate_real_estate_campaign(user_input):
#     user_prompt = f"""
#     {user_input}

#     قم بتحليل هذا المشروع وتحديد الجمهور المستهدف لجميع المنصات. يجب أن تشمل المخرجات تقسيم الجمهور حسب الفئة العمرية، الدخل، الموقع الجغرافي، والاهتمامات. أيضًا، يجب أن تشمل الاستراتيجيات الإعلانية الموصى بها لكل منصة مع نوع الإعلانات الأنسب.
    
#     استناداً إلى البيانات الحالية للسوق لكل منصة إعلانية (فيسبوك، إنستغرام، لينكد إن، جوجل، تويتر)، قم بإعداد دراسة كاملة تشمل ما يلي:
#     1. استراتيجية السوق لكل منصة بناءً على البيانات الحالية(Market_Strategy):
#         - فيسبوك: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
#         - إنستغرام: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
#         - لينكد إن: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
#         - جوجل: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
#         - تويتر: استراتيجية السوق، مؤشرات الأداء، التكلفة السنوية، الرؤى، التوصيات، التكرار الأسبوعي، النقرات اليومية (daily_clicks)، نسبة النقر (CTR)، نسبة التحويل (conversion_rate)، تكلفة التسويق (marketing_cost).
        
#     2. مؤشرات الأداء الرئيسية (KPIs) المتوقعة بناءً على الاتجاهات الحالية لكل منصة(Performance_Metrics).
#     3. التكلفة التسويقية السنوية المتوقعة بناءً على بيانات السوق الحالية(ROI_Calculation).
#          - قانون حساب نسبة العائد على الاستثمار (ROI): 
#         \[
#         \text{{ROI}} = \left( \frac{{\text{{صافي الربح}}}}{{\text{{تكلفة التسويق}}}} \right) \times 100
#         \]
#         - تأكد من حساب ROI وفقًا لهذا القانون مع إضافة علامة "%" في النهاية.
#     4. رؤى استراتيجية بناءً على السوق الحالي، تشمل الفرص والمخاطر(Strategic_Insights).
#     5. التوصيات لتحسين الأداء الإعلاني بناءً على ظروف السوق الحالية(Recommendations).
#     6. التكرار الأسبوعي الموصى به للمنشورات على كل منصة بناءً على الاتجاهات الحالية(Post_Frequency).

#     تأكد من تقديم النتائج في صيغة JSON مع الحفاظ على هذا الترتيب:
#     1. فيسبوك: الفئة_العمرية، الدخل، الموقع_الجغرافي، الاهتمامات، السلوك، نوع_الإعلانات، الأهداف.
#     2. إنستغرام: الفئة_العمرية، الدخل، الاهتمامات، السلوك، نوع_الإعلانات، الأهداف.
#     3. لينكد_إن: الفئة_المستهدفة، الدخل، الاهتمامات، نوع_الإعلانات، الأهداف.
#     4. تويتر: الفئة العمرية، الدخل، الاهتمامات، السلوك، نوع الإعلانات، الأهداف.
#     5. جوجل: الكلمات_المفتاحية، نوع_الإعلانات، الأهداف.
#     6.Market_Strategy.
#     7.Performance_Metrics.
#     8.ROI_Calculations.
#     9.Strategic_Insights.
#     10.Recommendations.
#     11.Post_Frequency.
    
#     json format:
#     {"""
#         {
#            "Target_Audience": {
#               "فيسبوك": {
#                  "الفئة_العمرية": "",
#                  "الدخل": "",
#                  "الموقع_الجغرافي": "",
#                  "الاهتمامات": [],
#                  "السلوك": [],
#                  "نوع_الإعلانات": [],
#                  "الأهداف": []
#               },
#               "إنستغرام": {
#                  "الفئة_العمرية": "",
#                  "الدخل": "",
#                  "الاهتمامات": [],
#                  "السلوك": [],
#                  "نوع_الإعلانات": [],
#                  "الأهداف": []
#               },
#               "لينكد_إن": {
#                  "الفئة_المستهدفة": "",
#                  "الدخل": "",
#                  "الاهتمامات": [],
#                  "نوع_الإعلانات": [],
#                  "الأهداف": []
#               },
#               "تويتر": {
#                  "الفئة العمرية": "",
#                  "الدخل": "",
#                  "الاهتمامات": [],
#                  "السلوك": [],
#                  "نوع الإعلانات": [],
#                  "الأهداف": []
#               },
#               "جوجل": {
#                  "الكلمات_المفتاحية": [],
#                  "نوع_الإعلانات": [],
#                  "الأهداف": []
#               }
#            },
#            "Market_Strategy": {
#                 "فيسبوك": {
#                     "استراتيجية السوق": "",
#                     "التوصيات": "",
#                     "النقرات اليومية": "100",
#                     "نسبة النقر (CTR)": "0.02",
#                     "نسبة التحويل (conversion_rate)": "0.01",
#                     "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
#                     "التكلفة السنوية": ""
#                 },
#                 "إنستغرام": {
#                     "استراتيجية السوق": "",
#                     "التوصيات": "",
#                     "النقرات اليومية": "80",
#                     "نسبة النقر (CTR)": "0.03",
#                     "نسبة التحويل (conversion_rate)": "0.015",
#                     "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
#                     "التكلفة السنوية": "",
#                 },
#                 "لينكد_إن": {
#                     "استراتيجية السوق": "",
#                     "التوصيات": "",
#                     "النقرات اليومية": "50",
#                     "نسبة النقر (CTR)": "0.015",
#                     "نسبة التحويل (conversion_rate)": "0.02",
#                     "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
#                     "التكلفة السنوية": "",
#                 },
#                 "تويتر": {
#                     "استراتيجية السوق": "",
#                     "التوصيات": "",
#                     "النقرات اليومية": "70",
#                     "نسبة النقر (CTR)": "0.025",
#                     "نسبة التحويل (conversion_rate)": "0.01",
#                     "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
#                     "التكلفة السنوية": "",
#                 },
#                 "جوجل": {
#                     "استراتيجية السوق": "",
#                     "التوصيات": "",
#                     "النقرات اليومية": "90",
#                     "نسبة النقر (CTR)": "0.04",
#                     "نسبة التحويل (conversion_rate)": "0.02",
#                     "تكلفة التسويق الشهرية": "(يجب عليك دراسة المنصة وكتابة التكلفة هنا مع مراعاة عملة البلد)",
#                     "التكلفة السنوية": "",
#               }
#            },
#            "Performance_Metrics": {
#               "فيسبوك": ["نسبة التفاعل", "نسبة النقر"],
#               "إنستغرام": ["عدد المتابعين", "نسبة التفاعل"],
#               "لينكد_إن": ["عدد المشاهدات", "عدد المحادثات"],
#               "تويتر": ["عدد الإشارات", "نسبة التفاعل"],
#               "جوجل": ["عدد الزيارات", "عدد التفاعل"]
#            },
#            "ROI_Calculation": {
#                 "فيسبوك": {
#                     "إسقاط_عدد_الزوار_السنوي": "",
#                     "إسقاط_عدد_المبيعات_السنوي": "",
#                     "إسقاط_الإيرادات_السنوية": "",
#                     "تكلفة_التسويق_السنوية": "",
#                     "صافي_الربح": "",
#                     "نسبة_العائد_على_الاستثمار": ""
#                 },
#                 "إنستغرام": {
#                     "إسقاط_عدد_الزوار_السنوي": "",
#                     "إسقاط_عدد_المبيعات_السنوي": "",
#                     "إسقاط_الإيرادات_السنوية": "",
#                     "تكلفة_التسويق_السنوية": "",
#                     "صافي_الربح": "",
#                     "نسبة_العائد_على_الاستثمار": ""
#                 },
#                 "لينكد_إن": {
#                     "إسقاط_عدد_الزوار_السنوي": "",
#                     "إسقاط_عدد_المبيعات_السنوي": "",
#                     "إسقاط_الإيرادات_السنوية": "",
#                     "تكلفة_التسويق_السنوية": "",
#                     "صافي_الربح": "",
#                     "نسبة_العائد_على_الاستثمار": ""
#                 },
#                 "تويتر": {
#                     "إسقاط_عدد_الزوار_السنوي": "",
#                     "إسقاط_عدد_المبيعات_السنوي": "",
#                     "إسقاط_الإيرادات_السنوية": "",
#                     "تكلفة_التسويق_السنوية": "",
#                     "صافي_الربح": "",
#                     "نسبة_العائد_على_الاستثمار": ""
#                 },
#                 "جوجل": {
#                     "إسقاط_عدد_الزوار_السنوي": "",
#                     "إسقاط_عدد_المبيعات_السنوي": "",
#                     "إسقاط_الإيرادات_السنوية": "",
#                     "تكلفة_التسويق_السنوية": "",
#                     "صافي_الربح": "",
#                     "نسبة_العائد_على_الاستثمار": ""
#                 }
#             },
#            "Strategic_Insights": {
#               "الفرص": "",
#               "المخاطر": ""
#            },
#            "Recommendations": {
#               "تحسين الإعلانات": "",
#               "زيادة التفاعل": "",
#               "استهداف دقيق": ""
#            },
#            "Post_Frequency": {
#               "فيسبوك": "",
#               "إنستغرام": "",
#               "لينكد_إن": "",
#               "تويتر": "",
#               "جوجل": ""
#            }
#         }

#     """}
#     إرشادات: 
#     أعطني فقط البيانات بدون اسم المشروع او أي شئ آخر .. فقط اتبع الترتيب بالأعلى و اعجلها لجميع المنصات 
    
#     """

#     system_prompt = f""" أنت أفضل media buyer متخصص. يجب عليك أن تلبي إحتياجات العميل على أكمل وجه ممكن."""

#     context = [{"role": "system", "content": system_prompt},{"role": "user", "content": user_prompt}]
#     parsed_ai_response = ''
#     try:
#         chat_completion = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=context,
#             max_tokens=16384,
#             response_format={"type": "json_object"},
#         )

#         # Fetching the response assuming it is structured as instructed
#         response = chat_completion.choices[0].message.content
#         print("Raw AI response:", response)

#         # Attempt to parse the response to ensure it is valid JSON
#         parsed_ai_response = json.loads(response)
#         print("Parsed AI response:", parsed_ai_response)
#     except json.JSONDecodeError as e:
#         print(f"Failed to decode JSON: {str(e)}")
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

#     return parsed_ai_response

# # وظيفة لتنظيم المخرجات في صيغة JSON
# def organize_campaign_output(project_name, location, platforms, assets, insights):
#     output = {
#         "project_name": project_name,
#         "location": location,
#         "platforms": platforms,
#         "assets": assets,
#         "insights": json.loads(insights)
#     }
#     return json.dumps(output, ensure_ascii=False, indent=4)

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
