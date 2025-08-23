"""Chat demo sin LangChain ni LangGraph.

Muestra dos cosas:
1. Conversaciones "aisladas" (sin memoria): cada llamada sólo ve el mensaje actual + system prompt.
2. Conversación con memoria manual en Python: acumulamos los mensajes en una lista y la reenviamos completa.

Objetivo: contrastar con la versión en `02-con-langchain/chat/server.py` que usa LangChain + LangGraph para gestionar mensajes y estado.
"""
from __future__ import annotations
import os
from typing import List, Dict
from dataclasses import dataclass, field
from dotenv import load_dotenv
from rich.console import Console
from openai import OpenAI

load_dotenv()
console = Console()

# =============================
# Configuración y cliente
# =============================
BASE_URL = os.getenv("GITHUB_MODELS_URL")
API_KEY = os.getenv("GITHUB_TOKEN")
MODEL_ID = os.getenv("GITHUB_MODEL_ID")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = (
    "Eres un asistente amistoso. Contesta de forma breve y clara. Si te preguntan por el nombre del usuario y aún no lo has visto, dilo honestamente."
)

# =============================
# Utilidades de conversación
# =============================
@dataclass
class ChatSession:
    """Gestiona el contexto de una conversación sin LangGraph.

    Almacena los mensajes en una lista de diccionarios compatibles con el SDK.
    """
    system_prompt: str = SYSTEM_PROMPT
    messages: List[Dict[str, str]] = field(default_factory=list)

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def build_payload(self) -> List[Dict[str, str]]:
        return [{"role": "system", "content": self.system_prompt}] + self.messages

    def ask(self, client: OpenAI, model: str, temperature: float = TEMPERATURE) -> str:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=self.build_payload(),
        )
        answer = response.choices[0].message.content
        self.add_assistant(answer)
        return answer

# =============================
# 1) Llamadas sin memoria
# =============================
console.rule("[bold yellow]1) Conversación sin memoria (stateless) [/bold yellow]")
first_user_msg = "Hola, ¿cómo estás? Mi nombre es Gisela"
console.print(f"[pink]👤 {first_user_msg}[/pink]")
response = client.chat.completions.create(
    model=MODEL_ID,
    temperature=TEMPERATURE,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": first_user_msg},
    ],
)
console.print(f"[blue]🤖 {response.choices[0].message.content}[/blue]")

follow_up = "¿Cómo me llamo?"
console.print(f"[pink]👤 {follow_up}[/pink]")
response2 = client.chat.completions.create(
    model=MODEL_ID,
    temperature=TEMPERATURE,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": follow_up},
    ],
)
console.print(f"[blue]🤖 {response2.choices[0].message.content}[/blue]")

# Nota: Seguramente el modelo no sabrá el nombre porque no tiene memoria de la primera interacción.

# =============================
# 2) Conversación con memoria manual
# =============================
console.rule("[bold green]2) Conversación con memoria (manual) [/bold green]")
session = ChatSession()

# Primer mensaje (se guarda)
session.add_user(first_user_msg)
answer1 = session.ask(client, MODEL_ID)
console.print(f"[blue]🤖 {answer1}[/blue]")

# Segunda pregunta: ahora el historial completo se envía de nuevo
offset_question = follow_up
console.print(f"[pink]👤 {offset_question}[/pink]")
session.add_user(offset_question)
answer2 = session.ask(client, MODEL_ID)
console.print(f"[blue]🤖 {answer2}[/blue]")

# =============================
# Resumen / Diferencias
# =============================
console.rule("[bold cyan]Resumen[/bold cyan]")
console.print("[white]Sin memoria: cada request ignora las anteriores. Con memoria manual: reenviamos el historial completo en cada llamada.\nEsto emula la persistencia que LangGraph gestiona de forma más estructurada.[/white]")

if __name__ == "__main__":
    console.print("[dim]Demo finalizada.[/dim]")
