from openai import OpenAI
import base64
import os
from dotenv import load_dotenv
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

# Modelo de IA a utilizar
MODEL_NAME = "gpt-image-1"

# Directorio de salida para las imágenes generadas
output_file = "/workspaces/hoy-empiezo-con-ia-generativa/images/generation/images-api/example_output/composition.png"

# Cargar variables de entorno desde un archivo .env
print("[bold cyan]🚀 Cargando variables de entorno...[/bold cyan]")
load_dotenv()

# Crear cliente de OpenAI
print("[bold cyan]🤖 Creando cliente de OpenAI...[/bold cyan]")
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

prompt = """
Genera una foto realista donde los personajes de las imágenes están juntos en una cesta.
"""

start_time = time.time()

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
    progress.add_task(
        description="[bold magenta]📡 Enviando solicitud de generación de imagen a la API...[/bold magenta]", total=None)
    response = client.images.edit( 
        model=MODEL_NAME, # Solo soporta gpt-image-1 y dall-e-2
        image=[
            open("/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/no-fail/figure-1.png", "rb"),
            open("/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/no-fail/figure-2.png", "rb"),
            open("/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/no-fail/figure-3.png", "rb"),
        ],
        prompt=prompt
    )

# Guardar el tiempo de finalización
end_time = time.time()

# Decodificar la imagen generada desde base64
image_base64 = response.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Guardar la imagen en un archivo
with open(f"{output_file}", "wb") as f:
    f.write(image_bytes)
