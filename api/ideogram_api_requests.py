import json

import requests
import os


def generate_image_from_ideogram(prompt):
    url = "https://api.ideogram.ai/generate"

    headers = {
        "Api-Key": os.getenv('IDEOGRAM_API_KEY'),
        "Content-Type": "application/json"
    }

    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": "ASPECT_16_9",
            "model": "V_2",
            "style_type": "RENDER_3D",
            "magic_prompt_option": "OFF",
            "negative_prompt": "extra floors, hidden floors, partial floors, mechanical penthouse, rooftop structures, basement, mezzanine, split levels, ambiguous floor count, similar building, duplicate building, repeated architecture"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        return response_data
    except Exception as error:
        print(f"Error: {error}")
        return None

def generate_image_from_ideogram_remix(prompt, reference_image_url):
    """
    Generates a new, 'remixed' image based on a reference image,
    with a fresh prompt to guide how it transforms.
    """

    url = "https://api.ideogram.ai/generate"

    headers = {
        "Api-Key": os.getenv('IDEOGRAM_API_KEY'),  # Make sure your environment variable is set!
        "Content-Type": "application/json"
    }

    # This payload includes an example of how you might pass in your reference for "remix"
    payload = {
        "image_request": {
            "prompt": prompt,
            "model": "V_2",  # Some versions might call for 'remix' specifically, or a different model name
            "style_type": "RENDER_3D",
            "aspect_ratio": "ASPECT_16_9",

            # The magic sauce for a remix approach
            "remix_image_url": reference_image_url,  # The direct link to your reference image

            # Additional settings
            "magic_prompt_option": "OFF",
            "negative_prompt": (
                "extra floors, hidden floors, partial floors, mechanical penthouse, "
                "rooftop structures, basement, mezzanine, split levels, ambiguous floor count, "
                "similar building, duplicate building, repeated architecture"
            )
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Good practice: raises HTTPError if the request was unsuccessful
        response_data = response.json()
        return response_data
    except Exception as error:
        print(f"Error generating remixed image: {error}")
        return None


def remix_image_from_remote_url(prompt, remote_image_url):
    """
    1. Fetch an image from the web.
    2. Post it to Ideogram's /remix endpoint.
    3. Return JSON response with the remixed image URL/info.
    """

    # Step 1: Download the image bytes from the remote URL
    try:
        image_response = requests.get(remote_image_url)
        image_response.raise_for_status()
        image_bytes = image_response.content
        print(image_bytes)
    except Exception as e:
        print(f"Error downloading image from {remote_image_url}: {e}")
        return None

    # Step 2: Prepare the /remix endpoint parameters
    remix_url = "https://api.ideogram.ai/remix"
    headers = {
        "Api-Key": os.getenv('IDEOGRAM_API_KEY')
    }

    # 'files' expects a tuple in the form: (filename, file_data, content_type)
    # We'll make up a filename (e.g., 'remix.jpg') and guess the content type
    # If it's actually PNG, or the service is picky, adjust as needed.
    files = {
        "image_file": ("remix.jpg", image_bytes, "image/jpeg")
    }

    # The prompt and other parameters go in 'image_request'
    # They must be sent as a JSON *string* for the form fields
    payload = {
        "image_request": json.dumps({
            "prompt": prompt,
            "aspect_ratio": "ASPECT_10_16",
            "image_weight": 40,
            "magic_prompt_option": "OFF",
            "model": "V_2_TURBO",
        })
    }

    print(payload)

    # Step 3: Send the POST request to /remix
    try:
        response = requests.post(remix_url, data=payload, files=files, headers=headers)
        response.raise_for_status()  # Raises a requests.HTTPError for bad responses
        return response.json()
    except Exception as e:
        print(f"Error calling Ideogram /remix endpoint: {e}")
        return None
