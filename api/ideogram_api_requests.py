import json
import requests
import os
import time
import random

def generate_image_from_ideogram(prompt, floor_count=None, view_type="side"):
    """
    Specialized function for generating high-rise buildings with accurate floor counts,
    optimized for side views to show all floors clearly.
    
    Args:
        prompt: Base description of the building
        floor_count: Number of floors in the building (optional)
        view_type: "side" (default for tall buildings) or "front" (for shorter buildings)
    """
    url = "https://api.ideogram.ai/generate"

    headers = {
        "Api-Key": os.getenv('IDEOGRAM_API_KEY'),
        "Content-Type": "application/json"
    }
    
    # If floor_count is specified, enhance the prompt for accurate floor rendering
    if floor_count:
        # Determine the optimal view based on floor count
        if view_type == "auto":
            view_type = "side" if floor_count > 8 else "front"
        
        # Specialized prompts based on view type
        if view_type == "side":
            view_prompt = f"""
            dramatic side view of a {floor_count}-story skyscraper,
            complete vertical view showing all {floor_count} floors from ground to top,
            each floor clearly visible and distinctly separated,
            architectural cross-section style,
            precise floor count: exactly {floor_count} floors,
            each floor labeled with its number,
            perspective that reveals the entire height of the building,
            dramatic lighting highlighting each floor's separation,
            ultrarealistic 3D architectural rendering,
            """
        else:
            view_prompt = f"""
            front view of a {floor_count}-story building,
            showing all {floor_count} floors clearly,
            each floor distinctly separated with visible floor lines,
            precise floor count: exactly {floor_count} floors,
            professional architectural rendering,
            """
        
        # Combine with the base prompt
        enhanced_prompt = f"{prompt}, {view_prompt} photorealistic 3D render, architectural visualization, high-detail facade texture, perfect lighting"
        
        # Generate a seed for reproducibility
        seed = random.randint(1000, 9999999)
        
        aspect_ratio = "ASPECT_9_16" if view_type == "side" else "ASPECT_16_9"
        
        negative_prompt = "incorrect floor count, merged floors, hidden floors, ambiguous floors, partial floors, unclear floor separations, inaccurate building height, wrong number of floors, cartoon style, unrealistic proportions, distorted perspective"
    else:
        # Use the prompt as is if no floor_count is specified
        enhanced_prompt = prompt
        seed = random.randint(1000, 9999999)
        aspect_ratio = "ASPECT_16_9"
        negative_prompt = "extra floors, hidden floors, partial floors, mechanical penthouse, rooftop structures, basement, mezzanine, split levels, ambiguous floor count, similar building, duplicate building, repeated architecture"
    
    payload = {
        "image_request": {
            "prompt": enhanced_prompt,
            "aspect_ratio": aspect_ratio,
            "model": "V_2",
            "style_type": "RENDER_3D",
            "magic_prompt_option": "OFF",
            "strength": 95,
            "seed": seed,
            "negative_prompt": negative_prompt
        }
    }

    if floor_count:
        print(f"Generating {view_type} view for {floor_count}-story building with seed {seed}")
    print(f"Enhanced prompt: {enhanced_prompt[:100]}...")

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except Exception as error:
        print(f"Error: {error}")
        if hasattr(error, 'response') and hasattr(error.response, 'text'):
            print(f"Response content: {error.response.text}")
        return None

