# Módulos que necesito importar
from ...common.models import Suggestions

from rich import print
from rich.console import Console

# Módulo de SDK de OpenAI
from openai import OpenAI

import os
from urllib import response
from dotenv import load_dotenv



# Instanciar una consola de rich
console = Console()

# Cargar las variables de entorno que necesito para esta demo
load_dotenv()

print("🚀 [bold cyan]Ejemplo sin Langchain ❌🦜🔗[/bold cyan]")
print(f"🌐 [magenta]URL:[/magenta] [white]{os.getenv('GITHUB_MODELS_URL')}[/]")
print(f"🧠 [magenta]Modelo:[/magenta] [white]{os.getenv('GITHUB_MODEL_ID')}[/]")
print(f"🎛️ [magenta]Temperatura:[/magenta] [white]{os.getenv('TEMPERATURE', '0.7')}[/]")
print(f"🎬 [magenta]Título original YouTube:[/magenta] [yellow]{os.getenv('YOUTUBE_TITLE')}[/]")

# Crear cliente de OpenAI (En este ejemplo uso GitHub Models porque es rápido y gratis)
client = OpenAI(
    base_url=os.getenv("GITHUB_MODELS_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
)


SYSTEM_MESSAGE = """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.
"""

# Llamar a la API de OpenAI para generar texto
print("\n⏳ [cyan]Llamando al modelo para generar sugerencias…[/cyan]")
try:
    response = client.chat.completions.parse(
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": os.getenv("YOUTUBE_TITLE")}
        ],
        model=os.getenv("GITHUB_MODEL_ID"),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        response_format=Suggestions
    )
    print("✅ [green]Respuesta recibida[/green]")
except Exception as e:
    print(f"🔥 [bold red]Error al llamar al modelo:[/bold red] {e}")
    exit(1)

# Recuperar las sugerencias
suggestions = response.choices[0].message.parsed

# Imprimir la respuesta cruda del modelo
print("\n🧪 [bold green]Respuesta generada[/bold green]")
print("[cyan]Lista de sugerencias:[/cyan]")
for idx, s in enumerate(suggestions.suggestions, start=1):
    color = "green" if s.length <= 55 else ("yellow" if s.length <= 65 else "red")
    print(
        f" {idx}. [bold yellow]{s.title}[/bold yellow]\n"
        f"    🔡 Longitud: [bold {color}]{s.length}[/] chars  | 😀 Emojis: [dim]{' '.join(s.emojis)}[/]"
    )

print("\n🏁 [bold cyan]Fin de la demo[/bold cyan]")
