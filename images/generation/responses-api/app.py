"""
Esta API es mejor cuando quieres generar imágenes como parte de una conversación.
"""

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
Genera una imagen hiperrealista y detallada de un caracol de escayola azul y una rana de escayola verde, ambos situados juntos sobre un lecho de hojas y musgo en un entorno natural iluminado suavemente. 
Asegúrate de que el caracol y la rana sean claramente visibles, con texturas realistas de escayola, y que el fondo muestre vegetación y elementos naturales como piedras o ramas. 
La composición debe transmitir tranquilidad y resaltar los colores azul y verde de los animales.
"""

print("⏳ Generando la primera imagen (caracol y rana de escayola)... Esto puede tardar unos segundos.")
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
    filename = f"image_with_responses_{random_number}.png"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(image_base64))
    print(f"✅ Imagen generada y guardada como {filename}")
else:
    print("❌ No se pudo generar la primera imagen.")

# Print the execution time
execution_time = end_time - start_time
print(f"⏱️ Tiempo de ejecución de la primera generación: {execution_time:.2f} segundos")

# Follow up
print("\n⏳ Generando la segunda imagen (añadiendo mariposa amarilla)... Espera mientras se procesa la petición.")
second_response = client.responses.create(
    previous_response_id=response.id,
    model=os.getenv("IMAGE_GENERATION_MODEL"),
    input=(
        "Añade una mariposa de color amarillo, con alas abiertas y detalles realistas, "
        "posada suavemente sobre una hoja cerca del caracol y la rana. "
        "Asegúrate de que la mariposa destaque en la composición, manteniendo la iluminación suave y el entorno natural, "
        "y que todos los elementos conserven un aspecto hiperrealista y armonioso."
    ),
    tools=[{"type": "image_generation"}],
)

# Save the second image
second_image_data = [
    output.result
    for output in second_response.output
    if output.type == "image_generation_call"
]

if second_image_data:
    second_image_base64 = second_image_data[0]
    filename2 = f"image_with_responses_followup_{random_number}.png"
    with open(filename2, "wb") as f:
        f.write(base64.b64decode(second_image_base64))
    print(f"✅ Segunda imagen generada y guardada como {filename2}")
else:
    print("❌ No se pudo generar la segunda imagen.")

# Last but not least, another follow up
print("\n⏳ Generando la tercera imagen (escena completamente realista en un bosque)... Por favor, espera.")
third_response = client.responses.create(
    previous_response_id=second_response.id,
    model=os.getenv("IMAGE_GENERATION_MODEL"),
    input=(
        "Transforma la escena para que tanto el caracol, la rana y la mariposa tengan un aspecto completamente realista, "
        "que dejen de ser de escayola y se conviertan en animales vivos, "
        "con detalles naturales en sus texturas y colores. Cambia el fondo a un bosque frondoso y realista, "
        "con árboles, hojas y luz filtrada entre las ramas, manteniendo la composición armoniosa y la iluminación suave. "
        "Asegúrate de que los animales se integren perfectamente en el entorno natural del bosque."
    ),
    tools=[{"type": "image_generation"}],
)

# Save the third image
third_image_data = [
    output.result
    for output in third_response.output
    if output.type == "image_generation_call"
]

if third_image_data:
    third_image_base64 = third_image_data[0]
    filename3 = f"image_with_responses_followup2_{random_number}.png"
    with open(filename3, "wb") as f:
        f.write(base64.b64decode(third_image_base64))
    print(f"✅ Tercera imagen generada y guardada como {filename3}")
else:
    print("❌ No se pudo generar la tercera imagen.")

print("\n🎉 Proceso completado. Puedes revisar las imágenes generadas en el directorio actual.")