def generate_image_from_ideogram_remix(prompt, image_url, floor_count=None, view_type="side"):
    """
    Remix a reference image into a high-rise building with accurate floor count,
    optimized for side views for tall buildings.
    
    Args:
        prompt: Base description for the image generation
        image_url: URL of the reference image to remix
        floor_count: Number of floors (optional)
        view_type: "side" (default) or "front" view perspective
    """
    # Step 1: Download the image bytes from the URL
    try:
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        image_bytes = image_response.content
        print("Successfully downloaded the image")
    except Exception as e:
        print(f"Error downloading image from {image_url}: {e}")
        return None

    # Step 2: Prepare the /remix endpoint parameters
    remix_url = "https://api.ideogram.ai/remix"
    headers = {
        "Api-Key": os.getenv('IDEOGRAM_API_KEY')
    }
    
    # If floor_count is specified, enhance the prompt for building rendering
    if floor_count:
        # Determine the optimal view and aspect ratio based on floor count
        if view_type == "auto":
            view_type = "side" if floor_count > 8 else "front"
        
        aspect_ratio = "ASPECT_9_16" if view_type == "side" else "ASPECT_16_9"
        
        # Specialized prompts based on view type
        if view_type == "side":
            view_prompt = f"""
            dramatic side view perspective of a {floor_count}-story skyscraper,
            complete vertical view showing all {floor_count} floors from ground to top,
            each floor clearly visible and distinctly separated,
            architectural cross-section style,
            precise floor count: exactly {floor_count} floors,
            each floor numbered 1 through {floor_count},
            perspective that captures the entire height of the building,
            dramatic lighting highlighting each floor's separation,
            """
        else:
            view_prompt = f"""
            front view of a {floor_count}-story building,
            showing all {floor_count} floors clearly,
            each floor distinctly separated with visible floor lines,
            precise floor count: exactly {floor_count} floors,
            """
        
        # Combine with the base prompt
        enhanced_prompt = f"""
        {prompt},
        {view_prompt}
        photorealistic 3D architectural visualization,
        high-detail facade texture,
        perfect lighting conditions,
        ultrarealistic materials,
        professional architectural rendering,
        award-winning architectural photography,
        each floor individually countable,
        """
        
        image_weight = 70  # Lower weight to allow more creative freedom with the perspective
        
        negative_prompt = (
            "incorrect floor count, wrong number of floors, merged floors, hidden floors, "
            "ambiguous floors, partial floors, unclear floor separations, inaccurate building height, "
            "cartoon style, unrealistic proportions, distorted perspective, "
            "incorrect view angle, cut-off building, incomplete building"
        )
    else:
        # Use simpler parameters if no floor_count is specified
        enhanced_prompt = prompt
        aspect_ratio = "ASPECT_16_9"
        image_weight = 40
        negative_prompt = (
            "extra floors, hidden floors, partial floors, mechanical penthouse, "
            "rooftop structures, basement, mezzanine, split levels, ambiguous floor count, "
            "similar building, duplicate building, repeated architecture"
        )
    
    # Generate a seed for reproducibility
    seed = random.randint(1000, 9999999)
    
    # 'files' expects a tuple in the form: (filename, file_data, content_type)
    files = {
        "image_file": ("building.jpg", image_bytes, "image/jpeg")
    }

    # The prompt and other parameters go in 'image_request'
    payload = {
        "image_request": json.dumps({
            "prompt": enhanced_prompt.strip(),
            "aspect_ratio": aspect_ratio,
            "image_weight": image_weight,
            "magic_prompt_option": "OFF",
            "model": "V_2",
            "style_type": "RENDER_3D",
            "upscale_factor": "2X",
            "seed": seed,
            "negative_prompt": negative_prompt
        })
    }

    if floor_count:
        print(f"Remixing to {view_type} view for {floor_count}-story building with seed {seed}")
    print(f"Enhanced prompt: {enhanced_prompt[:100]}...")

    # Implement retry logic for more reliable results
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(remix_url, data=payload, files=files, headers=headers)
            response.raise_for_status()
            result = response.json()
            print("Successfully created remix")
            return result
        except Exception as e:
            print(f"Error calling Ideogram /remix endpoint (attempt {attempt+1}/{max_retries}): {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response content: {e.response.text}")
            
            # If we haven't reached max retries, wait and try again
            if attempt < max_retries - 1:
                print(f"Retrying in 3 seconds...")
                time.sleep(3)
            else:
                print("Maximum retry attempts reached. Render failed.")
                return None

