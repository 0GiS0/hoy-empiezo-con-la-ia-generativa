"""
Si solo necesitas generar o editar una única imagen usando un único prompt, esta API es la más sencilla de usar.
Esta a día de hoy soporta gpt-image-1, dall-e-2 y dall-e-3.

"""
import os
from openai import OpenAI
from dotenv import load_dotenv
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


# Prompt de ejemplo
prompt = """
   Una escena realista, con estilo cinematográfico, que muestra a una inteligencia artificial generando arte. 
   La IA está representada por un brazo robótico futurista que pinta sobre un gran lienzo en un estudio creativo moderno. 
   En el lienzo aparece una imagen vibrante en proceso: mitad digital, mitad pintada a mano, simbolizando la fusión entre 
   tecnología y creatividad. Alrededor hay monitores que muestran prompts de generación de imágenes y referencias coloridas. 
   La iluminación es cálida y suave, con un leve resplandor que emana del lienzo. La IA está rodeada de bocetos, fotos de inspiración
   y moodboards digitales. El entorno es original, inspirador y con un espacio vacío en uno de los lados para insertar la imagen o 
   el logo del canal de YouTube.
    """

start_time = time.time()

# Llamada a la API para generar la imagen
response = client.images.generate(
    model=os.getenv("MODEL"),
    prompt=prompt,
    size="1024x1024",  # También puedes usar "1024x1792" o "1792x1024"
    n=1  # Número de imágenes a generar
)

end_time = time.time()

# Manejo de errores
image_base64 = response.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Genera un número aleatorio entre 1000 y 9999
random_number = random.randint(1000, 9999)

# Save the image to a file
with open(f"result_{random_number}.png", "wb") as f:
    f.write(image_bytes)

# Get image resolution from the file generated
with Image.open(f"result_{random_number}.png") as img:
    image_size = img.size
print(f"Image resolution: {image_size}")

# Print the execution time
execution_time = end_time - start_time
print(f"Image generated and saved as result_{random_number}.png")
print(f"Execution time: {execution_time} seconds")