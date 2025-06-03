from openai import OpenAI
import base64
import os
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Output directory for generated images
output_path = "/workspaces/hoy-empiezo-con-ia-generativa/images/generation/responses-api/example_output/composition.png"

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

def encode_image(file_path):
    print(f"[yellow]🖼️ Codificando imagen:[/yellow] {file_path}")
    with open(file_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    return base64_image

# Codificar imágenes de entrada
print("[bold cyan]🖼️ Codificando imágenes de entrada...[/bold cyan]")
base64_image1 = encode_image(
    "/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/no-fail/figure-1.png")
base64_image2 = encode_image(
    "/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/no-fail/figure-2.png")
base64_image3 = encode_image(
    "/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/no-fail/figure-3.png")

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
    progress.add_task(description="📡 Enviando solicitud de generación de imagen a la API...", total=None)
    response = client.responses.create(
        model=os.getenv("IMAGE_GENERATION_MODEL"),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_image1}",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_image2}",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_image3}",
                    },

                ],
            }
        ],
        tools=[{"type": "image_generation"}],
    )

# Procesar respuesta de la API
print("[bold cyan]🔄 Procesando respuesta de la API...[/bold cyan]")
image_generation_calls = [
    output
    for output in response.output
    if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    # Guardar la imagen generada
    print("[green]✅ Imagen generada correctamente. Guardando archivo...[/green]")
    image_base64 = image_data[0]
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_base64))
    print(f"[bold green]💾 Imagen guardada como {output_path}[/bold green]")
else:
    print("[red]❌ No se generó ninguna imagen. Respuesta de la API:[/red]")
    print(response.output.content)
