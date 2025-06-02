from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import random
import time
from PIL import Image

# Load environment variables from a .env file
load_dotenv()

# Create OpenAI client
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

start_time = time.time()

prompt = """
        Genera una imagen de un caracol y una rana de escayola. El caracol debe ser de color azul y la rana de color verde. 
        La escena debe ser detallada y mostrar ambos objetos en un entorno natural.
        """

response = client.responses.create(
    model=os.getenv("IMAGE_GENERATION_MODEL"),
    input=prompt,
    tools=[{"type": "image_generation"}],
)

end_time = time.time()

# Randomly generate a number between 1000 and 9999
random_number = random.randint(1000, 9999)

# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open(f"image_with_responses_{random_number}.png", "wb") as f:
        f.write(base64.b64decode(image_base64))


# Print the execution time
execution_time = end_time - start_time
print(f"Image generated and saved as image_with_responses_{random_number}.png")
print(f"Execution time: {execution_time:.2f} seconds")

# Print the name of the generated image
print(f"Generated image name: image_with_responses_{random_number}.png")