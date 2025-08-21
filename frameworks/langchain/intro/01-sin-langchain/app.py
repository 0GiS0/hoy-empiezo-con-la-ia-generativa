# Módulos que necesito importar
import os
import sys
import unicodedata
from pathlib import Path
from urllib import response
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

# Configurar PYTHONPATH para imports absolutos (enfoque productivo)
repo_root = Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import absoluto
from frameworks.langchain.intro.common import Suggestions

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


# Pinta que tiene el esquema de Suggestions
print("\n[bold cyan]Esquema de salida esperado[/bold cyan]")
print(Suggestions.model_json_schema())

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

# Imprimir la respuesta
print("\n[bold green]Respuesta de la API de OpenAI[/bold green]")
print(response.choices[0].message.content)

# Y ahora parseada
print("\n[bold green]Respuesta parseada[/bold green]")
print(print(response.choices[0].message.parsed))

# Validar que el título y la longitud coinciden


def get_visible_length(text):
    """Cuenta solo caracteres visibles, excluyendo caracteres de control y formato Unicode"""
    visible_chars = 0
    for char in text:
        # Excluir caracteres de control y formato (como \u200d)
        if unicodedata.category(char) not in ('Cf', 'Cc', 'Mn'):
            visible_chars += 1
    return visible_chars


for suggestion in response.choices[0].message.parsed.suggestions:
    actual_length = len(suggestion.title)
    visible_length = get_visible_length(suggestion.title)
    reported_length = suggestion.length

    print(f"\n[bold cyan]Análisis de '{suggestion.title}':[/bold cyan]")
    print(f"  • Longitud total (len()): {actual_length}")
    print(f"  • Longitud visible: {visible_length}")
    print(f"  • Longitud reportada por modelo: {reported_length}")

    # Validar contra longitud visible (más preciso)
    if reported_length != visible_length:
        print(
            f"[bold red]Error de validación:[/bold red] La longitud visible ({visible_length}) no coincide con la reportada ({reported_length})")
        # Mostrar caracteres no visibles si los hay
        if actual_length != visible_length:
            non_visible = [f"\\u{ord(c):04x}" for c in suggestion.title if unicodedata.category(
                c) in ('Cf', 'Cc', 'Mn')]
            print(f"  • Caracteres no visibles encontrados: {non_visible}")
    else:
        print(
            f"[bold green]Validación exitosa:[/bold green] La longitud visible ({visible_length}) coincide con la reportada ({reported_length})")
