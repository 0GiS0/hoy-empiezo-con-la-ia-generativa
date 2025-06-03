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

# Generate a mask image
prompt_mask = """
Genera una imagen de máscara que cubra el caracol azul que aparece en la imagen.
Usando blanco donde está el caracol
"""

print("[cyan]🖼️ Abriendo imagen de entrada...[/cyan]")
img_input = open(
    "/workspaces/hoy-empiezo-con-ia-generativa/final_frog_snail_and_butterfly.png", "rb")

print("[cyan]🎨 Generando la máscara...[/cyan]")
# Generate the mask
result_mask = client.images.edit(
    model="gpt-image-1",
    image=img_input,
    prompt=prompt_mask
)

# Save the mask image
print("[cyan]💾 Decodificando y guardando la máscara como mask_image.png...[/cyan]")
image_base64 = result_mask.data[0].b64_json

print(image_base64)

# print(f"🖤 Background: {result_mask.data[0].background}")
# print(f"✨ Quality: {result_mask.data[0].quality}")
# print(f"📏 Size: {result_mask.data[0].size}")

image_bytes = base64.b64decode(image_base64)

with open("mask_image.png", "wb") as f:
    f.write(image_bytes)

elapsed_time = time.time() - start_time
print(
    f"[bold green]🎉 Proceso completado en {elapsed_time:.2f} segundos.[/bold green]")


# Alpha channel
# 1. Load your black & white mask as a grayscale image
mask = Image.open("mask_image.png").convert("L")

# 2. Convert it to RGBA so it has space for an alpha channel
mask_rgba = mask.convert("RGBA")

# 3. Then use the mask itself to fill that alpha channel
mask_rgba.putalpha(mask)

# 4. Convert the mask into bytes
buf = BytesIO()
mask_rgba.save(buf, format="PNG")
mask_bytes = buf.getvalue()

# Save the resulting file
img_path_mask_alpha = "mask_alpha.png"
with open(img_path_mask_alpha, "wb") as f:
    f.write(mask_bytes)


# Reemplazar en la imagen original la parte del caracol con la máscara generada poniendo en su lugar una seta roja con puntos blancos.

prompt_replace = """
Sustituye únicamente el caracol azul en la imagen por algo divertido, 
asegurándote de que solo el caracol sea reemplazado y el fondo, 
la rana y la mariposa permanezcan exactamente igual que en la imagen original.
"""

mask = open("mask_alpha.png", "rb")



print("[cyan]🎨 Generando la imagen editada...[/cyan]")

result_mask_edit = client.images.edit(
    model="gpt-image-1",
    prompt=prompt_replace,
    image=img_input,
    mask=mask,
    size="1024x1024"
)

# Save the edited image
print("[cyan]💾 Decodificando y guardando la imagen editada como edited_image.png...[/cyan]")
image_base64_edit = result_mask_edit.data[0].b64_json

image_bytes_edit = base64.b64decode(image_base64_edit)

with open("edited_image.png", "wb") as f:
    f.write(image_bytes_edit)

print("[bold green]🎉 Imagen editada guardada como edited_image.png.[/bold green]")
