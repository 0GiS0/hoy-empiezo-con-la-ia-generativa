"""
🕸️ Ejemplo de Agente con LangGraph - Versión Simplificada

Este archivo demuestra el uso de LangGraph para crear agentes con control explícito del flujo:
- 🎨 LangGraph permite definir el flujo de ejecución como un grafo de estados
- 🧩 Cada nodo representa una unidad de trabajo (agente, herramientas, lógica personalizada)
- 🔗 Las aristas definen las transiciones entre nodos basadas en condiciones
- 🌟 Proporciona transparencia total del estado y flujo de ejecución

Ventajas de LangGraph vs AgentExecutor:
✅ 🎮 Control explícito del flujo de ejecución
✅ 👁️ Estado transparente y predecible
✅ 🧩 Modularidad y reutilización de componentes
✅ 🤹 Ideal para flujos multi-agente complejos
✅ 🔍 Mejor observabilidad y depuración
✅ 🌊 Flexibilidad para ciclos y ramificaciones personalizadas
✅ 👨‍💻 Facilita la intervención humana en el flujo

Casos de uso ideales para LangGraph:
🎯 🏭 Aplicaciones de producción robustas
🎯 🤝 Flujos que requieren múltiples agentes colaborando
🎯 🧠 Lógicas de decisión complejas con ramificaciones
🎯 🤲 Sistemas que necesitan intervención humana
🎯 📊 Aplicaciones que requieren máxima observabilidad
"""

# Imports generales
import datetime
import random
import os
import operator

from dotenv import load_dotenv

import asyncio
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from typing import TypedDict, Annotated, Sequence

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode


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

# 1️⃣ Definir el estado del agente
# 🔬 El estado es completamente transparente y predecible, a diferencia del AgentExecutor
# 🔄 Cada nodo del grafo recibe y modifica este estado de manera explícita
class AgentState(TypedDict):
    # 💬 La secuencia de mensajes se acumula a lo largo del tiempo
    # ➕ Annotated con operator.add significa que los nuevos mensajes se añaden a la lista existente
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 2️⃣ Definir los nodos del grafo
# 🧩 Cada nodo es una función que toma el estado actual y produce una nueva versión del estado
# ⚙️ Esto proporciona control granular sobre cada paso del proceso

def call_model(state: AgentState, llm):
    """
    🤖 Nodo 'agent': Ejecuta el LLM directamente para decidir qué hacer.
    🎮 A diferencia del AgentExecutor, aquí controlamos explícitamente cuando y cómo
    se ejecuta el modelo. Podemos inspeccionar el estado antes y después.
    """
    # 📨 Obtener todos los mensajes del estado
    messages = state["messages"]
    
    # 🧠 Llamar al LLM con los mensajes
    response = llm.invoke(messages)
    
    # 📤 Devolver el nuevo estado con la respuesta del LLM
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """
    🚦 Función de decisión para aristas condicionales.
    🎯 Esta es la lógica que determina el flujo del grafo - completamente personalizable.
    🔒 En AgentExecutor esta lógica está oculta e es más difícil de modificar.
    """
    last_message = state['messages'][-1]
    # ✅ Si no hay llamadas a herramientas, hemos terminado
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return "end"
    # 🔧 De lo contrario, hay que llamar a las herramientas
    return "continue"


async def main():
    # 🧠 Configurar el modelo LLM
    llm = init_chat_model(
        model_provider=os.getenv("MODEL_PROVIDER"),
        model=os.getenv("MODEL_ID"),
        openai_api_base=os.getenv("ENDPOINT_URL"),
        openai_api_key=os.getenv("API_KEY"),
        temperature=0.7
    )

    # 🔧 Definir las herramientas disponibles para el agente
    tools = [get_current_time, generate_random_number, create_youtube_titles]

    # 🔗 Vincular las herramientas al LLM
    llm_with_tools = llm.bind_tools(tools)

    # 3️⃣ Construir el grafo
    # 🏗️ Aquí definimos explícitamente la arquitectura de nuestro agente
    # 🔍 Cada nodo y arista es transparente y modificable
    workflow = StateGraph(AgentState)

    # 🤖 Añadir el nodo que ejecuta el modelo
    # 🧠 Este nodo recibe el estado, ejecuta el LLM, y devuelve la decisión
    workflow.add_node("agent", lambda state: call_model(state, llm_with_tools))

    # 🔧 Añadir el nodo que ejecuta las herramientas  
    # 📦 ToolNode es un nodo preconfigurado que maneja las llamadas a herramientas
    tool_node = ToolNode(tools)
    workflow.add_node("action", tool_node)

    # 🚪 Añadir el punto de entrada
    # ▶️ El grafo siempre empieza ejecutando el nodo 'agent'
    workflow.set_entry_point("agent")

    # 🚦 Añadir la arista condicional para decidir si llamar a herramientas o finalizar
    # 🔑 Esta es la clave de la flexibilidad: podemos personalizar completamente la lógica de decisión
    workflow.add_conditional_edges(
        "agent",                    # 🤖 Desde el nodo 'agent'
        should_continue,           # 🎯 Función que decide la próxima acción
        {
            "continue": "action",  # 🔧 Si hay tool_calls, vamos al nodo 'action'
            "end": END,           # 🏁 Si no hay tool_calls, terminamos
        },
    )

    # 🔄 Añadir la arista para volver al agente después de ejecutar las herramientas
    # 🔁 Después de ejecutar herramientas, siempre volvemos al agente para evaluar los resultados
    workflow.add_edge("action", "agent")

    # 🏭 Compilar el grafo en un objeto ejecutable
    # 🚀 El grafo se convierte en una aplicación que podemos ejecutar paso a paso
    app = workflow.compile()

    # 🎬 Ejecutar una consulta
    user_input = """
    ¡Hola developer 👋🏻! Para este vídeo te voy a mostrar cómo empezar con Microsoft Agent Framework, 
    desde un agente simple, pasando por uno con tools y demás a un flujo donde se involucren varios agentes.
    """

    # 📝 Crear el mensaje inicial del sistema
    system_message = """
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

    try:
        # 📨 Preparar los mensajes iniciales
        initial_messages = [
            ("system", system_message),
            ("user", f"Crea títulos para YouTube basados en esta descripción: {user_input}")
        ]
        
        inputs = {"messages": initial_messages}
        
        print("🤖 Ejecutando el grafo del agente...")
        
        # 🌟 VENTAJA CLAVE: Observabilidad completa del proceso
        # 👁️ El método astream() permite ver cada paso del grafo en tiempo real
        # 📦 Esto es imposible con AgentExecutor que es una caja negra
        async for output in app.astream(inputs):
            # 📊 El resultado del stream es un diccionario donde la clave es el nombre del nodo
            for key, value in output.items():
                print(f"--- 🔄 SALIDA DEL NODO: '{key}' ---")
                # 🔍 Podemos inspeccionar exactamente qué ocurre en cada nodo
                # 🐛 Esto facilita la depuración y el monitoreo en producción
                print(value['messages'])  # 💬 Descomenta para ver todos los mensajes
        
        # 🏆 La respuesta final está en el último mensaje del estado
        final_response = value['messages'][-1]
        print("\n🤖 Respuesta Final del Agente:")
        print(final_response.content)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de tener Ollama ejecutándose con el modelo llama3.2")


if __name__ == "__main__":
    asyncio.run(main())