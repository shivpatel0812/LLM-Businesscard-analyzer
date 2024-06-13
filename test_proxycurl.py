import requests

# Define your Proxycurl API key
api_key = "TI1vqZrelObP0lGYfSsYPA"
headers = {'Authorization': 'Bearer ' + api_key}
api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
linkedin_profile_url = 'https://www.linkedin.com/in/williamhgates'

response = requests.get(api_endpoint,
                        params={'url': linkedin_profile_url},
                        headers=headers)

# Print the response status code and content
print(f"Status Code: {response.status_code}")
try:
    response_data = response.json()
    print("Response JSON:", response_data)
except ValueError as e:
    print("Failed to parse JSON response. Response content:")
    print(response.text)
