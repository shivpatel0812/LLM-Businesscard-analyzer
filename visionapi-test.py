import base64
import json
import os
import requests
import openai
import re
from urllib.parse import urlparse

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_from_image(client, image_url):
    try:
        response = client.chat.completions.create(
            model='gpt-4-vision-preview',
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract information from this business card image."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ],
                }
            ],
            max_tokens=500,
        )
        response_content = response.choices[0].message.content
        print("OpenAI API Response:", response_content)  # Debug print
        return response_content
    except openai.error.InvalidRequestError as e:
        print(f"Invalid request: {e}")
        return None

def test_proxycurl_connection(api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    test_url = 'https://nubela.co/proxycurl/api/v2/linkedin/profile/test'  # Example test endpoint
    response = requests.get(test_url, headers=headers)
    if response.status_code == 200:
        print("Proxycurl API is connected.")
        return True
    else:
        print(f"Error: Unable to connect to Proxycurl API. Status code: {response.status_code}")
        print(response.json())
        return False

def fetch_proxycurl_profile(api_key, email=None, name=None):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    if email:
        profile_url = f'https://nubela.co/proxycurl/api/v2/linkedin/profile/email/{email}'  # Corrected endpoint
    elif name:
        profile_url = f'https://nubela.co/proxycurl/api/v2/linkedin/profile/resolve?name={name}'
    else:
        return None
    
    response = requests.get(profile_url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to fetch data from Proxycurl. Status code: {response.status_code}")
        print(response.json())
        return None
    return response.json()

def extract_email(text):
    # Simple regex to extract email addresses
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text)
    return match.group(0) if match else None

def extract_name(text):
    # Example logic to extract name, can be improved
    lines = text.split('\n')
    for line in lines:
        if "name" in line.lower():
            return line.split(':')[-1].strip()
    return None

# Encode image
image_local = 'Images/IMG_3016.jpg'
image_base64 = encode_image(image_local)
image_url = f"data:image/jpeg;base64,{image_base64}"

# OpenAI setup
openai_api_key = "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"
client = openai.OpenAI(api_key=openai_api_key, organization='org-CShH8o5u9YiL93m6V71zkQxY')

# Proxycurl setup
proxycurl_api_key = "TI1vqZrelObP0lGYfSsYPA"

# Check Proxycurl API connection
if not test_proxycurl_connection(proxycurl_api_key):
    exit(1)

# Extract information from image
extracted_info = extract_text_from_image(client, image_url)
if extracted_info is None:
    exit(1)
print("Extracted Information:", extracted_info)

# Extract email and name from the extracted information
email = extract_email(extracted_info)
name = extract_name(extracted_info)

if email:
    # Fetch additional details from Proxycurl using email
    proxycurl_profile = fetch_proxycurl_profile(proxycurl_api_key, email=email)
    if proxycurl_profile is None:
        print("Unable to retrieve additional details from Proxycurl using email.")
        proxycurl_profile = {}
    print("Proxycurl Profile:", json.dumps(proxycurl_profile, indent=4))
elif name:
    # Fetch additional details from Proxycurl using name
    proxycurl_profile = fetch_proxycurl_profile(proxycurl_api_key, name=name)
    if proxycurl_profile is None:
        print("Unable to retrieve additional details from Proxycurl using name.")
        proxycurl_profile = {}
    print("Proxycurl Profile:", json.dumps(proxycurl_profile, indent=4))
else:
    print("Email or Name not found in extracted information.")
    proxycurl_profile = {}

# Integrate data and generate a detailed report using OpenAI
try:
    response = client.chat.completions.create(
        model='gpt-4-vision-preview',
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Generate a detailed report about the individual and the company based on the following data: "},
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": f"Extracted Info: {extracted_info}"},
                    {"type": "text", "text": f"Proxycurl Profile: {json.dumps(proxycurl_profile)}"}
                ],
            }
        ],
        max_tokens=1500,
    )
    response_content = response.choices[0].message.content
    print("OpenAI API Final Response:", response_content)  # Debug print
except openai.error.InvalidRequestError as e:
    print(f"Invalid request: {e}")
    exit(1)

# Assuming the response is plain text, split and save it accordingly
try:
    json_part, text_part = response_content.split('\n\n', 1)
    json_part = json_part.replace("```json\n", "").replace("\n```", "")
    json_data = json.loads(json_part)
except ValueError as e:
    print(f"Split error: {e}")
    json_data = None
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    json_data = None

if json_data is None:
    exit(1)

output_directory = "./Data/"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

filename_without_extension = os.path.splitext(os.path.basename(image_local))[0]
json_filename = f"{filename_without_extension}.json"

with open(os.path.join(output_directory, json_filename), 'w') as file:
    json.dump(json_data, file, indent=4)

print(f"JSON data saved to {json_filename}")

text_filename = f"{filename_without_extension}_details.txt"
with open(os.path.join(output_directory, text_filename), 'w') as file:
    file.write(text_part)

print(f"Additional text saved to {text_filename}")
