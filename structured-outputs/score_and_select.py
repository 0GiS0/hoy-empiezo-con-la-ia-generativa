from http import client
import os
import json
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from schema import Suggestions, Suggestion

# Para mensajes más bonitos por el terminal
console = Console()

# Cargar variables de entorno
load_dotenv()

# Crear cliente de OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Función que evalúa un listado de Sugerencias y se queda con la mejor de las recibidas
def best_suggestion(suggestions: List[Suggestion]) -> Suggestion:

    SYSTEM_PROMPT = (
        "Eres un experto en selección de sugerencias. Tu tarea es evaluar las siguientes sugerencias y seleccionar la mejor."
        "Debes quedarte con aquella que tenga el mejor balance entre creatividad y relevancia."
    )

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "user", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(
                [s.model_dump() for s in suggestions])}
        ]
    )


    suggestion = response.choices[0].message.content

    # response = client.chat.completions.parse(
    #     model=os.getenv("MODEL_NAME"),
    #     messages=[
    #         {"role": "user", "content": SYSTEM_PROMPT},
    #         {"role": "user", "content": json.dumps(
    #             [s.dict() for s in suggestions])}
    #     ],
    #     response_format=Suggestion

    # )

    # suggestion = response.choices[0].message.parsed

    return suggestion
