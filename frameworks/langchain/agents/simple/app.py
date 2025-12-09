# Imports generales
import os

from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import SystemMessage, HumanMessage
from langchain.agents.structured_output import ToolStrategy
from langchain_core.callbacks import BaseCallbackHandler


from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from schema import Suggestions

# Cargo las variables de entorno del .env
load_dotenv()


console = Console()


class RichToolLogger(BaseCallbackHandler):
    def __init__(self, console: Console):
        self.console = console

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = serialized.get("name", "tool") if isinstance(serialized, dict) else str(serialized)
        self.console.print(f"🛠️  [bold cyan]{name}[/] start", style="cyan")
        self.console.print(Panel(str(input_str), title="Tool input", border_style="cyan"))

    def on_tool_end(self, output, **kwargs):
        self.console.print(Panel(str(output), title="Tool output", border_style="green"))
        self.console.print("✅ Tool end\n", style="green")

    def on_tool_error(self, error, **kwargs):
        self.console.print(Panel(str(error), title="Tool error", border_style="red"))


@tool
def create_youtube_titles(description: str) -> str:
    """Crea 5 títulos optimizados para YouTube basados en una descripción."""
    # Esta es una función de ejemplo, en la práctica podrías usar APIs o lógica más compleja
    base_titles = [
        f"🔥 {description[:30]}... ¡INCREÍBLE!",
        f"✨ Cómo {description[:35]}... paso a paso",
        f"🚀 {description[:40]}... ¡TUTORIAL!",
        f"💡 {description[:30]}... ¡Te va a sorprender!",
        f"⚡ {description[:35]}... ¡FÁCIL y RÁPIDO!"
    ]
    return "\n".join([f"{i+1}. {title}" for i, title in enumerate(base_titles)])


# Definir el modelo que vamos a usar para crear el agente
model = init_chat_model(
    model_provider=os.getenv("MODEL_PROVIDER"),
    model=os.getenv("MODEL_ID"),
    openai_api_base=os.getenv("ENDPOINT_URL"),
    openai_api_key=os.getenv("API_KEY"),
    # temperature=0.7
)


# Crear el prompt del sistema para el agente
system_prompt = """
Eres un asistente especializado en crear títulos optimizados para YouTube 🎬.
Tu tarea principal es generar 5 opciones de títulos atractivos, creativos y relevantes.

➡️ Cuando generes títulos, cada uno debe:
- Ser claro y fácil de entender.
- Estar orientado a captar la atención (gancho).
- Reflejar fielmente el contenido del vídeo.
- Usar un máximo de 70 caracteres.
- Incluir siempre al menos un emoji para hacerlo más llamativo.

Si recibes una solicitud que no esté relacionada con la generación de títulos de YouTube,
puedes usar tus otras herramientas si son relevantes, o responder de manera útil.
"""

# Crear el agente
agent = create_agent(
    model=model,
    tools=[create_youtube_titles],
    system_prompt=SystemMessage(
        content=[{"type": "text", "text": system_prompt}]),
    response_format=ToolStrategy(Suggestions),
)

# Ejecutar una consulta
user_input = """
¡Hola developer 👋🏻! Para este vídeo te voy a mostrar cómo empezar con Langchain,
desde un agente simple, pasando por uno con tools y demás a un flujo donde se involucren varios agentes.
"""

try:

    console.rule("[bold cyan]Agente de títulos para YouTube")
    console.print(
        f"🔗 Modelo: [bold]{os.getenv('MODEL_ID')}[/] · Proveedor: [bold]{os.getenv('MODEL_PROVIDER')}[/]\n")
    console.print(Panel(user_input.strip(),
                  title="Descripción del video", border_style="magenta"))
    console.print("⏳ Ejecutando agente...\n", style="yellow")

    callbacks = [RichToolLogger(console)]

    result = agent.invoke(
        {"messages": [
            HumanMessage(f"Crea títulos para YouTube basados en esta descripción: {user_input}")
        ]},
        config={"callbacks": callbacks},
    )

    console.print("✅ [green]Respuesta recibida[/green]\n")
    console.print(Rule(style="dim"))

    # print(result["structured_response"])

    suggestions = result["structured_response"].suggestions

    for idx, s in enumerate(suggestions, start=1):
        console.print(f"  {idx}. {s}")

except Exception as e:
    console.print(Panel(str(e), title="Error", border_style="red")) 