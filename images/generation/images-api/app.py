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
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Crear y configurar console de Rich
console = Console()

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Crear cliente de OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Prompt de ejemplo
prompt = """
    Una escena realista, con estilo cinematográfico, que muestra a una inteligencia artificial generando arte. 
    La IA está representada por un brazo robótico futurista que utiliza Microsoft Paint en una computadora clásica, 
    en lugar de un lienzo físico. En la pantalla del monitor se ve la interfaz característica de Microsoft Paint, 
    con herramientas y paletas de colores visibles, mientras la IA dibuja una imagen vibrante: mitad digital, mitad pintada a mano, 
    simbolizando la fusión entre tecnología y creatividad. Alrededor hay monitores que muestran prompts de generación de imágenes 
    y referencias coloridas. La iluminación es cálida y suave, con un leve resplandor que emana de la pantalla. 
    La IA está rodeada de bocetos, fotos de inspiración y moodboards digitales. El entorno es original, inspirador y con un espacio 
    vacío en uno de los lados de la pantalla para insertar la imagen o el logo del canal de YouTube.
     """

console.print(
    Panel.fit(
        f"⏳🖼️ [bold cyan]Generando imagen con el endpoint[/bold cyan] [bold magenta]/v1/images/generations[/bold magenta]."
        f"[bold cyan]Esto puede tardar unos segundos.[/bold cyan]\n\n"
        f"[bold yellow]Prompt:[/bold yellow]\n{prompt.strip()}",
        title="[bold green]OpenAI Images API[/bold green]"
    )
)

# Guardar el tiempo de inicio
start_time = time.time()

# Mostrar un spinner mientras se genera la imagen
with Progress(
    SpinnerColumn(spinner_name="dots"),
    TextColumn("[progress.description]{task.description}"),
    console=console,
) as progress:
    task = progress.add_task("[bold green]Generando imagen...", total=None)

# Llamada a la API para generar la imagen
response = client.images.generate(
    # model=os.getenv("IMAGE_GENERATION_MODEL"),
    model="gpt-image-1",  # Puedes usar "dall-e-2" o "dall-e-3" si lo prefieres
    prompt=prompt,
    size="1024x1024",  # También puedes usar "1024x1792" o "1792x1024"
    n=1,  # Número de imágenes a generar
)

# Actualizar el progreso al completar la tarea
progress.update(task, description="[bold green]Imagen generada con éxito![/bold green]")

# Guardar el tiempo de finalización
end_time = time.time()

# Decodificar la imagen generada desde base64
image_base64 = response.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Generar un número aleatorio entre 1000 y 9999
random_number = random.randint(1000, 9999)

# Guardar la imagen en un archivo
with open(f"image_generated_with_images-api.png", "wb") as f:
    f.write(image_bytes)

# Obtener la resolución de la imagen guardada
with Image.open(f"image_generated_with_images-api.png") as img:
    image_size = img.size
print(f"Resolución de la imagen: {image_size}")

# Imprimir el tiempo de ejecución
execution_time = end_time - start_time

console.print(
    Panel.fit(
        f"✅🖼️ [bold green]Imagen generada y guardada como[/bold green] [yellow]image_generated_with_images-api.png[/yellow]\n"
        f"⏱️ [bold]Tiempo de ejecución:[/bold] [cyan]{execution_time:.2f} segundos[/cyan]",
        border_style="green"
    )
)
# Mostrar la imagen generada
console.print(
    Panel.fit(
        f"[bold blue]Puedes encontrarla la imagen generada en el archivo[/bold blue] [yellow]image_generated_with_images-api.png[/yellow]",
        border_style="blue",      
        title="[bold green]Imagen Generada[/bold green]"
    )
)
