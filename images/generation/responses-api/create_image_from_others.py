from openai import OpenAI
import base64
import os
from dotenv import load_dotenv
from rich import print

# Load environment variables from a .env file
print("[bold cyan]🚀 Cargando variables de entorno...[/bold cyan]")
load_dotenv()

# Create OpenAI client
print("[bold cyan]🤖 Creando cliente de OpenAI...[/bold cyan]")
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

prompt = """
Genera una foto realista donde la llama esté utilizando el portatil y este tenga Visual Studio Code abierto.
Asegúrate de que la llama esté claramente visible y que el entorno sea natural, con detalles como hojas y ramas alrededor. 
La imagen debe transmitir una sensación de calma y curiosidad.
"""

def encode_image(file_path):
    print(f"[yellow]🖼️ Codificando imagen:[/yellow] {file_path}")
    with open(file_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    return base64_image

print("[bold cyan]🖼️ Codificando imágenes de entrada...[/bold cyan]")
base64_image1 = encode_image(
    "/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/llama.jpg")
base64_image2 = encode_image(
    "/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/Surface laptop.webp")
base64_image3 = encode_image(
    "/workspaces/hoy-empiezo-con-ia-generativa/images/image-for-demos/composition/visual studio code logo.png")

print("[bold cyan]📡 Enviando solicitud de generación de imagen a la API...[/bold cyan]")
response = client.responses.create(
    model=os.getenv("IMAGE_GENERATION_MODEL"),
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image1}",
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/webp;base64,{base64_image2}",
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

print("[bold cyan]🔄 Procesando respuesta de la API...[/bold cyan]")
image_generation_calls = [
    output
    for output in response.output
    if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    print("[green]✅ Imagen generada correctamente. Guardando archivo...[/green]")
    image_base64 = image_data[0]
    with open("image_from_others.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
    print("[bold green]💾 Imagen guardada como image_from_others.png[/bold green]")
else:
    print("[red]❌ No se generó ninguna imagen. Respuesta de la API:[/red]")
    print(response.output.content)
