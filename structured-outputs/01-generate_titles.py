import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from schema import Suggestions
from score_and_select import best_suggestion
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import json


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

# Mostrar el system message
console.print(
    Panel.fit(
        SYSTEM_MESSAGE,
        title="🧠 System Prompt",
        border_style="bold magenta",
    )
)

# Esquema que espero de salida
schema_dict = Suggestions.model_json_schema()
schema_json = json.dumps(schema_dict, indent=2, ensure_ascii=False)
console.print(
    Panel(
        Syntax(schema_json, "json", theme="dracula", line_numbers=False),
        title="📜 Esquema de salida (structured)",
        border_style="blue",
    )
)

try:
    response = client.chat.completions.parse(
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": os.getenv("YOUTUBE_TITLE")},
        ],
        model=os.getenv("MODEL_NAME"),
        response_format=Suggestions,
    )
except Exception as e:
    console.print(
        Panel.fit(
            f"Error al generar títulos: {e}",
            title="❌ Error",
            border_style="red",
        )
    )
    sys.exit(1)


parsed = response.choices[0].message.parsed
suggestions = parsed.suggestions

# Tabla con las sugerencias
table = Table(title="✅ Respuesta parseada (Pydantic)")
table.add_column("#", style="bold green", justify="right")
table.add_column("Título", style="white")
table.add_column("Emojis", style="yellow")
table.add_column("Length", style="cyan", justify="right")

for idx, s in enumerate(suggestions, start=1):
    emojis_txt = " ".join(s.emojis) if isinstance(
        s.emojis, list) else str(s.emojis)
    table.add_row(str(idx), s.title, emojis_txt, str(s.length))

console.print(Panel(table, border_style="green"))

the_good_one = best_suggestion(suggestions)

console.print(
    Panel(
        f"Título: {the_good_one.title}, Emojis: {the_good_one.emojis}, Longitud: {the_good_one.length}",
        # str(the_good_one),
        title="🏆 La mejor sugerencia",
        border_style="bold green",
    )
)
