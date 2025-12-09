# 📦 Imports generales: cargamos utilidades del entorno, LangChain y Rich
import json
import os
from textwrap import shorten

from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.callbacks import BaseCallbackHandler


from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from schema import Suggestions

# 🔐 Cargo las variables de entorno del .env para configurar el modelo
load_dotenv()


console = Console()


class RichToolLogger(BaseCallbackHandler):
    """🧭 Callback que actúa como middleware para monitorear las tools."""

    def __init__(self, console: Console):
        self.console = console

    def on_tool_start(self, serialized, input_str, **kwargs):
        # 🚀 Cuando una tool inicia, mostramos su nombre y los argumentos recibidos
        name = serialized.get("name", "tool") if isinstance(serialized, dict) else str(serialized)
        self.console.print(f"🛠️  [bold cyan]{name}[/] start", style="cyan")
        self.console.print(Panel(str(input_str), title="Tool input", border_style="cyan"))

    def on_tool_end(self, output, **kwargs):
        # ✅ Al terminar, registramos el resultado que la herramienta devolvió
        self.console.print(Panel(str(output), title="Tool output", border_style="green"))
        self.console.print("✅ Tool end\n", style="green")

    def on_tool_error(self, error, **kwargs):
        # ❌ Si ocurre un error, lo pintamos en rojo para detectarlo rápido
        self.console.print(Panel(str(error), title="Tool error", border_style="red"))


# 🔧 Helpers para validar y regenerar títulos con longitud máxima
def _normalize_title(text: str) -> str:
    return " ".join(text.split())


def _regenerate_title(text: str, max_length: int) -> str:
    candidate = shorten(text, width=max_length, placeholder="").strip()
    if candidate:
        return candidate
    candidate = text[:max_length].rstrip()
    return candidate


@tool
def validate_youtube_title(title: str, max_length: int = 70) -> str:
    """Valida la longitud del título y genera una versión <= max_length si hace falta."""
    # 🧼 Normalizamos para contar caracteres correctamente
    normalized = _normalize_title(title)
    length = len(title)

    if length <= max_length:
        payload = {
            "status": "valid",
            "title": normalized,
            "length": length,
        }
    else:
        regenerated = _regenerate_title(normalized, max_length)
        payload = {
            "status": "regenerated",
            "title": regenerated,
            "length": len(regenerated),
            "warn": f"Título original con {length} caracteres. Ajustado a {max_length}.",
        }

    return json.dumps(payload, ensure_ascii=False)


# 🤖 Definimos el modelo LLM que alimentará al agente
model = init_chat_model(
    model_provider=os.getenv("MODEL_PROVIDER"),
    model=os.getenv("MODEL_ID"),
    openai_api_base=os.getenv("ENDPOINT_URL"),
    openai_api_key=os.getenv("API_KEY"),
    # temperature=0.7
)


# 🧠 Prompt del sistema: instrucciones base que guían al agente
system_prompt = """
Eres un asistente especializado en crear títulos optimizados para YouTube 🎬.
Tu tarea principal es generar 5 opciones de títulos atractivos, creativos y relevantes.

➡️ Cuando generes títulos, cada uno debe:
- Ser claro y fácil de entender.
- Estar orientado a captar la atención (gancho).
- Reflejar fielmente el contenido del vídeo.
- Incluir siempre al menos un emoji para hacerlo más llamativo.

Tienes acceso a herramientas que puedes usar cuando sea necesario:
- validate_youtube_title: Cuenta los caracteres y ajusta títulos que superen el máximo permitido.

Si recibes una solicitud que no esté relacionada con la generación de títulos de YouTube,
puedes usar tus otras herramientas si son relevantes, o responder de manera útil.
"""

# 🧱 Preparamos una versión del modelo que devuelve la estructura `Suggestions`
structured_model = model.with_structured_output(Suggestions)

# 🧪 Ejecutar una consulta de prueba con una descripción base
user_input = """
¡Hola developer 👋🏻! Para este vídeo te voy a mostrar cómo empezar con Langchain,
desde un agente simple, pasando por uno con tools y demás a un flujo donde se involucren varios agentes.
"""

try:

    # 🎨 Cabecera bonita para entender qué demo estamos corriendo
    console.rule("[bold cyan]Agente de títulos para YouTube")
    console.print(
        f"🔗 Modelo: [bold]{os.getenv('MODEL_ID')}[/] · Proveedor: [bold]{os.getenv('MODEL_PROVIDER')}[/]\n")
    console.print(Panel(user_input.strip(),
                  title="Descripción del video", border_style="magenta"))
    console.print("⏳ Ejecutando agente...\n", style="yellow")

    # 📬 Preparamos la conversación para el modelo
    messages = [
        SystemMessage(system_prompt),
        HumanMessage(f"Crea títulos para YouTube basados en esta descripción: {user_input}"),
    ]

    suggestions_response = structured_model.invoke(messages)

    # 🧩 Enganchamos nuestro logger para observar cómo la tool valida cada título
    callbacks = [RichToolLogger(console)]
    validated = []

    for suggestion in suggestions_response.suggestions:
        raw = validate_youtube_title.invoke(
            {"title": suggestion.title, "max_length": 70},
            config={"callbacks": callbacks},
        )
        data = json.loads(raw)
        validated.append(
            {
                "title": data["title"],
                "length": data["length"],
                "emojis": suggestion.emojis,
                "status": data["status"],
            }
        )

    # 📨 Mostramos la respuesta validada
    console.print("✅ [green]Respuesta recibida[/green]\n")
    console.print(Rule(style="dim"))

    for idx, s in enumerate(validated, start=1):
        # 📋 Listamos cada título sugerido en consola con su longitud y emojis
        emojis = " ".join(s["emojis"]) if s["emojis"] else "—"
        status = "🆗" if s["status"] == "valid" else "♻️"
        console.print(
            f"  {idx}. {status} [bold yellow]{s['title']}[/]"
            f"\n     🔡 Longitud: [green]{s['length']}[/] · 😀 Emojis: [magenta]{emojis}[/]\n"
        )

except Exception as e:
    # 🧯 Capturamos cualquier excepción y la mostramos claramente
    console.print(Panel(str(e), title="Error", border_style="red")) 