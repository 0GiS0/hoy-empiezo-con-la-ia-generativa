"""
En este ejemplo, se utiliza la API de OpenAI para analizar imágenes.
Se envía una solicitud con un texto y una imagen, y se obtiene una respuesta que describe lo que se ve en la imagen.
El código utiliza la biblioteca `openai` para interactuar con la API y `dotenv` para cargar las variables de entorno.
Asegúrate de tener las variables de entorno `ENDPOINT_URL`, `API_KEY` y `MODEL_FOR_VISION` configuradas correctamente en tu archivo `.env`.
"""
import os
import time
import base64
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Constantes de rutas de imagen
IMAGE_URL = "https://i0.wp.com/www.returngis.net/wp-content/uploads/2025/04/Ollama-con-Prompty.png"
IMAGE_PATH_BASE64 = "/workspaces/hoy-empiezo-con-ia-generativa/images/vision/samples/partida_de_ajedrez.jpg"

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
console = Console()

# Crear cliente de OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Función para codificar una imagen a base64
def encode_image_to_base64(image_path):
    """Convierte una imagen a base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Función para analizar una imagen usando el endpoint /v1/responses
def analyze_image_openai(description, input_data):
    """Analiza una imagen usando la API de OpenAI y muestra un spinner con tiempo transcurrido."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        transient=True,
        console=console
    ) as progress:
        progress.add_task(description=description, total=None)
        start_time = time.time()
        response = client.responses.create(
            model=os.getenv("MODEL_FOR_VISION"),
            input=input_data,
        )
        elapsed = time.time() - start_time
        return response.output_text, elapsed

# Función para mostrar el resultado en un panel de Rich
def show_result_panel(text, elapsed_time, title, color):
    """Muestra el resultado en un panel de Rich."""
    console.print(
        Panel.fit(
            f":hourglass_flowing_sand: [green]Tiempo de respuesta:[/green] {elapsed_time:.2f} segundos\n\n"
            f":sparkles: [bold yellow]Descripción generada:[/bold yellow]\n"
            f"{text}",
            title=title,
            border_style=color
        )
    )

# --- Análisis por URL ---
input_url = [{
    "role": "user",
    "content": [
        {"type": "input_text", "text": "¿Qué ves en esta imagen?"},
        {
            "type": "input_image",
            "image_url": IMAGE_URL,
            "detail": "auto"
        },
    ],
}]
description_url = "🔍 Analizando la imagen..."
text_url, elapsed_url = analyze_image_openai(description_url, input_url)
show_result_panel(text_url, elapsed_url, "Resultado Imagen por URL", "bright_blue")

# --- Análisis por base64 ---
base64_image = encode_image_to_base64(IMAGE_PATH_BASE64)
input_base64 = [{
    "role": "user",
    "content": [
        {"type": "input_text", "text": "¿Qué ves en esta imagen?"},
        {
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{base64_image}",
        },
    ],
}]
description_base64 = "🔍 Analizando la imagen en base64..."
text_base64, elapsed_base64 = analyze_image_openai(description_base64, input_base64)
show_result_panel(text_base64, elapsed_base64, "Resultado Imagen Base64", "bright_magenta")
