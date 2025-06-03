"""
En este ejemplo, se utiliza la API de OpenAI para analizar imágenes usando el endpoint de chat completions.
Se envía una solicitud con un texto y una imagen, y se obtiene una respuesta que describe lo que se ve en la imagen.
El código utiliza la biblioteca `openai` para interactuar con la API y `dotenv` para cargar las variables de entorno.
Asegúrate de tener las variables de entorno `ENDPOINT_URL`, `API_KEY` y `MODEL_FOR_VISION` configuradas correctamente en tu archivo `.env`.
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
from rich.console import Console
import time

load_dotenv()
console = Console()

# Crear cliente de OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Iniciar medición de tiempo
start_time = time.time()

# Analizar una imagen usando la API de OpenAI usando URL
console.print(
    ":mag: [bold cyan]Analizando imagen...[/bold cyan] :framed_picture:")

response = client.chat.completions.create(
    model=os.getenv("MODEL_FOR_VISION"),
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "¿Qué ves en esta imagen?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://i0.wp.com/www.returngis.net/wp-content/uploads/2025/04/Ollama-con-Prompty.png"                        
                    }
                }
            ]
        }
    ]
)

# Finalizar medición de tiempo
end_time = time.time()

console.print(
    f":hourglass_flowing_sand: [green]Tiempo de respuesta:[/green] {end_time - start_time:.2f} segundos")
console.print(":sparkles: [bold yellow]Descripción generada:[/bold yellow]")
console.print(response.choices[0].message.content)

