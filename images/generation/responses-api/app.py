"""
Esta API es mejor cuando quieres generar imágenes como parte de una conversación.
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

output_path = "/workspaces/hoy-empiezo-con-ia-generativa/images/generation/responses-api/example_output"

# Configura la consola de rich
console = Console()

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Crea el cliente de OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

start_time = time.time()

prompt = """
Genera una imagen hiperrealista y detallada de un caracol de cristal azul y una rana de cristal verde, que se note claramente que son de cristal, ambos situados juntos sobre un lecho de hojas y musgo en un entorno natural iluminado suavemente. 
Asegúrate de que el caracol y la rana sean claramente visibles, con texturas realistas de cristal, y que el fondo muestre vegetación y elementos naturales como piedras o ramas. 
La composición debe transmitir tranquilidad y resaltar los colores azul y verde de los animales.
"""

console.print(Panel.fit(
    "⏳🖼️ [bold cyan]Generando la primera imagen (caracol y rana de cristal)...[/bold cyan]\nEsto puede tardar unos segundos.", border_style="cyan"))

# Genera la primera imagen
with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
    progress.add_task(description="Generando imagen...", total=None)
    response = client.responses.create(
        model=os.getenv("IMAGE_GENERATION_MODEL"),
        input=prompt,
        tools=[{"type": "image_generation"}],
    )

end_time = time.time()

# Genera un número aleatorio entre 1000 y 9999
random_number = random.randint(1000, 9999)

# Guarda la imagen en un archivo
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    filename = f"{output_path}/first_image.png"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(image_base64))
    console.print(Panel.fit(
        f"✅🖼️ [bold green]Imagen generada y guardada como[/bold green] [yellow]{filename}[/yellow]", border_style="green"))
else:
    console.print(Panel.fit(
        "❌🚫 [bold red]No se pudo generar la primera imagen.[/bold red]", border_style="red"))

# Imprime el tiempo de ejecución
execution_time = end_time - start_time
console.print(
    f"⏱️ [bold]Tiempo de ejecución de la primera generación:[/bold] [cyan]{execution_time:.2f} segundos[/cyan]")

# Segunda generación: añade una mariposa amarilla
console.print(Panel.fit(
    "⏳🦋 [bold magenta]Generando la segunda imagen (añadiendo mariposa amarilla)...[/bold magenta]\nEspera mientras se procesa la petición.", border_style="magenta"))
with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
    progress.add_task(description="Generando imagen...", total=None)
    second_response = client.responses.create(
        previous_response_id=response.id,
        model=os.getenv("IMAGE_GENERATION_MODEL"),
        input=(
            "Añade una mariposa de color amarillo, con alas abiertas también de cristal, se tiene que notar claramente, "
            "posada suavemente sobre una hoja cerca del caracol y la rana. "
            "Asegúrate de que la mariposa destaque en la composición, manteniendo la iluminación suave y el entorno natural, "
            "y que todos los elementos conserven un aspecto hiperrealista y armonioso."
        ),
        tools=[{"type": "image_generation"}],
    )

# Guarda la segunda imagen
second_image_data = [
    output.result
    for output in second_response.output
    if output.type == "image_generation_call"
]

if second_image_data:
    second_image_base64 = second_image_data[0]
    filename2 = f"{output_path}/second_image.png"
    with open(filename2, "wb") as f:
        f.write(base64.b64decode(second_image_base64))
    console.print(Panel.fit(
        f"✅🦋 [bold green]Segunda imagen generada y guardada como[/bold green] [yellow]{filename2}[/yellow]", border_style="green"))
else:
    console.print(Panel.fit(
        "❌🚫 [bold red]No se pudo generar la segunda imagen.[/bold red]", border_style="red"))

# Tercera generación: escena completamente realista en un bosque
console.print(Panel.fit(
    "⏳🌳 [bold blue]Generando la tercera imagen (escena completamente realista en un bosque)...[/bold blue]\nPor favor, espera.", border_style="blue"))
third_response_stream = client.responses.create(
    previous_response_id=second_response.id,
    model=os.getenv("IMAGE_GENERATION_MODEL"),
    input=(
        "Transforma la escena para que tanto el caracol, la rana y la mariposa tengan un aspecto completamente realista, "
        "que dejen de ser de escayola y se conviertan en animales vivos, "
        "con detalles naturales en sus texturas y colores. Cambia el fondo a un bosque frondoso y realista, "
        "con árboles, hojas y luz filtrada entre las ramas, manteniendo la composición armoniosa y la iluminación suave. "
        "Asegúrate de que los animales se integren perfectamente en el entorno natural del bosque."
    ),
    stream=True,
    tools=[{"type": "image_generation", "partial_images": 2}],
)

console.print(
    "🔄🌲 [bold green]Generando la tercera imagen (escena completamente realista en un bosque)... Esto puede tardar un poco.[/bold green]")

# Guarda las imágenes parciales y la imagen final
for partial_image in third_response_stream:
    if partial_image.type == "response.image_generation_call.partial_image":
        index = partial_image.partial_image_index
        image_base64 = partial_image.partial_image_b64
        image_bytes = base64.b64decode(image_base64)
        # Si es la última imagen parcial, guárdala con el nombre final
        if index == 2:
            filename = f"{output_path}/final_frog_snail_and_butterfly.png"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            console.print(
                f"🖼️ [bold green]Imagen final generada:[/bold green] [cyan]{filename}[/cyan]")
        else:
            filename = f"{output_path}/partial_image_{index}.png"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            console.print(
                f"🖼️ [bold yellow]Imagen parcial generada:[/bold yellow] [cyan]{filename}[/cyan]")
