import os

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from rich.console import Console

# LangGraph para persistencia
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

load_dotenv()

console = Console()

model = init_chat_model(
    model=os.getenv("GITHUB_MODEL_ID"),
    model_provider="openai",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url=os.getenv("GITHUB_MODELS_URL"),
)

userMessage = "Hola, ¿cómo estás? Mi nombre es Gisela"

console.print(f"[pink]👤 {userMessage}[/pink]")

response = model.invoke(
    [HumanMessage(content=userMessage)])

console.print(f"[blue]🤖 {response.content}[/blue]")

console.print(f"[pink]👤 ¿Cómo me llamo?[/pink]")

response = model.invoke(
    [HumanMessage(content="¿Cómo me llamo?")])

console.print(f"[blue]🤖 {response.content}[/blue]")

# Definimos un nuevo grafo.
# ¿Qué es un grafo? Un grafo es una estructura que representa relaciones entre diferentes entidades. En este caso, estamos utilizando un grafo para representar el estado de la conversación.
# Esto significa que el grafo tendrá un estado que refleja la conversación actual
workflow = StateGraph(state_schema=MessagesState)

# Función que llamará al modelo recibiendo el estado previo de la conversación


def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    console.print(response)
    return {"messages": response}


# Definimos un único nodo en el grado que será nuestro punto de entrada
workflow.add_edge(START, "chat")
workflow.add_node("chat", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


config = {"configurable": {"thread_id": "1234"}}

# Intentamos comunicarnos de nuevo pero ahora con estado

query = "¡Hola! Soy Gisela."

input_messages = [HumanMessage(query)]
output = app.invoke({"messages": input_messages}, config)
console.print(f"[blue]🤖 {output['messages'][-1].content}[/blue]")

query = "¿Cuál es mi nombre?"

input_messages = [HumanMessage(query)]
output = app.invoke({"messages": input_messages}, config)
console.print(f"[blue]🤖 {output['messages'][-1].content}[/blue]"   )