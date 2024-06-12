import os
from openai import OpenAI

# Set the environment variable


OPENAI_API_KEY="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"



client = OpenAI(
  organization='org-CShH8o5u9YiL93m6V71zkQxY',
  project='your_project_id_here',  # Replace with your actual project ID
)

# Now you can use the client to make API calls

stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")