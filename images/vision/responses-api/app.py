"""
En este ejemplo, se utiliza la API de OpenAI para analizar imágenes.
Se envía una solicitud con un texto y una imagen, y se obtiene una respuesta que describe lo que se ve en la imagen.
El código utiliza la biblioteca `openai` para interactuar con la API y `dotenv` para cargar las variables de entorno.
Asegúrate de tener las variables de entorno `ENDPOINT_URL`, `API_KEY` y `MODEL_FOR_VISION` configuradas correctamente en tu archivo `.env`.
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
from rich.console import Console
import time
import base64
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

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

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
    progress.add_task(description="🔍 Analizando la imagen...", total=None)
    response = client.responses.create(
        model=os.getenv("MODEL_FOR_VISION"),
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": "¿Qué ves en esta imagen?"},
                {
                    "type": "input_image",
                            "image_url": "https://i0.wp.com/www.returngis.net/wp-content/uploads/2025/04/Ollama-con-Prompty.png",
                            ""
                    "detail": "low"  # low, high o auto
                },
            ],
        }],
    )

# Finalizar medición de tiempo
end_time = time.time()

console.print(
    f":hourglass_flowing_sand: [green]Tiempo de respuesta:[/green] {end_time - start_time:.2f} segundos")
console.print(":sparkles: [bold yellow]Descripción generada:[/bold yellow]")
console.print(response.output_text)

# Analizar usando una imagen en base64
console.print(
    ":mag: [bold cyan]Analizando imagen en base64...[/bold cyan] :framed_picture:")


def encode_image_to_base64(image_path):
    """Convierte una imagen a base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image = encode_image_to_base64(
    "/workspaces/hoy-empiezo-con-ia-generativa/images/vision/samples/partida_de_ajedrez.jpg")

response_base64 = client.responses.create(
    model=os.getenv("MODEL_FOR_VISION"),
    input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": "¿Qué ves en esta imagen?"},
            {
                "type": "input_image",
                "image_url":  f"data:image/jpeg;base64,{base64_image}",

            },
        ],
    }],
)

# Mostrar el tiempo de respuesta
end_time_base64 = time.time()
console.print(
	f":hourglass_flowing_sand: [green]Tiempo de respuesta (base64):[/green] {end_time_base64 - end_time:.2f} segundos")

# Descripción de la imagen en base64
console.print(":sparkles: [bold yellow]Descripción generada (base64):[/bold yellow]")
print(response_base64.output_text)


