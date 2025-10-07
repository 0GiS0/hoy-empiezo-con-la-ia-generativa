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

# 🎨 Rich para salida bonita
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.table import Table
from rich.columns import Columns
from rich import box


# Cargo las variables de entorno del .env
load_dotenv()

# 🎨 Crear consola Rich para salida bonita
console = Console()


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
    # 📝 Extraer palabras clave de la descripción
    keywords = description.lower()
    
    # 🎯 Generar títulos específicos y relevantes
    if "microsoft agent framework" in keywords:
        base_titles = [
            "🔥 MICROSOFT AGENT FRAMEWORK - ¡Guía completa para developers!",
            "✨ Cómo empezar con Microsoft Agent Framework - Paso a paso",
            "🚀 Microsoft Agent Framework TUTORIAL - De básico a avanzado",
            "💡 Secretos de Microsoft Agent Framework - ¡Te va a sorprender!",
            "⚡ Domina Microsoft Agent Framework - ¡FÁCIL y RÁPIDO!"
        ]
    else:
        # 📋 Títulos genéricos para otras descripciones
        topic = description.split('.')[0][:40] if '.' in description else description[:40]
        base_titles = [
            f"🔥 {topic} - ¡INCREÍBLE!",
            f"✨ Cómo {topic} - paso a paso",
            f"🚀 {topic} - ¡TUTORIAL!",
            f"💡 {topic} - ¡Te va a sorprender!",
            f"⚡ {topic} - ¡FÁCIL y RÁPIDO!"
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

    # � VISUALIZACIÓN DEL GRAFO
    # 👁️ Una de las ventajas clave de LangGraph: puedes ver el grafo visualmente
    try:
        console.print("\n🎨 [bold cyan]Generando visualización del grafo...[/bold cyan]")
        
        # 📊 Obtener representación Mermaid del grafo (formato de texto)
        mermaid_graph = app.get_graph().draw_mermaid()
        
        # 📋 Mostrar Mermaid con Rich
        mermaid_panel = Panel(
            Syntax(mermaid_graph, "mermaid", theme="monokai", line_numbers=False),
            title="📋 Representación Mermaid del Grafo",
            border_style="cyan",
            expand=False
        )
        console.print(mermaid_panel)
        
        # 🖼️ Generar imagen PNG del grafo
        png_data = app.get_graph().draw_mermaid_png()
        
        # 💾 Guardar la imagen
        graph_image_path = "graph_visualization.png"
        with open(graph_image_path, "wb") as f:
            f.write(png_data)
        
        console.print(f"🖼️  [green]Imagen del grafo guardada en:[/green] [bold]{graph_image_path}[/bold]")
        console.print("   [dim]Puedes abrirla para ver la visualización completa del flujo![/dim]")
        
    except Exception as e:
        console.print(f"⚠️  [yellow]Error generando visualización:[/yellow] {e}")
        console.print("   [dim](Es normal si no tienes graphviz instalado)[/dim]")

    # �🎬 Ejecutar una consulta
    user_input = """
    ¡Hola developer 👋🏻! Para este vídeo te voy a mostrar cómo empezar con Microsoft Agent Framework, 
    desde un agente simple, pasando por uno con tools y demás a un flujo donde se involucren varios agentes.
    """

    # 📝 Crear el mensaje inicial del sistema
    system_message = """
    Eres un asistente especializado en crear títulos optimizados para YouTube 🎬.
    
    Cuando el usuario te pida crear títulos para YouTube, DEBES usar la herramienta create_youtube_titles 
    pasándole la descripción del video como parámetro.
    
    NUNCA respondas directamente con títulos, SIEMPRE usa la herramienta create_youtube_titles.
    
    Después de usar la herramienta, puedes comentar o mejorar los títulos que generó.
    
    Tienes acceso a estas herramientas:
    - get_current_time: Para obtener la hora actual
    - generate_random_number: Para generar números aleatorios  
    - create_youtube_titles: Para crear títulos optimizados para YouTube (¡USA ESTA!)
    
    Recuerda: Siempre usa las herramientas cuando sea apropiado, no respondas directamente.
    """

    try:
        # 📨 Preparar los mensajes iniciales
        initial_messages = [
            ("system", system_message),
            ("user", f"Crea títulos para YouTube basados en esta descripción: {user_input}")
        ]
        
        inputs = {"messages": initial_messages}
        
        console.print("\n🤖 [bold green]Ejecutando el grafo del agente...[/bold green]")
        console.print()
        
        # 🌟 VENTAJA CLAVE: Observabilidad completa del proceso
        # 👁️ El método astream() permite ver cada paso del grafo en tiempo real
        # 📦 Esto es imposible con AgentExecutor que es una caja negra
        
        # 📊 Recopilar todos los mensajes para mostrar al final
        all_tool_results = []
        
        async for output in app.astream(inputs):
            # 📊 El resultado del stream es un diccionario donde la clave es el nombre del nodo
            for key, value in output.items():
                
                # 🎨 Crear panel bonito para cada nodo
                node_title = f"� OUTPUT DEL NODO: {key.upper()}"
                node_content = []
                
                # 📋 Procesar cada mensaje
                for msg in value['messages']:
                    if hasattr(msg, 'content') and msg.content:
                        # 🎯 Mostrar contenido completo si es importante
                        content = msg.content.strip()
                        if len(content) > 0:
                            if len(content) > 200:
                                node_content.append(f"💬 [cyan]Contenido:[/cyan] {content[:150]}...")
                            else:
                                node_content.append(f"💬 [cyan]Contenido:[/cyan] {content}")
                    
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            node_content.append(f"🔧 [yellow]Llamada a herramienta:[/yellow] [bold]{tool_call['name']}[/bold]")
                            # 📝 Mostrar argumentos de forma más limpia
                            args_preview = str(tool_call['args'])[:150]
                            node_content.append(f"   📋 [dim]Argumentos:[/dim] {args_preview}...")
                    
                    if hasattr(msg, 'name') and msg.name:
                        node_content.append(f"🛠️  [green]Resultado de herramienta:[/green] [bold]{msg.name}[/bold]")
                        if hasattr(msg, 'content'):
                            # 🎨 Guardar resultado completo para mostrar al final
                            all_tool_results.append(msg.content)
                            # Mostrar preview
                            response_preview = msg.content.replace('\n', ' | ')[:100]
                            node_content.append(f"   📤 [green]Respuesta:[/green] {response_preview}...")
                
                # � Mostrar panel del nodo
                if node_content:
                    panel = Panel(
                        "\n".join(node_content),
                        title=node_title,
                        border_style="blue",
                        expand=False
                    )
                    console.print(panel)
        
        # 🏆 Mostrar respuesta final completa del agente
        final_response = value['messages'][-1]
        
        # 🎨 Panel especial para la respuesta final
        final_panel = Panel(
            f"[bold white]{final_response.content}[/bold white]",
            title="🤖 Respuesta Final del Agente",
            border_style="green",
            expand=False
        )
        console.print(final_panel)
        
        # 📋 Si hay resultados de herramientas, mostrarlos también
        if all_tool_results:
            console.print("\n🎬 [bold cyan]Títulos generados por la herramienta:[/bold cyan]")
            for i, result in enumerate(all_tool_results, 1):
                # 🧹 Limpiar caracteres unicode problemáticos
                clean_result = result.encode('utf-8', errors='ignore').decode('utf-8')
                clean_result = clean_result.replace('\\u00a1', '¡').replace('\\u00bb', '»')
                clean_result = clean_result.replace('\\u00e1', 'á').replace('\\u00e9', 'é')
                clean_result = clean_result.replace('\\u00ed', 'í').replace('\\u00f3', 'ó')
                clean_result = clean_result.replace('\\u00fa', 'ú').replace('\\u00f1', 'ñ')
                
                tool_panel = Panel(
                    f"[yellow]{clean_result}[/yellow]",
                    title=f"📝 Resultado de Herramienta #{i}",
                    border_style="yellow",
                    expand=False
                )
                console.print(tool_panel)
        
        # 🌟 Mostrar resumen final de ventajas de LangGraph
        console.print("\n" + "="*70)
        advantages_text = """
🌟 VENTAJAS DE LANGGRAPH DEMOSTRADAS:

✅ Observabilidad completa - Viste cada paso del proceso
✅ Control explícito del flujo - Definiste el grafo exacto
✅ Visualización del grafo - Imagen y código Mermaid generados
✅ Estado transparente - Acceso completo a todos los mensajes
✅ Depuración fácil - Información detallada de cada nodo
✅ Modularidad - Nodos reutilizables (agent, action)

🎯 Con AgentExecutor esto sería una caja negra sin visibilidad.
        """
        
        console.print(Panel(
            advantages_text.strip(),
            title="🕸️ LangGraph vs AgentExecutor",
            border_style="magenta",
            expand=False
        ))

    except Exception as e:
        console.print(f"❌ [red]Error:[/red] {e}")
        console.print("[dim]Asegúrate de tener Ollama ejecutándose con el modelo llama3.2[/dim]")


if __name__ == "__main__":
    asyncio.run(main())