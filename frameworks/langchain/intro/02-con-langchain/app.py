# Módulos que necesito importar
import os
from typing import List
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from rich import print

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
    temperature=float(os.getenv("TEMPERATURE", "0.7")),
)


# Mensaje del sistema, para que sepa qué es lo que esperamos
system_message = """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.

Guías de calidad para cada título:
- 55–70 caracteres por título (ideal ≤ 65); si no es viable, prioriza claridad y valor.
- Incluye 1–2 emojis relevantes por título; evita colocarlos al inicio.
- Integra la palabra clave principal del tema y, cuando encaje, una variación breve.
- Varía las fórmulas entre: beneficio claro, cómo/guía/truco, lista con número, sorpresa/curiosidad, urgencia/tiempo.
- Evita MAYÚSCULAS SOSTENIDAS, clickbait engañoso y afirmaciones dudosas.
"""

# Definimos el esquema de salida esperado (valida que haya exactamente 5 títulos)
class Suggestion(BaseModel):
    title: str = Field(
        description="Título en español optimizado para SEO y CTR; incluye 1–2 emojis no al inicio"
    )
    length: int = Field(description="Longitud del título en caracteres")
    emojis: List[str] = Field(description="Emojis usados en el título (1–2)")


class Suggestions(BaseModel):
    suggestions: List[Suggestion] = Field(
        min_items=5, max_items=5, description="Exactamente 5 títulos sugeridos"
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
).partial(format_instructions=parser.get_format_instructions())

# Cadena: prompt -> modelo -> parser
chain = prompt | chat_model | parser

# Ejecutar la cadena con la variable de entrada
result: Suggestions = chain.invoke({"title": os.getenv("YOUTUBE_TITLE")})

# Imprimir la respuesta de forma legible
print("\n[bold green]Sugerencias (parseadas y validadas)[/bold green]")
for idx, s in enumerate(result.suggestions, start=1):
    print(f"[cyan]{idx}[/cyan]. {s.title} [dim]({s.length} chars, emojis: {', '.join(s.emojis)})[/dim]")