def remix_image_from_remote_url(prompt, remote_image_url):
    """
    1. Fetch an image from the web.
    2. Post it to Ideogram's /remix endpoint.
    3. Return JSON response with the remixed image URL/info.
    
    A more generic version of the remix function.
    """
    # Step 1: Download the image bytes from the remote URL
    try:
        image_response = requests.get(remote_image_url)
        image_response.raise_for_status()
        image_bytes = image_response.content
        print("Successfully downloaded the image")
    except Exception as e:
        print(f"Error downloading image from {remote_image_url}: {e}")
        return None

    # Step 2: Prepare the /remix endpoint parameters
    remix_url = "https://api.ideogram.ai/remix"
    headers = {
        "Api-Key": os.getenv('IDEOGRAM_API_KEY')
    }

    # 'files' expects a tuple in the form: (filename, file_data, content_type)
    files = {
        "image_file": ("remix.jpg", image_bytes, "image/jpeg")
    }

    # The prompt and other parameters go in 'image_request'
    payload = {
        "image_request": json.dumps({
            "prompt": prompt,
            "aspect_ratio": "ASPECT_10_16",
            "image_weight": 40,
            "magic_prompt_option": "OFF",
            "model": "V_2",
            "style_type": "RENDER_3D",
        })
    }

    # Step 3: Send the POST request to /remix
    try:
        response = requests.post(remix_url, data=payload, files=files, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error calling Ideogram /remix endpoint: {e}")
        return None

def render_building_smart(image_url, floor_count, description="", max_retry=2):
    """
    Smart function to render buildings with the most appropriate view based on floor count.
    Automatically selects side view for tall buildings and front view for shorter ones.
    
    Args:
        image_url: URL to the reference image
        floor_count: Number of floors in the building
        description: Additional building description
        max_retry: Maximum number of rendering attempts with different methods
    
    Returns:
        Generated image data or None if all attempts fail
    """
    view_type = "side" if floor_count > 8 else "front"
    
    print(f"Smart rendering {floor_count}-floor building with {view_type} view")
    
    # First attempt: try remixing with the optimal view
    result = generate_image_from_ideogram_remix(description, image_url, floor_count, view_type)
    if result:
        return result
    
    # Second attempt: try direct generation with the optimal view
    result = generate_image_from_ideogram(description, floor_count, view_type)
    if result:
        return result
    
    # Third attempt: try alternate view if previous attempts failed
    alt_view = "front" if view_type == "side" else "side"
    print(f"Retrying with alternate {alt_view} view")
    result = generate_image_from_ideogram(description, floor_count, alt_view)
    
    return 


# import json

# import requests
# import os


# def generate_image_from_ideogram(prompt):
#     url = "https://api.ideogram.ai/generate"

#     headers = {
#         "Api-Key": os.getenv('IDEOGRAM_API_KEY'),
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "image_request": {
#             "prompt": prompt,
#             "aspect_ratio": "ASPECT_16_9",
#             "model": "V_2",
#             "style_type": "RENDER_3D",
#             "magic_prompt_option": "OFF",
#             "negative_prompt": "extra floors, hidden floors, partial floors, mechanical penthouse, rooftop structures, basement, mezzanine, split levels, ambiguous floor count, similar building, duplicate building, repeated architecture"
#         }
#     }

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response_data = response.json()
#         return response_data
#     except Exception as error:
#         print(f"Error: {error}")
#         return None

# def generate_image_from_ideogram_remix(prompt, reference_image_url):
#     """
#     Generates a new, 'remixed' image based on a reference image,
#     with a fresh prompt to guide how it transforms.
#     """

#     url = "https://api.ideogram.ai/generate"

#     headers = {
#         "Api-Key": os.getenv('IDEOGRAM_API_KEY'),  # Make sure your environment variable is set!
#         "Content-Type": "application/json"
#     }

#     # This payload includes an example of how you might pass in your reference for "remix"
#     payload = {
#         "image_request": {
#             "prompt": prompt,
#             "model": "V_2",  # Some versions might call for 'remix' specifically, or a different model name
#             "style_type": "RENDER_3D",
#             "aspect_ratio": "ASPECT_16_9",

#             # The magic sauce for a remix approach
#             "remix_image_url": reference_image_url,  # The direct link to your reference image

#             # Additional settings
#             "magic_prompt_option": "OFF",
#             "negative_prompt": (
#                 "extra floors, hidden floors, partial floors, mechanical penthouse, "
#                 "rooftop structures, basement, mezzanine, split levels, ambiguous floor count, "
#                 "similar building, duplicate building, repeated architecture"
#             )
#         }
#     }

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()  # Good practice: raises HTTPError if the request was unsuccessful
#         response_data = response.json()
#         return response_data
#     except Exception as error:
#         print(f"Error generating remixed image: {error}")
#         return None


# def remix_image_from_remote_url(prompt, remote_image_url):
#     """
#     1. Fetch an image from the web.
#     2. Post it to Ideogram's /remix endpoint.
#     3. Return JSON response with the remixed image URL/info.
#     """

#     # Step 1: Download the image bytes from the remote URL
#     try:
#         image_response = requests.get(remote_image_url)
#         image_response.raise_for_status()
#         image_bytes = image_response.content
#         print(image_bytes)
#     except Exception as e:
#         print(f"Error downloading image from {remote_image_url}: {e}")
#         return None

#     # Step 2: Prepare the /remix endpoint parameters
#     remix_url = "https://api.ideogram.ai/remix"
#     headers = {
#         "Api-Key": os.getenv('IDEOGRAM_API_KEY')
#     }

#     # 'files' expects a tuple in the form: (filename, file_data, content_type)
#     # We'll make up a filename (e.g., 'remix.jpg') and guess the content type
#     # If it's actually PNG, or the service is picky, adjust as needed.
#     files = {
#         "image_file": ("remix.jpg", image_bytes, "image/jpeg")
#     }

#     # The prompt and other parameters go in 'image_request'
#     # They must be sent as a JSON *string* for the form fields
#     payload = {
#         "image_request": json.dumps({
#             "prompt": prompt,
#             "aspect_ratio": "ASPECT_10_16",
#             "image_weight": 40,
#             "magic_prompt_option": "OFF",
#             "model": "V_2_TURBO",
#         })
#     }

#     print(payload)

#     # Step 3: Send the POST request to /remix
#     try:
#         response = requests.post(remix_url, data=payload, files=files, headers=headers)
#         response.raise_for_status()  # Raises a requests.HTTPError for bad responses
#         return response.json()
#     except Exception as e:
#         print(f"Error calling Ideogram /remix endpoint: {e}")
#         return None


################################################################################################################################33
# import json
# import requests
# import os
# import time

# def generate_image_from_ideogram(prompt):
#     url = "https://api.ideogram.ai/generate"

#     headers = {
#         "Api-Key": os.getenv('IDEOGRAM_API_KEY'),
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "image_request": {
#             "prompt": prompt,
#             "aspect_ratio": "ASPECT_16_9",
#             "model": "V_2",
#             "style_type": "RENDER_3D",  # Changed from "RENDER_3D_PHOTOREALISTIC" to "RENDER_3D"
#             "magic_prompt_option": "OFF",
#             "negative_prompt": "extra floors, hidden floors, partial floors, mechanical penthouse, rooftop structures, basement, mezzanine, split levels, ambiguous floor count, similar building, duplicate building, repeated architecture"
#         }
#     }

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()  # Added to catch HTTP errors
#         response_data = response.json()
#         return response_data
#     except Exception as error:
#         print(f"Error: {error}")
#         if hasattr(error, 'response') and hasattr(error.response, 'text'):
#             print(f"Response content: {error.response.text}")
#         return None

# def generate_image_from_ideogram_remix(prompt, reference_image_url):
#     """
#     Generates a new, 'remixed' image based on a reference image,
#     with a fresh prompt to guide how it transforms.
#     """

#     url = "https://api.ideogram.ai/generate"

#     headers = {
#         "Api-Key": os.getenv('IDEOGRAM_API_KEY'),  # Make sure your environment variable is set!
#         "Content-Type": "application/json"
#     }

#     # Enhanced prompt for better architectural accuracy
#     enhanced_prompt = f"{prompt}, ultra-detailed photorealistic 3D render, architectural visualization, precise floor count, exact structural proportions, professional rendering"

#     # This payload includes an example of how you might pass in your reference for "remix"
#     payload = {
#         "image_request": {
#             "prompt": enhanced_prompt,
#             "model": "V_2",  # Some versions might call for 'remix' specifically, or a different model name
#             "style_type": "RENDER_3D",  # Changed from "RENDER_3D_PHOTOREALISTIC" to "RENDER_3D"
#             "aspect_ratio": "ASPECT_16_9",
#             "upscale_factor": "2X",  # Added upscaling for higher resolution

#             # The magic sauce for a remix approach
#             "remix_image_url": reference_image_url,  # The direct link to your reference image
#             "image_weight": 80,  # Increased image weight to preserve structure

#             # Additional settings
#             "magic_prompt_option": "OFF",
#             "negative_prompt": (
#                 "extra floors, hidden floors, partial floors, mechanical penthouse, "
#                 "rooftop structures, basement, mezzanine, split levels, ambiguous floor count, "
#                 "similar building, duplicate building, repeated architecture, "
#                 "low quality, blurry, distorted proportions, incorrect floor count"
#             )
#         }
#     }

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()  # Good practice: raises HTTPError if the request was unsuccessful
#         response_data = response.json()
#         return response_data
#     except Exception as error:
#         print(f"Error generating remixed image: {error}")
#         if hasattr(error, 'response') and hasattr(error.response, 'text'):
#             print(f"Response content: {error.response.text}")
#         return None


# def remix_image_from_remote_url(prompt, remote_image_url):
#     """
#     1. Fetch an image from the web.
#     2. Post it to Ideogram's /remix endpoint.
#     3. Return JSON response with the remixed image URL/info.
#     """

#     # Step 1: Download the image bytes from the remote URL
#     try:
#         image_response = requests.get(remote_image_url)
#         image_response.raise_for_status()
#         image_bytes = image_response.content
#         print("Successfully downloaded the image")
#     except Exception as e:
#         print(f"Error downloading image from {remote_image_url}: {e}")
#         return None

#     # Step 2: Prepare the /remix endpoint parameters
#     remix_url = "https://api.ideogram.ai/remix"
#     headers = {
#         "Api-Key": os.getenv('IDEOGRAM_API_KEY')
#     }

#     # Craft a highly detailed prompt for architectural accuracy
#     enhanced_prompt = f"""
#     {prompt}, 
#     photorealistic 3D rendering of a residential building, 
#     architectural visualization with perfect materials and lighting,
#     maintain EXACT floor count and level spacing from sketch,
#     precise structural proportions, hyperrealistic details,
#     professional architectural visualization, award-winning quality,
#     architectural photography style, dramatic lighting, perfect shadows,
#     ultradetailed facade, high-fidelity materials, crystal clear windows
#     """

#     # 'files' expects a tuple in the form: (filename, file_data, content_type)
#     files = {
#         "image_file": ("sketch.jpg", image_bytes, "image/jpeg")
#     }

#     # The prompt and other parameters go in 'image_request'
#     # Optimized parameters for high-quality renders
#     payload = {
#         "image_request": json.dumps({
#             "prompt": enhanced_prompt.strip(),
#             "aspect_ratio": "ASPECT_16_9",  # Match the aspect ratio to your sketch if needed
#             "image_weight": 85,  # Significantly increased image weight for structural accuracy
#             "magic_prompt_option": "OFF",
#             "model": "V_2",  # Use V_2 for better architectural detail
#             "style_type": "RENDER_3D",  # Changed from "RENDER_3D_PHOTOREALISTIC" to "RENDER_3D"
#             "upscale_factor": "2X",  # Request higher resolution output
#             "negative_prompt": (
#                 "distorted proportions, incorrect floor count, inaccurate building height, "
#                 "modified floor levels, extra floors, hidden floors, partial floors, "
#                 "mechanical penthouse, rooftop structures not in original, basement not in original, "
#                 "mezzanine not in original, split levels not in original, ambiguous floor count, "
#                 "blurry details, low quality, drafty, sketchy, unrealistic lighting, "
#                 "incorrect shadows, disproportionate windows, cartoon style, stylized"
#             )
#         })
#     }

#     print("Sending request with payload:", payload)

#     # Implement retry logic for more reliable results
#     max_retries = 3
#     for attempt in range(max_retries):
#         try:
#             response = requests.post(remix_url, data=payload, files=files, headers=headers)
#             response.raise_for_status()  # Raises a requests.HTTPError for bad responses
#             result = response.json()
#             print("Successfully created remix")
#             return result
#         except Exception as e:
#             print(f"Error calling Ideogram /remix endpoint (attempt {attempt+1}/{max_retries}): {e}")
#             if hasattr(e, 'response') and hasattr(e.response, 'text'):
#                 print(f"Response content: {e.response.text}")
            
#             # If we haven't reached max retries, wait and try again
#             if attempt < max_retries - 1:
#                 print(f"Retrying in 3 seconds...")
#                 time.sleep(3)
#             else:
#                 print("Maximum retry attempts reached. Render failed.")
#                 return None
