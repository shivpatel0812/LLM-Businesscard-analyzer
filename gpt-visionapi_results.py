import base64
import json
import os
import openai

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Encode the local image as base64
image_local = './Images/IMG_3016.jpg'
image_base64 = encode_image(image_local)

# Set your API key here
api_key = "test"

# Initialize the OpenAI client
openai.api_key = api_key

response = openai.ChatCompletion.create(
    model='gpt-4-vision-preview',
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Return JSON document with data. Only return JSON not other text. Also write out 3 good paragraphs under the JSON that gives details about the company and about the person if possible. Specfically go into the role of the person if mentioned and try to get as specific as possible in what that role does at that specific company. Also after you wirte the paragraph rewrite all the contact info and honelsty all the import general info reput it under the summary that i told you. In short the user shoudl be able to scan a business card and all important information should be given so that next time that person maybe speak to that person or reaches out they are able to have a very background of what they do and mentioning as many key facts regarding the position, projects, experiences, etc. would be the best so that this information cna be used for the user."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                }
            ],
        }
    ],
    max_tokens=500,
)

# Extract response content
response_content = response.choices[0].message['content']

# Separate JSON part and additional text
json_part, text_part = response_content.split('\n\n', 1)

# Clean up JSON part
json_part = json_part.replace("```json\n", "").replace("\n```", "")

# Parse the string into a JSON object
try:
    json_data = json.loads(json_part)
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    exit(1)

# Create the directory if it doesn't exist
output_directory = "./Data/"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

filename_without_extension = os.path.splitext(os.path.basename(image_local))[0]

# Add .json extension to the filename
json_filename = f"{filename_without_extension}.json"

# Save the JSON data to a file with proper formatting
with open(os.path.join(output_directory, json_filename), 'w') as file:
    json.dump(json_data, file, indent=4)

print(f"JSON data saved to {json_filename}")

# Save the additional text to a file
text_filename = f"{filename_without_extension}_details.txt"
with open(os.path.join(output_directory, text_filename), 'w') as file:
    file.write(text_part)

print(f"Additional text saved to {text_filename}")
