"""Versión con LangChain del ejemplo de 01-sin-langchain/app.py.
Mantiene el mismo caso de uso, esquema Pydantic compartido y validaciones.
"""

# Módulos que necesito importar
from rich import print
from rich.json import JSON
from rich.console import Console
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pathlib import Path
import sys
import os
import json

# Configurar PYTHONPATH para imports absolutos (enfoque productivo)
repo_root = Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import absoluto del esquema compartido
from frameworks.langchain.intro.common import Suggestions, build_validation_table


# Cargar las variables de entorno que necesito para esta demo
load_dotenv()

# Pintar la configuración (sin la clave)
print("[bold cyan]Configuración de la API de OpenAI[/bold cyan]")
print(f"[magenta]URL:[/magenta] {os.getenv('GITHUB_MODELS_URL')}")
print(f"[magenta]Modelo:[/magenta] {os.getenv('GITHUB_MODEL_ID')}")
print(f"[magenta]Temperatura:[/magenta] {os.getenv('TEMPERATURE', '0.7')}")
print(f"[magenta]Título de YouTube:[/magenta] {os.getenv('YOUTUBE_TITLE')}")

# Modelo chat con Langchain
chat_model = init_chat_model(
    model=os.getenv("GITHUB_MODEL_ID"),
    model_provider="openai",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url=os.getenv("GITHUB_MODELS_URL"),
    # temperature=float(os.getenv("TEMPERATURE", "0.7")),
)


# Mensaje del sistema, para que sepa qué es lo que esperamos
system_message = (
    """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.
"""
)

# Parser pydantic para forzar el formato
parser = PydanticOutputParser(pydantic_object=Suggestions)

# Prompt con instrucciones de formato estrictas
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_message),
        (
            "system",
            "Sigue estrictamente este formato de salida JSON válido:\n{format_instructions}",
        ),
        ("human", "Título original: {title}"),
    ]
).partial(
    format_instructions=parser.get_format_instructions()
)

# Pinta que tiene el esquema de Suggestions
print("\n[bold cyan]Esquema de salida esperado[/bold cyan]")
print(JSON.from_data(Suggestions.model_json_schema(), indent=2))

# Cadena: prompt -> modelo (para obtener raw) y luego parser
llm_chain = prompt | chat_model

# Ejecutar la cadena con la variable de entrada
ai_message = llm_chain.invoke({"title": os.getenv("YOUTUBE_TITLE")})

# Imprimir la respuesta cruda del modelo
print("\n[bold green]Respuesta del modelo (cruda)[/bold green]")
print(ai_message.content)

# Parsear a nuestro esquema Pydantic
result: Suggestions = PydanticOutputParser(pydantic_object=Suggestions).parse(ai_message.content)

# Imprimir la respuesta parseada como JSON legible
print("\n[bold green]Respuesta parseada (JSON)[/bold green]")
try:
    parsed_json = result.model_dump()  # Pydantic v2
except Exception:
    parsed_json = json.loads(result.json())
print(JSON.from_data(parsed_json, indent=2))


console = Console()
table, mismatches = build_validation_table(result.suggestions)
print("\n[bold cyan]Resumen de sugerencias[/bold cyan]")
console.print(table)
if mismatches:
    print("[yellow]\nAviso:[/yellow] Se detectaron discrepancias entre longitud visible y reportada. ")
    print("Puede deberse a caracteres no visibles (marcas Unicode). Revisa la tabla y el JSON parseado.")
