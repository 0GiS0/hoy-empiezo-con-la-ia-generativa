from schema import Suggestions, Suggestion
from calendar import c
import os
import re
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console


# Para mensajes más bonitos por el terminal
console = Console()

# Cargar las variables definidas en el archivo .env (si todavía no lo tienes copia y pega el .env-sample)
load_dotenv()

# Crear cliente de OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)


SYSTEM_PROMPT = (
    """
Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Devuelve un resultado como este:
{
  "suggestions": [
    {
      "title": "string (<= 70 caracteres, incluye emojis si aportan)",
      "emojis": ["string", "string"],
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
).strip()

console.print("[blue]System Prompt:[/blue]")
console.print(SYSTEM_PROMPT)


response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content":  os.getenv("YOUTUBE_TITLE")},
    ],
    model=os.getenv("MODEL_NAME"),

)
result = response.choices[0].message.content

console.print(result)


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


printable_json = extract_json_block(result)

console.print("[green]JSON extraído:[/green]")
console.print(printable_json)

# Convertir este json a un listado de objetos Suggestion

suggestions_data = printable_json
suggestions = Suggestions.model_validate_json(suggestions_data)

console.print("[green]Respuesta parseada:[/green]")
console.print(suggestions)