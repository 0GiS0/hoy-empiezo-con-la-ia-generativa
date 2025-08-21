import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from schema import Suggestions
from score_and_select import best_suggestion


# Para mensajes más bonitos por el terminal
console = Console()

# Cargar las variables definidas en el archivo .env (si todavía no lo tienes copia y pega el .env-sample)
load_dotenv()

MODEL = os.getenv("STRUCTURED_OUTPUTS_MODEL")

# Crear cliente de OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)


SYSTEM_MESSAGE = """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Tu tarea es mejorar el título que te envíe el usuario y proponer alternativas que inviten al clic sin prometer en exceso.
"""

try:
    response = client.chat.completions.parse(
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": os.getenv("YOUTUBE_TITLE")},
        ],
        model=os.getenv("MODEL_NAME"),
        response_format=Suggestions

    )
except:
    console.print("[red]Error al generar títulos.[/red]")


# Imprimir la respuesta
console.print(response)


# Imprimir la respuesta parseada
console.print("[green]Respuesta parseada:[/green]")
parsed = response.choices[0].message.parsed
suggestions = parsed.suggestions
console.print(suggestions)

the_good_one = best_suggestion(suggestions)

console.print("[green]La mejor sugerencia es:[/green]")
console.print(the_good_one)
