# Módulos que necesito importar
from ..common.models import Suggestions

import os
import json
from urllib import response
from dotenv import load_dotenv
from openai import OpenAI
from rich import print
from rich.json import JSON
from rich.console import Console

# Instanciar una consola de rich
console = Console()

# Cargar las variables de entorno que necesito para esta demo
load_dotenv()

# Pintar la configuración (sin la clave)
print("[bold cyan]Configuración de la API de OpenAI[/bold cyan]")
print(f"[magenta]URL:[/magenta] {os.getenv('GITHUB_MODELS_URL')}")
print(f"[magenta]Modelo:[/magenta] {os.getenv('GITHUB_MODEL_ID')}")
print(f"[magenta]Temperatura:[/magenta] {os.getenv('TEMPERATURE', '0.7')}")
print(f"[magenta]Título de YouTube:[/magenta] {os.getenv('YOUTUBE_TITLE')}")

# Crear cliente de OpenAI (En este ejemplo uso GitHub Models porque es rápido y gratis)
client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)


# Modelo importados desde models.py

system_message = """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.
"""

# Llamar a la API de OpenAI para generar texto
try:
    response = client.chat.completions.parse(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": os.getenv("YOUTUBE_TITLE")}
        ],
        model=os.getenv("GITHUB_MODEL_ID"),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        response_format=Suggestions
    )
except Exception as e:
    print(f"[bold red]Error:[/bold red] {e}")
    exit(1)

# Recuperar las sugerencias
suggestions = response.choices[0].message.parsed

# Imprimir la respuesta cruda del modelo
print("\n[bold green]Respuesta del modelo (cruda)[/bold green]")
print(suggestions)
