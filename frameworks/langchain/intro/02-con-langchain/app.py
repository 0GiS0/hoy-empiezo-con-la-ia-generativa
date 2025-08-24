"""Versión con LangChain del ejemplo de 01-sin-langchain/app.py.
Mantiene el mismo caso de uso, esquema Pydantic compartido y validaciones.
"""

# Módulos que necesito importar
from frameworks.langchain.intro.common import Suggestions, build_validation_table
from rich import print
from rich.json import JSON
from rich.console import Console
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from pathlib import Path
import sys
import os

# Configurar PYTHONPATH para imports absolutos (enfoque productivo)
repo_root = Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import absoluto del esquema compartido


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


# Prompt con instrucciones de formato estrictas
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system_message),
#         (
#             "system",
#             "Sigue estrictamente este formato de salida JSON válido:\n{format_instructions}",
#         ),
#         ("human", "Título original: {title}"),
#     ]
# ).partial(
#     format_instructions=parser.get_format_instructions()
# )

# Pinta que tiene el esquema de Suggestions
print("\n[bold cyan]Esquema de salida esperado[/bold cyan]")
print(JSON.from_data(Suggestions.model_json_schema(), indent=2))


# Ejecutar la cadena con la variable de entrada
ai_message = model_with_structured_output.invoke(
    {"title": os.getenv("YOUTUBE_TITLE")}
)

# Imprimir la respuesta cruda del modelo
print("\n[bold green]Respuesta del modelo (cruda)[/bold green]")
print(ai_message.content)





