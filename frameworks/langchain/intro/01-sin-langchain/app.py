# Módulos que necesito importar
import os
import sys
from pathlib import Path
import json
from urllib import response
from dotenv import load_dotenv
from openai import OpenAI
from rich import print
from rich.json import JSON
from rich.console import Console

# Configurar PYTHONPATH para imports absolutos (enfoque productivo)
repo_root = Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import absoluto
from frameworks.langchain.intro.common import Suggestions, build_validation_table

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

# Definir cómo quiero que sea la salida de la llamada
# system_message = """
# Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
# Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.

# Instrucciones del output:
# - Devuelve exactamente 5 títulos en español.
# - Que aparezcan en un formato listado.
# - 55–70 caracteres por título (ideal ≤ 65); si no es viable, prioriza claridad y valor.
# - Incluye 1–2 emojis relevantes por título; evita colocarlos al inicio.
# - Identifica e integra la palabra clave principal del tema y, cuando encaje, una variación breve.
# - Varía las fórmulas entre: beneficio claro, cómo/guía/truco, lista con número, sorpresa/curiosidad, urgencia/tiempo.
# - Evita MAYÚSCULAS SOSTENIDAS, clickbait engañoso y afirmaciones dudosas.
# - Mantén el significado e intención del título original.
# - Entrega únicamente los 5 títulos, nada más.
# """


# Modelo importados desde models.py

system_message = """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.
"""


# Pinta el esquema de salida (bonito)
print("\n[bold cyan]Esquema de salida esperado[/bold cyan]")
print(JSON.from_data(Suggestions.model_json_schema(), indent=2))

# Llamar a la API de OpenAI para generar texto
# response = client.chat.completions.create(
try:
    response = client.chat.completions.parse(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": os.getenv("YOUTUBE_TITLE")}
        ],
        model=os.getenv("GITHUB_MODEL_ID"),
        # temperature=float(os.getenv("TEMPERATURE", "0.7")),
        response_format=Suggestions
    )
except Exception as e:
    print(f"[bold red]Error:[/bold red] {e}")
    exit(1)

# Imprimir la respuesta cruda y la parseada (bonito)
print("\n[bold green]Respuesta de la API de OpenAI (cruda)[/bold green]")
print(response.choices[0].message.content)

# Y ahora parseada como JSON legible
print("\n[bold green]Respuesta parseada (JSON)[/bold green]")
parsed = response.choices[0].message.parsed
try:
    parsed_json = parsed.model_dump()  # Pydantic v2
except Exception:
    # Fallback defensivo si cambia la versión
    parsed_json = json.loads(parsed.json())
print(JSON.from_data(parsed_json, indent=2))

# Validación y tabla compartida
console = Console()
table, mismatches = build_validation_table(parsed.suggestions)
print("\n[bold cyan]Resumen de sugerencias[/bold cyan]")
console.print(table)
if mismatches:
    print("[yellow]\nAviso:[/yellow] Se detectaron discrepancias entre longitud visible y reportada. ")
    print("Puede deberse a caracteres no visibles (marcas Unicode). Revisa la tabla y el JSON parseado.")
