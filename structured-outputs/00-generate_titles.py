from schema import Suggestions, Suggestion
from calendar import c
import os
import re
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


# Para mensajes más bonitos por el terminal
console = Console()

# Cargar las variables definidas en el archivo .env (si todavía no lo tienes copia y pega el .env-sample)
load_dotenv()

# Crear cliente de OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Si queremos obtener un formato en concreto "a pelo" necesitamos indicar de alguna forma todo lo que queremos que cumpla el mismo
SYSTEM_PROMPT = (
    """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Como parte del resultado devuelve un JSON como este:
{
  "suggestions": [
    {
      "title": "string (<= 70 caracteres, incluye emojis si aportan)",
      "emojis": ["string", "string"], //Requeridos 2
      "length": 42
    },
    { /* total 5 items exactos */ }
  ]
}

Reglas:
- Exactamente 5 elementos en "suggestions".
- "emojis" debe contener 0-2 elementos máximo.
- "length" es la longitud real de "title".
- Sé atractivo para el clic sin prometer en exceso.
"""
)

# Este sería el system prompt
console.print(
    Panel.fit(
        SYSTEM_PROMPT,
        title="🧠 System Prompt",
        subtitle="Reglas y formato esperado",
        border_style="bold magenta",
    )
)


response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content":  os.getenv("YOUTUBE_TITLE")},
    ],
    model=os.getenv("MODEL_NAME"),

)
result = response.choices[0].message.content

console.print(
    Panel(
        result,
        title="🤖 Respuesta del modelo (texto)",
        border_style="cyan",
    )
)

# Función que intenta aislar el bloque JSON del texto
def extract_json_block(text: str) -> Optional[str]:
    """Intenta aislar el JSON a partir del texto (por si el modelo habla de más)."""
    # Busca el primer bloque {...}
    match = re.search(r"\{[\s\S]*\}$", text.strip())
    if match:
        return match.group(0)
    # Fallback: intenta encontrar el primer '{' y el último '}'
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start: end + 1]
    return None

# Intentar extraer el JSON del resultado
printable_json = extract_json_block(result)

# Imprimirlo por pantalla con resaltado si existe
if printable_json:
    json_syntax = Syntax(printable_json, "json", theme="dracula", line_numbers=False)
    console.print(
        Panel(
            json_syntax,
            title="📦 JSON extraído (sin structured outputs)",
            border_style="yellow",
        )
    )
else:
    console.print(
        Panel(
            "No se pudo extraer un bloque JSON del texto devuelto por el modelo.",
            title="⚠️ JSON no encontrado",
            border_style="red",
        )
    )

# Convertir este json a un listado de objetos Suggestion
suggestions = Suggestions.model_validate_json(printable_json)

# Imprimir el resultado ya como un objeto Suggestions con el estilo que quiera porque al ser un objeto puedo acceder a sus propiedades
table = Table(title="✅ Respuesta parseada")
table.add_column("#", style="bold green", justify="right")
table.add_column("Título", style="white")
table.add_column("Emojis", style="yellow")
table.add_column("Length", style="cyan", justify="right")

for idx, s in enumerate(suggestions.suggestions, start=1):
    emojis_txt = " ".join(s.emojis) if isinstance(s.emojis, list) else str(s.emojis)
    table.add_row(str(idx), s.title, emojis_txt, str(s.length))

# Imprimir en formato tabla la información dentro del listado Suggestions
console.print(Panel(table, border_style="green"))