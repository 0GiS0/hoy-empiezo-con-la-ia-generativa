from openai import OpenAI
import os
from dotenv import load_dotenv
from rich.console import Console
import time
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
import base64

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configurar la consola de Rich para mostrar mensajes
console = Console()

# Configurar el cliente de OpenAI con las variables de entorno
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Analiza la imagen usando el endpoint de chat completions
def analyze_image(description, prompt):
    # Muestra un spinner de progreso mientras se analiza la imagen
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), transient=True, console=console) as progress:
        progress.add_task(description=description, total=None)
        start_time = time.time()

        # Llamada al endpoint de chat completions
        response = client.chat.completions.create(
            model=os.getenv("MODEL_FOR_VISION"),
            messages=prompt
        )

        end_time = time.time()
        elapsed = end_time - start_time
        return response.choices[0].message.content, elapsed

# Analizar imagen por URL
prompt_with_url = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What do you see in this image?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://i0.wp.com/www.returngis.net/wp-content/uploads/2025/04/Ollama-con-Prompty.png"
                }
            }
        ]
    }
]
description_url = "🔍 Analyzing the image retrieved from a URL..."
result_url, time_url = analyze_image(description_url, prompt_with_url)
console.print(
    Panel.fit(
        f":hourglass_flowing_sand: [green]Response time:[/green] {time_url:.2f} seconds\n\n"
        f":sparkles: [bold yellow]Generated description:[/bold yellow]\n"
        f"{result_url}",
        title="Result Image by URL",
        border_style="bright_blue"
    )
)

# Analizar imagen en base64
with open("/workspaces/hoy-empiezo-con-ia-generativa/images/vision/samples/IMG_2377.png", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

prompt_with_base64 = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What do you see in this base64 image?"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
            }
        ]
    }
]

description_base64 = "🔍 Analyzing base64 image..."
result_base64, time_base64 = analyze_image(description_base64, prompt_with_base64)
console.print(
    Panel.fit(
        f":hourglass_flowing_sand: [green]Response time:[/green] {time_base64:.2f} seconds\n\n"
        f":sparkles: [bold yellow]Generated description from base64:[/bold yellow]\n"
        f"{result_base64}",
        title="Result Base64 Image",
        border_style="bright_magenta"
    )
)
