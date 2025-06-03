from io import BytesIO
from openai import OpenAI
import os
from dotenv import load_dotenv
from rich import print
from rich.console import Console
import time
import base64
from rich.panel import Panel
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Imagen que vamos a editar
input_image_file = "/workspaces/hoy-empiezo-con-ia-generativa/images/generation/responses-api/example_output/final_frog_snail_and_butterfly.png"

# Output directory for generated images
output_path = "/workspaces/hoy-empiezo-con-ia-generativa/images/generation/images-api/example_output"

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
Usando blanco donde está el caracol
"""

img_input = open(
    input_image_file, "rb")

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    TimeElapsedColumn(),
    transient=True
) as progress:
    progress.add_task(description=f"🎨 Generando la máscara de la imagen {input_image_file}...", total=None)
    result_mask = client.images.edit(
        model="gpt-image-1",
        image=img_input,
        prompt=prompt_mask
    )

# Guardar la imagen de la máscara
print("[cyan]💾 Decodificando y guardando la máscara como mask_image.png...[/cyan]")
image_base64 = result_mask.data[0].b64_json

# print(image_base64)

image_bytes = base64.b64decode(image_base64)

with open(f"{output_path}/mask_image.png", "wb") as f:
    f.write(image_bytes)

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

prompt_replace = """
Sustituye únicamente el caracol azul en la imagen por algo divertido, 
asegurándote de que solo el caracol sea reemplazado y el fondo, 
la rana y la mariposa permanezcan exactamente igual que en la imagen original.
"""

mask = open(f"{output_path}/mask_alpha.png", "rb")
# mask = open(f"{output_path}/mask_image.png", "rb")

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    TimeElapsedColumn(),
    transient=True
) as progress:
    progress.add_task(description="🎨 Editando imagen con máscara...", total=None)
    result_mask_edit = client.images.edit(
        model="gpt-image-1",
        prompt=prompt_replace,
        image=img_input,
        mask=mask,
        size="auto"
    )

# Guardar la imagen editada
print("[cyan]💾 Decodificando y guardando la imagen editada como edited_image.png...[/cyan]")
image_base64_edit = result_mask_edit.data[0].b64_json

image_bytes_edit = base64.b64decode(image_base64_edit)

with open(f"{output_path}/edited_image.png", "wb") as f:
    f.write(image_bytes_edit)

print("[bold green]🎉 Imagen editada guardada como edited_image.png.[/bold green]")
