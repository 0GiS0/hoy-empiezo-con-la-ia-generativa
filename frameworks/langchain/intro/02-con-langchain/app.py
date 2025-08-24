# Módulos que necesito importar
from ..common.models import Suggestions
from rich import print
from rich.json import JSON
from rich.console import Console
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os

# Instancia de Console, para pintar el output bonito
console = Console()

# Cargar las variables de entorno que necesito para esta demo
load_dotenv()

# Pintar la configuración (sin la clave)
print("[bold cyan]Configuración de la API de OpenAI[/bold cyan]")
print(f"[magenta]URL:[/magenta] {os.getenv('GITHUB_MODELS_URL')}")
print(f"[magenta]Modelo:[/magenta] {os.getenv('GITHUB_MODEL_ID')}")
print(f"[magenta]Temperatura:[/magenta] {os.getenv('TEMPERATURE', '0.7')}")
print(f"[magenta]Título de YouTube:[/magenta] {os.getenv('YOUTUBE_TITLE')}")

# Modelo chat con Langchain
model = init_chat_model(
    model=os.getenv("GITHUB_MODEL_ID"),
    model_provider="openai",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url=os.getenv("GITHUB_MODELS_URL"),
    # temperature=float(os.getenv("TEMPERATURE", "0.7")),
)


# Parser pydantic para forzar el formato
parser = PydanticOutputParser(pydantic_object=Suggestions)

# Añadir la salida estructurada
model_with_structured_output = model.with_structured_output(
    parser.get_output_schema())


# Mensaje del sistema, para que sepa qué es lo que esperamos
system_message = (
    """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.
"""
)

# Preparar mensajes a enviar al modelo
messages = [
    SystemMessage(system_message),
    HumanMessage("Título original: {title}")
]

# Ejecutar la cadena con la variable de entrada
suggestions = model_with_structured_output.invoke(
    messages, {"title": os.getenv("YOUTUBE_TITLE")})

# Imprimir la respuesta cruda del modelo
print("\n[bold green]Respuesta del modelo (cruda)[/bold green]")
print(suggestions)
