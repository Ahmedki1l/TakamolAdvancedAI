import requests
import os


def generate_image_from_ideogram(prompt):
    url = "https://api.ideogram.ai/generate"

    headers = {
        "Authorization": f"Bearer {os.environ.get('API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": "ASPECT_16_9",
            "model": "V_2_TURBO",
            "style_type": "RENDER_3D",
            "magic_prompt_option": "ON"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        return response_data
    except Exception as error:
        print(f"Error: {error}")
        return None
