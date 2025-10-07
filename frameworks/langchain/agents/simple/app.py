"""
🤖 Ejemplo de Agente LangChain Tradicional con AgentExecutor

Este archivo demuestra el uso del enfoque tradicional de LangChain para crear agentes:
- 🔄 Utiliza AgentExecutor como wrapper que maneja automáticamente el bucle "pensamiento -> acción -> observación"
- 🚀 Ideal para prototipos rápidos y casos de uso simples
- 📦 El flujo de ejecución es una "caja negra" controlada internamente por LangChain

Ventajas de AgentExecutor:
✅ 🎯 Configuración simple y rápida
✅ 🔮 Abstracción del bucle de ejecución
✅ 📝 Menos código para casos básicos
✅ 🔧 Integración directa con herramientas

Limitaciones de AgentExecutor:
❌ 🎮 Control limitado sobre el flujo de ejecución
❌ ⚙️ Difícil personalización de la lógica de decisión
❌ 👁️ Estado interno no transparente
❌ 🤹 Complicado para flujos multi-agente complejos
❌ 🔍 Menor observabilidad del proceso de pensamiento
"""

# Imports generales
import datetime
import random
import os

from dotenv import load_dotenv

import asyncio
from langchain.chat_models import init_chat_model
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate


# Cargo las variables de entorno del .env
load_dotenv()


# Definir herramientas personalizadas para el agente
@tool
def get_current_time() -> str:
    """Obtiene la hora actual del sistema."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def generate_random_number(min_val: int = 1, max_val: int = 100) -> int:
    """Genera un número aleatorio entre min_val y max_val."""
    return random.randint(min_val, max_val)


@tool
def create_youtube_titles(description: str) -> str:
    """Crea 5 títulos optimizados para YouTube basados en una descripción."""
    # Esta es una función de ejemplo, en la práctica podrías usar APIs o lógica más compleja
    base_titles = [
        f"🔥 {description[:30]}... ¡INCREÍBLE!",
        f"✨ Cómo {description[:35]}... paso a paso",
        f"🚀 {description[:40]}... ¡TUTORIAL!",
        f"💡 {description[:30]}... ¡Te va a sorprender!",
        f"⚡ {description[:35]}... ¡FÁCIL y RÁPIDO!"
    ]
    return "\n".join([f"{i+1}. {title}" for i, title in enumerate(base_titles)])


async def main():
    # Configurar el modelo LLM
    llm = init_chat_model(
        model_provider=os.getenv("MODEL_PROVIDER"),
        model=os.getenv("MODEL_ID"),
        openai_api_base=os.getenv("ENDPOINT_URL"),
        openai_api_key=os.getenv("API_KEY"),
        temperature=0.7
    )

    # Definir las herramientas disponibles para el agente
    tools = [get_current_time, generate_random_number, create_youtube_titles]

    # Crear el prompt del sistema para el agente
    system_prompt = """
    Eres un asistente especializado en crear títulos optimizados para YouTube 🎬.
    Tu tarea principal es generar 5 opciones de títulos atractivos, creativos y relevantes.

    ➡️ Cuando generes títulos, cada uno debe:
    - Ser claro y fácil de entender.
    - Estar orientado a captar la atención (gancho).
    - Reflejar fielmente el contenido del vídeo.
    - Usar un máximo de 70 caracteres.
    - Incluir siempre al menos un emoji para hacerlo más llamativo.

    Tienes acceso a herramientas que puedes usar cuando sea necesario:
    - get_current_time: Para obtener la hora actual
    - generate_random_number: Para generar números aleatorios
    - create_youtube_titles: Para crear títulos optimizados para YouTube

    Si recibes una solicitud que no esté relacionada con la generación de títulos de YouTube, 
    puedes usar tus otras herramientas si son relevantes, o responder de manera útil.
    """

    # Crear el template del prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 🧠 Crear el agente con las herramientas
    agent = create_openai_functions_agent(llm, tools, prompt)

    # 🏭 Crear el ejecutor del agente
    # 📦 AgentExecutor encapsula toda la lógica del bucle "pensamiento -> acción -> observación"
    # 🎭 Es una caja negra que maneja automáticamente las decisiones y llamadas a herramientas
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Ejecutar una consulta
    user_input = """
    ¡Hola developer 👋🏻! Para este vídeo te voy a mostrar cómo empezar con Microsoft Agent Framework, 
    desde un agente simple, pasando por uno con tools y demás a un flujo donde se involucren varios agentes.
    """

    try:
        # 🚀 Ejecutar el agente usando AgentExecutor
        # 🔄 El bucle interno automáticamente:
        # 1. 🧠 Llama al LLM para decidir qué hacer
        # 2. 🔧 Ejecuta herramientas si es necesario
        # 3. 🔍 Evalúa si necesita más información
        # 4. 🔁 Repite hasta llegar a una respuesta final
        result = await agent_executor.ainvoke({
            "input": f"Crea títulos para YouTube basados en esta descripción: {user_input}"
        })
        print("🤖 Respuesta del Agente:")
        print(result["output"])

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de tener Ollama ejecutándose con el modelo llama3.2")


if __name__ == "__main__":
    asyncio.run(main())
