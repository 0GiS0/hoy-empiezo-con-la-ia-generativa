# Módulos que necesito importar
from ...common.models import Suggestions

from rich import print
from rich.console import Console

# Módulos de langchain
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
import os

# Instancia de Console, para pintar el output bonito
console = Console()

# Cargar las variables de entorno que necesito para esta demo
load_dotenv()

# Pintar la configuración (sin la clave)
print("🚀 [bold cyan]Ejemplo con Langchain 🦜🔗[/bold cyan]")
print(f"🌐 [magenta]URL:[/magenta] [white]{os.getenv('GITHUB_MODELS_URL')}[/]")
print(f"🧠 [magenta]Modelo:[/magenta] [white]{os.getenv('GITHUB_MODEL_ID')}[/]")
print(
    f"🎛️ [magenta]Temperatura:[/magenta] [white]{os.getenv('TEMPERATURE', '0.7')}[/]")
print(
    f"🎬 [magenta]Título original YouTube:[/magenta] [yellow]{os.getenv('YOUTUBE_TITLE')}[/]")

# Modelo chat con Langchain
model = init_chat_model(
    model=os.getenv("GITHUB_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER"),
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url=os.getenv("GITHUB_MODELS_URL"),
    temperature=float(os.getenv("TEMPERATURE", "0.7")),
)


# Parser pydantic para forzar el formato
parser = PydanticOutputParser(pydantic_object=Suggestions)

# Añadir la salida estructurada
model_with_structured_output = model.with_structured_output(
    parser.get_output_schema())


# Mensaje del sistema, para que sepa qué es lo que esperamos
SYSTEM_MESSAGE = (
    """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.
"""
)

template = ChatPromptTemplate([
    ("system", SYSTEM_MESSAGE),
    ("user", "{title}")
])

prompt_value = template.invoke(
    {
        "title": os.getenv("YOUTUBE_TITLE")
    }
)

console.print(f"\n📝 [bold cyan]Prompt generado:[/bold cyan]\n{prompt_value}")

print("\n⏳ [cyan]Llamando al modelo con LangChain 🔗🦜[/cyan]")
try:
    # Ejecutar la cadena con la variable de entrada
    suggestions = model_with_structured_output.invoke(prompt_value)

    print("✅ [green]Respuesta recibida[/green]")
except Exception as e:
    print(f"🔥 [bold red]Error al invocar el modelo:[/bold red] {e}")
    raise

# Mostrar sugerencias formateadas
print("\n🧪 [bold green]Respuesta generada[/bold green]")
print("[cyan]Lista de sugerencias:[/cyan]")
for idx, s in enumerate(suggestions.suggestions, start=1):
    color = "green" if s.length <= 55 else (
        "yellow" if s.length <= 65 else "red")
    print(
        f" {idx}. [bold yellow]{s.title}[/bold yellow]\n"
        f"    🔡 Longitud: [bold {color}]{s.length}[/] chars  | 😀 Emojis: [dim]{' '.join(s.emojis)}[/]"
    )

print("\n🏁 [bold cyan]Fin de la demo[/bold cyan]")
