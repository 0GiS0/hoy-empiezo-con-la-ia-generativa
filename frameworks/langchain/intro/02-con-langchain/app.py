"""Versión con LangChain del ejemplo de 01-sin-langchain/app.py.
Mantiene el mismo caso de uso, esquema Pydantic compartido y validaciones.
"""

# Módulos que necesito importar
from rich import print
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pathlib import Path
import sys
import os
import unicodedata

# Configurar PYTHONPATH para imports absolutos (enfoque productivo)
repo_root = Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Import absoluto del esquema compartido
from frameworks.langchain.intro.common import Suggestions


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
print(Suggestions.model_json_schema())

# Cadena: prompt -> modelo (para obtener raw) y luego parser
llm_chain = prompt | chat_model

# Ejecutar la cadena con la variable de entrada
ai_message = llm_chain.invoke({"title": os.getenv("YOUTUBE_TITLE")})

# Imprimir la respuesta cruda del modelo
print("\n[bold green]Respuesta del modelo (cruda)[/bold green]")
print(ai_message.content)

# Parsear a nuestro esquema Pydantic
result: Suggestions = PydanticOutputParser(pydantic_object=Suggestions).parse(ai_message.content)

# Imprimir la respuesta parseada
print("\n[bold green]Respuesta parseada[/bold green]")
print(result)


# Validación similar al ejemplo sin LangChain
def get_visible_length(text: str) -> int:
    """Cuenta solo caracteres visibles, excluyendo caracteres de control y formato Unicode"""
    visible_chars = 0
    for char in text:
        if unicodedata.category(char) not in ("Cf", "Cc", "Mn"):
            visible_chars += 1
    return visible_chars


for suggestion in result.suggestions:
    actual_length = len(suggestion.title)
    visible_length = get_visible_length(suggestion.title)
    reported_length = suggestion.length

    print(f"\n[bold cyan]Análisis de '{suggestion.title}':[/bold cyan]")
    print(f"  • Longitud total (len()): {actual_length}")
    print(f"  • Longitud visible: {visible_length}")
    print(f"  • Longitud reportada por modelo: {reported_length}")

    if reported_length != visible_length:
        print(
            f"[bold red]Error de validación:[/bold red] La longitud visible ({visible_length}) no coincide con la reportada ({reported_length})"
        )
        if actual_length != visible_length:
            non_visible = [
                f"\\u{ord(c):04x}" for c in suggestion.title if unicodedata.category(c) in ("Cf", "Cc", "Mn")
            ]
            print(f"  • Caracteres no visibles encontrados: {non_visible}")
    else:
        print(
            f"[bold green]Validación exitosa:[/bold green] La longitud visible ({visible_length}) coincide con la reportada ({reported_length})"
        )
