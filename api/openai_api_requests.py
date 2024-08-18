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
            temperature=0.3,
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
            temperature=0.3,
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


def image_creator(prompt):
    try:
        # Generate an image using the DALL-E model from OpenAI
        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            style="natural",
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


def image_analyzer(image_path, sent_context):
    try:
        # base64_image = encode_image(image_path)
        context = [{"role": "system", "content": sent_context},
                   {"role": "user", "content":[
                       {
                           'type': 'image_url',
                           'image_url':{
                               'url':image_path
                           }
                       }
                   ]
                    }]
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
            response_format={"type":"json_object"},
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
            response_format={"type":"json_object"},
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
def investment_generator(user_input):
    try:
        context = [
            {
                "role":"system",
                "content":"""
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
                                        "zoning_regulations": "Residential R3, allowing for up to 3 stories"
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
            },
            {
                "role":"user",
                "content":user_input
            }
        ]

        print(context)
        chat_completion = client.chat.completions.create(
            messages=context,
            model="gpt-4o-mini",
            temperature=0.7,
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