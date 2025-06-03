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
console = Console()

# Configurar el cliente de OpenAI con las variables de entorno
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)


# Analiza la imagen usando el endpoint de chat completions
def analizar_imagen(descripcion, prompt):
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), transient=True, console=console) as progress:
        progress.add_task(description=descripcion, total=None)
        start_time = time.time()

        # Llamada al endpoint de chat completions
        response = client.chat.completions.create(
            model=os.getenv("MODEL_FOR_VISION"),
            messages=prompt
        )

        end_time = time.time()
        elapsed = end_time - start_time
        return response.choices[0].message.content, elapsed


#### Analizar imagen por URL ####
prompt_with_url = [
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
description_url = "🔍 Analizando la imagen recuperada de una URL..."
resultado_url, tiempo_url = analizar_imagen(description_url, prompt_with_url)
console.print(
    Panel.fit(
        f":hourglass_flowing_sand: [green]Tiempo de respuesta:[/green] {tiempo_url:.2f} segundos\n\n"
        f":sparkles: [bold yellow]Descripción generada:[/bold yellow]\n"
        f"{resultado_url}",
        title="Resultado Imagen por URL",
        border_style="bright_blue"
    )
)

#### Analizar imagen en base64 ####
with open("/workspaces/hoy-empiezo-con-ia-generativa/images/vision/samples/IMG_2377.png", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

prompt_with_base64 = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "¿Qué ves en esta imagen en base64?"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
            }
        ]
    }
]

description_base64 = "🔍 Analizando imagen en base64..."
resultado_base64, tiempo_base64 = analizar_imagen(description_base64, prompt_with_base64)
console.print(
    Panel.fit(
        f":hourglass_flowing_sand: [green]Tiempo de respuesta:[/green] {tiempo_base64:.2f} segundos\n\n"
        f":sparkles: [bold yellow]Descripción generada desde base64:[/bold yellow]\n"
        f"{resultado_base64}",
        title="Resultado Imagen Base64",
        border_style="bright_magenta"
    )
)
