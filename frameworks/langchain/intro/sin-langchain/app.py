# Módulos que necesito importar
import os
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

# Cargar las variables de entorno que necesito para esta demo
load_dotenv()

# Pintar la configuración (sin la clave)
print("[bold cyan]Configuración de la API de OpenAI[/bold cyan]")
print(f"[magenta]URL:[/magenta] {os.getenv('GITHUB_MODELS_URL')}")
print(f"[magenta]Modelo:[/magenta] {os.getenv('GITHUB_MODEL_ID')}")
print(f"[magenta]Título de YouTube:[/magenta] {os.getenv('YOUTUBE_TITLE')}")

# Crear cliente de OpenAI
# En este ejemplo uso GitHub Models porque es rápido y gratis
client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)

system_message = """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.

Instrucciones del output:
- Devuelve exactamente 5 títulos en español.
- Que aparezcan en un formato listado.
- 55–70 caracteres por título (ideal ≤ 65); si no es viable, prioriza claridad y valor.
- Incluye 1–2 emojis relevantes por título; evita colocarlos al inicio.
- Identifica e integra la palabra clave principal del tema y, cuando encaje, una variación breve.
- Varía las fórmulas entre: beneficio claro, cómo/guía/truco, lista con número, sorpresa/curiosidad, urgencia/tiempo.
- Evita MAYÚSCULAS SOSTENIDAS, clickbait engañoso y afirmaciones dudosas.
- Mantén el significado e intención del título original.

Entrega únicamente los 5 títulos, nada más.
"""

# Llamar a la API de OpenAI para generar texto
response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": os.getenv("YOUTUBE_TITLE")}
    ],
    model=os.getenv("GITHUB_MODEL_ID"),
)

# Imprimir la respuesta
print("\n[bold green]Respuesta de la API de OpenAI[/bold green]")
print(response.choices[0].message.content)
