from io import BytesIO
from openai import OpenAI
import os
from dotenv import load_dotenv
from rich import print
from rich.console import Console
import time
import base64
from PIL import Image
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Imagen que vamos a editar
input_image_file = "/workspaces/hoy-empiezo-con-ia-generativa/images/generation/responses-api/example_output/final_frog_snail_and_butterfly.png"

# Output directory for generated images
output_path = "/workspaces/hoy-empiezo-con-ia-generativa/images/generation/responses-api/example_output"

# Cargar variables de entorno desde un archivo .env
load_dotenv()
console = Console()

# Crear cliente de OpenAI
print("[cyan]🤖 Creando cliente de OpenAI...[/cyan]")
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Iniciar medición de tiempo
start_time = time.time()

# Generar una imagen de máscara
prompt_mask = """
Genera una imagen de máscara que cubra el caracol azul que aparece en la imagen.
Usando blanco donde está el caracol. El fondo y el resto de la imagen deben permanecer intactos.
Asegúrate de que la máscara sea precisa y cubra únicamente el caracol.
"""

with open(input_image_file, "rb") as img_input:
    base64_input_image = base64.b64encode(img_input.read()).decode("utf-8")

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    TimeElapsedColumn(),
    transient=True
) as progress:
    progress.add_task(
        description=f"[bold magenta]🎨 Generando la máscara de la imagen [/bold magenta][bold yellow]{input_image_file}[/bold yellow]\n[bold blue]🧠 Modelo: {os.getenv('IMAGE_GENERATION_MODEL')} [/bold blue]", total=None)
    result_mask = client.responses.create(
        model=os.getenv("IMAGE_GENERATION_MODEL"),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt_mask},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_input_image}",
                    },
                ],
            }
        ],
        tools=[{"type": "image_generation"}],
    )

# Procesar respuesta de la API para la máscara
image_generation_calls = [
    output
    for output in result_mask.output
    if output.type == "image_generation_call"
]
image_data = [output.result for output in image_generation_calls]

# Guardar la imagen de la máscara
print("[cyan]💾 Decodificando y guardando la máscara como mask_image.png...[/cyan]")
# Procesar respuesta de la API
print("[bold cyan]🔄 Procesando respuesta de la API...[/bold cyan]")
image_generation_calls = [
    output
    for output in result_mask.output
    if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

def save_base64_image(image_base64: str, path: str) -> None:
    """Decodifica y guarda una imagen base64 en el path indicado."""
    try:
        with open(path, "wb") as f:
            f.write(base64.b64decode(image_base64))
        print(f"[bold green]💾 Imagen guardada como {path}[/bold green]")
    except Exception as e:
        print(f"[red]❌ Error guardando la imagen: {e}[/red]")

if image_data:
    print("[green]✅ Imagen generada correctamente. Guardando archivo...[/green]")
    image_base64 = image_data[0]
    save_base64_image(image_base64, f"{output_path}/mask_image.png")
else:
    print("[red]❌ No se generó ninguna imagen para la máscara.[/red]")

elapsed_time = time.time() - start_time
print(
    f"[bold green]🎉 Proceso completado en {elapsed_time:.2f} segundos.[/bold green]")


# Canal alfa
# 1. Cargar tu máscara en blanco y negro como imagen en escala de grises
mask = Image.open(f"{output_path}/mask_image.png").convert("L")

# 2. Convertirla a RGBA para que tenga espacio para un canal alfa
mask_rgba = mask.convert("RGBA")

# 3. Usar la propia máscara para rellenar ese canal alfa
mask_rgba.putalpha(mask)

# 4. Convertir la máscara en bytes
buf = BytesIO()
mask_rgba.save(buf, format="PNG")
mask_bytes = buf.getvalue()

# Guardar el archivo resultante
img_path_mask_alpha = f"{output_path}/mask_alpha.png"
with open(img_path_mask_alpha, "wb") as f:
    f.write(mask_bytes)


# Reemplazar en la imagen original la parte del caracol con la máscara generada poniendo en su lugar una seta roja con puntos blancos.

# Variable para definir con qué queremos reemplazar el caracol
replacement_object = "un Pokemón"

prompt_replace = f"""
Sustituye únicamente el caracol azul en la imagen por {replacement_object}, 
asegurándote de que solo el caracol sea reemplazado y el fondo, 
la rana y la mariposa permanezcan exactamente igual que en la imagen original.
"""

with open(f"{output_path}/mask_alpha.png", "rb") as mask:
    base64_mask = base64.b64encode(mask.read()).decode("utf-8")

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    TimeElapsedColumn(),
    transient=True
) as progress:
    progress.add_task(
        description=f"[bold bright_cyan]🎨 Editando imagen con máscara...[/bold bright_cyan]\n\n[bold blue]🧠 Modelo: {os.getenv('IMAGE_GENERATION_MODEL')} [/bold blue]", total=None)
    result_mask_edit = client.responses.create(
        model=os.getenv("IMAGE_GENERATION_MODEL"),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt_replace},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_input_image}",
                    },
                ],
            }
        ],
        tools=[{
            "type": "image_generation",
            "input_image_mask": { # en este caso la tool recibe una máscara
                "image_url": f"data:image/png;base64,{base64_mask}"
            }
        }]
    )

# Procesar respuesta de la API para la imagen editada
image_generation_calls = [
    output
    for output in result_mask_edit.output
    if output.type == "image_generation_call"
]
image_data = [output.result for output in image_generation_calls]

# Guardar la imagen editada
print("[cyan]💾 Decodificando y guardando la imagen editada como edited_image.png...[/cyan]")
# Procesar respuesta de la API
image_generation_calls = [
    output
    for output in result_mask_edit.output
    if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    print("[green]✅ Imagen generada correctamente. Guardando archivo...[/green]")
    image_base64 = image_data[0]
    save_base64_image(image_base64, f"{output_path}/edited_image.png")
else:
    print("[red]❌ No se generó ninguna imagen editada.[/red]")