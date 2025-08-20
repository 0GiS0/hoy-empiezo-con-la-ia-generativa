import os
from dotenv import load_dotenv
from mistralai import Mistral
import time


# Load environment variables from a .env file
load_dotenv()

# Initialize the Mistral client
client = Mistral(
    api_key=os.getenv("GITHUB_TOKEN"),
    server_url=os.getenv("GITHUB_MODELS_URL")
)

start_time = time.time()

# Call the Mistral API to generate text
response = client.chat.complete(
    model="mistral-ai/mistral-small-2503",
    messages=[
        {"role": "user", "content": "Mejórame este título para un vídeo de YouTube, incluye emojis:" + os.getenv("YOUTUBE_TITLE")}
    ]
)

end_time = time.time()
execution_time = end_time - start_time

# Print the response
print(response.choices[0].message.content)
print(f"Execution time: {execution_time} seconds")
