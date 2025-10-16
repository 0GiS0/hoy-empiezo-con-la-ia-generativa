"""
╔════════════════════════════════════════════════════════════════════════════╗
║                          📑 RAG con LangChain 🦜 🔗                         ║
╚════════════════════════════════════════════════════════════════════════════╝ 

Este servidor implementa un sistema RAG (Retrieval Augmented Generation) con:
- Router inteligente que decide cuándo usar RAG o responder directamente
- Historial de conversación persistente (gestión automática)
- Búsqueda semántica en Qdrant
"""

# 📦 Módulos generales
import os
import json
from rich.console import Console
from dotenv import load_dotenv

# 🌐 Flask: Framework web para crear la API REST
from flask import Flask, request, jsonify, Response

# 🧬 OpenAI Embeddings: Convierte texto en vectores numéricos para búsqueda semántica
from langchain_openai import OpenAIEmbeddings
# 🤖 LLM: Inicializador universal de modelos de lenguaje (OpenAI, Ollama, Azure, etc.)
from langchain.chat_models import init_chat_model
# 💾 Historial: Almacena mensajes de chat en SQLite para mantener contexto entre peticiones
from langchain_community.chat_message_histories import SQLChatMessageHistory
# 🗄️ Vector Store: Interfaz para interactuar con Qdrant (base de datos vectorial)
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
# 📋 JSON Parser: Convierte respuestas del LLM en objetos JSON estructurados
from langchain_core.output_parsers import JsonOutputParser
# 💬 Prompts: Templates para construir mensajes al LLM (system, user, history)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# 🔄 Historial automático: Envuelve cadenas para inyectar/guardar historial automáticamente
from langchain_core.runnables.history import RunnableWithMessageHistory


#══════════════════════════════════════════════════════════════════════════════
# 🔧 CONFIGURACIÓN INICIAL
#══════════════════════════════════════════════════════════════════════════════
# 🔐 Cargar variables de entorno desde archivo .env
load_dotenv()

# 🌐 Crear aplicación Flask (API web + servidor de archivos estáticos)
app = Flask(__name__, static_folder='../web', static_url_path='')

# 🎨 Crear consola Rich para output formateado con colores y emojis en el terminal
console = Console()

# ⚙️ Constantes de configuración
K_DOCUMENTS = 3  # 📊 Número máximo de documentos recuperados de Qdrant por consulta
MAX_HISTORY_MESSAGES = 6  # 📜 Cantidad de mensajes del historial enviados al router como contexto
COLLECTION_NAME = "youtube_guides"  # 🏷️ Nombre de la colección en Qdrant con documentación de YouTube

# 📁 Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "message_history.sqlite")  # 💾 Base de datos SQLite para historial de chat

console.print("\n[bold cyan]🚀 Iniciando servidor RAG...[/bold cyan]\n")

#══════════════════════════════════════════════════════════════════════════════
# 🤖 MODELOS LLM
#══════════════════════════════════════════════════════════════════════════════

console.print("📋 Configurando modelos...")

# 🧭 Modelo Router: Decide si una pregunta requiere RAG (retrieve) o respuesta directa (direct)
# Usa un modelo más pequeño/rápido para esta tarea de clasificación simple
llm_router = init_chat_model(
    model=os.getenv("LLM_ROUTER_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER", "openai"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("ENDPOINT_URL"),
)

# 💬 Modelo Answer: Genera respuestas finales al usuario (con o sin contexto RAG)
# Usa un modelo más capaz para generar respuestas de calidad
llm_answer = init_chat_model(
    model=os.getenv("LLM_ANSWER_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER", "openai"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("ENDPOINT_URL"),
)
console.print("   ✓ Modelos configurados\n")

#══════════════════════════════════════════════════════════════════════════════
# 📝 PROMPTS Y CADENAS (LCEL - LangChain Expression Language)
#══════════════════════════════════════════════════════════════════════════════

# 🧭 Router: Clasifica preguntas en "retrieve" (necesita RAG) o "direct" (conocimiento general)
router_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un clasificador. Decide si la pregunta NECESITA búsqueda externa (retrieve) "
     "o se puede responder con conocimiento general (direct). "
     "Responde SOLO en JSON válido con estas claves: action (valores permitidos: 'retrieve' o 'direct'), rationale (string). "
     "Reglas: retrieve=preguntas sobre YouTube; direct=saludos, chit-chat, etc.\n\n"
     "Ejemplo de respuesta:\n"
     '{{"action": "direct", "rationale": "Es un saludo simple"}}'),
    ("user", "Pregunta: {question}\nContexto: {chat_hint}")
])
# ⛓️ Cadena: prompt → LLM → JSON parser (devuelve dict con "action" y "rationale")
router = router_prompt | llm_router | JsonOutputParser()

# ⚡ Cadena Directa: Para preguntas que NO requieren RAG (saludos, conocimiento general)
direct_prompt = ChatPromptTemplate.from_messages([
    ("system", "Responde con precisión usando tu conocimiento general."),
    MessagesPlaceholder(variable_name="history"),  # 📜 Inyecta historial automáticamente
    ("user", "{input}")
])
direct_chain = direct_prompt | llm_answer

# 📚 Cadena RAG: Para preguntas que SÍ requieren contexto de documentos
rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente experto. Responde basándote en el contexto proporcionado.\n"
     "Contexto:\n{context}"),
    MessagesPlaceholder(variable_name="history"),  # 📜 Inyecta historial automáticamente
    ("user", "{input}")
])
rag_chain = rag_prompt | llm_answer

#══════════════════════════════════════════════════════════════════════════════
# 🗄️ VECTOR STORE (Qdrant - Base de Datos Vectorial)
#══════════════════════════════════════════════════════════════════════════════

console.print("🔍 Configurando Vector Store...")
api_key = os.getenv("API_KEY", "dummy-key")
embeddings_model = os.getenv("EMBEDDINGS_MODEL_ID", "text-embedding-3-small")

# 🧬 Modelo de Embeddings: Convierte texto en vectores numéricos para búsqueda semántica
embeddings = OpenAIEmbeddings(
    model=embeddings_model,
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=api_key
)

# 📐 Determinar dimensionalidad del vector según el modelo (crítico para Qdrant)
if "embeddinggemma" in embeddings_model:
    vector_size = 768
elif "text-embedding-3-large" in embeddings_model:
    vector_size = 3072
elif "text-embedding-3-small" in embeddings_model:
    vector_size = 1536
else:
    vector_size = 768  # 🔧 Fallback por defecto

# 🔌 Cliente Qdrant: Conexión con la base de datos vectorial
client = QdrantClient(os.getenv("QDRANT_URL"))

# 🏗️ Crear colección si no existe (con configuración de vectores)
if not client.collection_exists(COLLECTION_NAME):
    console.print(f"   ⚠️  Colección '{COLLECTION_NAME}' no existe. Creando...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

# 🗄️ Vector Store: Abstracción de LangChain para interactuar con Qdrant
vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)
console.print("   ✓ Vector Store listo\n")

#══════════════════════════════════════════════════════════════════════════════
# 🔄 GESTIÓN AUTOMÁTICA DE HISTORIAL (RunnableWithMessageHistory)
#══════════════════════════════════════════════════════════════════════════════

def get_history(session_id: str):
    """
    🏭 Factoría de historial: Retorna un objeto SQLChatMessageHistory para una sesión.
    LangChain llamará automáticamente esta función para cargar/guardar mensajes.
    """
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=f"sqlite:///{DB_FILE}"
    )

# 🔗 Envolver cadenas con gestión automática de historial
# Esto hace que las cadenas automáticamente:
# 1. 📥 CARGUEN el historial antes de ejecutar
# 2. 📤 GUARDEN el mensaje del usuario y la respuesta después de ejecutar

direct_chain_with_history = RunnableWithMessageHistory(
    direct_chain,
    get_history,
    input_messages_key="input",      # 🔑 Clave donde está el mensaje del usuario
    history_messages_key="history",  # 🔑 Clave donde se inyectará el historial
)

rag_chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    get_history,
    input_messages_key="input",      # 🔑 Clave donde está el mensaje del usuario
    history_messages_key="history",  # 🔑 Clave donde se inyectará el historial
)

console.print("🔄 Gestión automática de historial configurada\n")

#══════════════════════════════════════════════════════════════════════════════
# 🔧 FUNCIONES AUXILIARES
#══════════════════════════════════════════════════════════════════════════════

def retrieve(query):
    """
    🔍 Recupera documentos relevantes del vector store usando búsqueda semántica.
    
    Args:
        query (str): Pregunta del usuario convertida a embedding para comparar
    
    Returns:
        list: Documentos más similares (sin scores, para compatibilidad)
    """
    docs_with_scores = vector_store.similarity_search_with_score(query, k=K_DOCUMENTS)
    console.print(f"\n   📚 [bold cyan]Documentos recuperados: {len(docs_with_scores)}[/bold cyan]")
    
    # 📊 Mostrar detalles de cada documento con score de similitud
    for i, (doc, score) in enumerate(docs_with_scores, 1):
        # ⚠️ IMPORTANTE: En Qdrant con distancia COSINE, el score es la DISTANCIA (0=idéntico, 2=opuesto)
        # Convertimos a similitud (porcentaje) para hacerlo más intuitivo: similitud = 1 - distancia
        similarity = 1 - score
        similarity_percent = similarity * 100
        
        # 🎨 Color según relevancia del documento
        if similarity_percent >= 80:
            score_color = "green"
            relevance = "Alta"
        elif similarity_percent >= 60:
            score_color = "yellow"
            relevance = "Media"
        else:
            score_color = "red"
            relevance = "Baja"
        
        console.print(f"\n   [yellow]📄 Documento {i}:[/yellow]")
        console.print(f"      🎯 Similitud: [{score_color}]{similarity_percent:.1f}% ({relevance})[/{score_color}]")
        console.print(f"      🔗 Fuente: [blue]{doc.metadata.get('source', 'Sin fuente')}[/blue]")
        console.print(f"      📝 Título: {doc.metadata.get('title', 'Sin título')}")
        
        # 📖 Mostrar preview del contenido (primeras 150 caracteres)
        preview = doc.page_content[:150].replace('\n', ' ')
        console.print(f"      📖 Preview: [dim]{preview}...[/dim]")
        
        # 🔢 Mostrar índice de chunk si el documento fue dividido
        if 'chunk_index' in doc.metadata:
            console.print(f"      🔢 Chunk: {doc.metadata['chunk_index']}")
    
    console.print()  # Línea en blanco para separación
    
    # 🔄 Retornar solo los documentos (sin scores) para mantener compatibilidad con el resto del código
    return [doc for doc, _ in docs_with_scores]


def format_docs(docs):
    """
    📑 Formatea documentos como texto plano para inyectar en el prompt.
    Concatena el contenido de todos los docs separados por "---"
    """
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def build_chat_hint(messages):
    """
    📜 Construye un resumen del historial para el router (no todo el historial completo).
    
    El router solo necesita saber "de qué se habló" para clasificar mejor,
    no necesita el historial completo (eso lo reciben las cadenas de respuesta).
    
    Args:
        messages: Lista de mensajes del historial (HumanMessage, AIMessage)
    
    Returns:
        str: Resumen tipo "Usuario: ... | Asistente: ... | Usuario: ..."
    """
    if len(messages) < 2:
        return ""
    
    # 🔪 Tomar solo los últimos N mensajes (definido en MAX_HISTORY_MESSAGES)
    recent = messages[-MAX_HISTORY_MESSAGES:]
    hint_parts = []
    
    for msg in recent:
        role = "Usuario" if msg.type == "human" else "Asistente"
        content_preview = msg.content[:100]  # 📏 Truncar a 100 caracteres
        hint_parts.append(f"{role}: {content_preview}")
    
    return " | ".join(hint_parts)


def decide_route(question, chat_hint=""):
    """
    🧭 Clasifica la pregunta usando el router LLM.
    
    Args:
        question (str): Pregunta del usuario
        chat_hint (str): Resumen del historial reciente
    
    Returns:
        tuple: (action, rationale) donde action es "retrieve" o "direct"
    """
    try:
        result = router.invoke({
            "question": question,
            "chat_hint": chat_hint or "Sin contexto previo"
        })
        
        # ✅ Validar que tengamos los campos necesarios en el JSON
        action = result.get("action", "direct")
        rationale = result.get("rationale", "Sin explicación")
        
        # ⚠️ Validar que action sea uno de los valores permitidos
        if action not in ["retrieve", "direct"]:
            console.print(f"   ⚠️  Action inválido '{action}', usando 'direct' por defecto")
            action = "direct"
        
        console.print(f"   🤖 Decisión: [bold]{action}[/bold] - {rationale}")
        return action, rationale
        
    except Exception as e:
        # 🛡️ Fallback: En caso de error, usar respuesta directa (más seguro)
        console.print(f"   ⚠️  Error en router: {str(e)}")
        console.print(f"   ℹ️  Usando respuesta directa por defecto")
        return "direct", f"Error en clasificación, respondiendo directamente"


def run_retrieve_chain(question, session_id):
    """
    📚 Ejecuta la cadena RAG completa CON STREAMING.
    
    Flujo:
    1. 🔍 Recupera documentos relevantes de Qdrant
    2. 📋 Formatea documentos como contexto
    3. 🌊 Genera respuesta en streaming usando historial automático
    
    Args:
        question (str): Pregunta del usuario
        session_id (str): ID de sesión para historial
    
    Returns:
        dict: {"stream": generator, "references": list} o {"content": error_msg, "references": []}
    """
    console.print("   📚 Ejecutando cadena RAG con streaming...")
    try:
        # 🔍 Recuperar documentos similares
        retrieved_docs = retrieve(question)
        context = format_docs(retrieved_docs)

        # 📎 Formatear referencias únicas (evitar duplicados si varios chunks del mismo doc)
        unique_sources = {}
        for doc in retrieved_docs:
            url = doc.metadata.get("source", "Sin fuente")
            if url not in unique_sources:
                unique_sources[url] = {
                    "source": url,
                    "title": doc.metadata.get("title", "Documento"),
                    "content_preview": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }

        references = [
            {**data, "id": i}
            for i, (url, data) in enumerate(unique_sources.items(), 1)
        ]

        # 🌊 Generar respuesta con streaming (historial se inyecta/guarda automáticamente)
        stream = rag_chain_with_history.stream(
            {"input": question, "context": context},
            config={"configurable": {"session_id": session_id}}
        )

        return {"stream": stream, "references": references}

    except Exception as e:
        console.print(f"   ❌ Error en RAG: {str(e)}")
        return {
            "content": f"Error al buscar en documentos: {str(e)}",
            "references": []
        }


def run_direct_chain(question, session_id):
    """
    ⚡ Ejecuta la cadena directa (sin RAG) CON STREAMING.
    
    Flujo:
    1. 🌊 Genera respuesta en streaming usando solo conocimiento del LLM
    2. 📜 Historial se inyecta/guarda automáticamente
    
    Args:
        question (str): Pregunta del usuario
        session_id (str): ID de sesión para historial
    
    Returns:
        dict: {"stream": generator, "references": None} o {"content": error_msg, "references": None}
    """
    console.print("   ⚡ Ejecutando cadena directa con streaming...")
    try:
        # 🌊 Generar respuesta con streaming (historial se inyecta/guarda automáticamente)
        stream = direct_chain_with_history.stream(
            {"input": question},
            config={"configurable": {"session_id": session_id}}
        )
        return {"stream": stream, "references": None}
    except Exception as e:
        console.print(f"   ❌ Error: {str(e)}")
        return {"content": f"Error: {str(e)}", "references": None}


# 🗺️ Mapa de acciones: Relaciona cada decisión del router con su handler correspondiente
ACTION_HANDLERS = {
    "retrieve": run_retrieve_chain,  # 📚 Preguntas que requieren RAG
    "direct": run_direct_chain,      # ⚡ Preguntas de conocimiento general
}

#══════════════════════════════════════════════════════════════════════════════
# 🌐 ENDPOINTS DE LA API
#══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Página principal - interfaz web"""
    return app.send_static_file('index.html')


@app.route('/<path:filename>')
def static_files(filename):
    """Archivos estáticos (CSS, JS, etc.)"""
    return app.send_static_file(filename)


@app.route("/chat", methods=["POST"])
def chat_invoke():
    """
    💬 Endpoint principal del chat con STREAMING
    
    Request: {"session_id": "...", "message": "..."}
    Response: Server-Sent Events (SSE) con chunks de texto
    """
    console.print("\n" + "="*80)
    console.print("[bold cyan]📨 Nueva petición al chat (streaming)[/bold cyan]")
    console.print("="*80)

    try:
        data = request.get_json(force=True)
        session_id = data.get("session_id")
        user_text = data.get("message", "")

        if not session_id or not user_text:
            return jsonify({"error": "session_id y message son requeridos"}), 400

        console.print(f"   👤 Session: {session_id[:8]}...")
        console.print(f"   💬 Mensaje: {user_text[:100]}...")

        # 📜 Construir hint del historial para el router
        # El router recibe un RESUMEN del historial (no todo) para decidir mejor si usar RAG
        # Las cadenas de respuesta sí reciben el historial completo (lo inyecta RunnableWithMessageHistory)
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection=f'sqlite:///{DB_FILE}'
        )
        chat_hint = build_chat_hint(message_history.messages)

        # � Mostrar historial de forma visual en el terminal
        if chat_hint:
            console.print("\n   📜 [bold cyan]Contexto del historial:[/bold cyan]")
            # Dividir por el separador " | " para mostrar cada mensaje en su línea
            messages = chat_hint.split(" | ")
            for msg in messages:
                if msg.startswith("Usuario:"):
                    console.print(f"      [blue]👤 {msg[9:]}[/blue]")  # Remover "Usuario: "
                elif msg.startswith("Asistente:"):
                    console.print(f"      [green]🤖 {msg[11:]}[/green]")  # Remover "Asistente: "
            console.print()
        else:
            console.print("\n   📜 [dim]Sin historial previo[/dim]\n")

        # 🧭 Clasificar pregunta con el router
        console.print("\n   🎯 Clasificando pregunta...")
        action, rationale = decide_route(user_text, chat_hint)

        # ⚙️ Ejecutar handler correspondiente según la decisión del router
        console.print(f"\n   ⚙️  Ejecutando handler '{action}' con streaming...")

        # 🗺️ Obtener handler del mapa (fallback a direct_chain si algo falla)
        handler = ACTION_HANDLERS.get(action, run_direct_chain)
        
        # 🚀 Ejecutar handler con el texto del usuario y el session_id
        result = handler(user_text, session_id)

        # 🌊 Función generadora para Server-Sent Events (SSE)
        def generate():
            """
            🎭 Generador que emite eventos SSE progresivamente.
            
            Formato SSE: "data: {json}\n\n"
            
            Tipos de eventos:
            - metadata: Info inicial (routing, referencias) - Se envía primero
            - content: Chunks de texto del LLM - Se envían conforme se generan
            - done: Señal de finalización - Se envía al terminar
            - error: Error durante el streaming - Se envía si algo falla
            """
            try:
                # 📤 Enviar metadata inicial (routing + referencias)
                metadata = {
                    "type": "metadata",
                    "session_id": session_id,
                    "routing": {"action": action, "rationale": rationale}
                }
                
                if result.get("references"):
                    metadata["references"] = result["references"]
                
                yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"
                
                # 📝 Stream de contenido (chunks del LLM)
                if "stream" in result:
                    for chunk in result["stream"]:
                        # 🔄 LangChain puede devolver objetos AIMessage o AIMessageChunk
                        if hasattr(chunk, "content"):
                            content = chunk.content
                        else:
                            content = str(chunk)
                        
                        if content:
                            chunk_data = {
                                "type": "content",
                                "content": content
                            }
                            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                    
                    console.print(f"\n   ✅ [bold green]Streaming completado[/bold green]")
                    
                    # 🏁 Señal de fin (frontend sabrá que terminó)
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
                # ❌ Caso de error (sin stream disponible, tenemos "content" con mensaje de error)
                elif "content" in result:
                    error_data = {
                        "type": "content",
                        "content": result["content"]
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                console.print(f"\n   ❌ Error en streaming: {str(e)}")
                error_data = {
                    "type": "error",
                    "error": str(e)
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            console.print("="*80 + "\n")

        # 🔄 Retornar respuesta SSE con headers apropiados
        return Response(
            generate(),
            mimetype='text/event-stream',  # 📡 Tipo MIME para SSE
            headers={
                'Cache-Control': 'no-cache',        # 🚫 No cachear eventos
                'X-Accel-Buffering': 'no',          # 🚫 Desactivar buffering de nginx/proxies
                'Connection': 'keep-alive'          # 🔌 Mantener conexión abierta
            }
        )

    except Exception as e:
        console.print(f"\n   ❌ Error: {str(e)}")
        console.print("="*80 + "\n")
        return jsonify({"error": "Error interno", "details": str(e)}), 500


@app.route("/info", methods=["GET"])
def info():
    """ℹ️  Devuelve información sobre la configuración del servidor RAG"""
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        doc_count = collection_info.points_count
    except:
        doc_count = 0

    # 🔌 Obtener información del proveedor de modelos
    endpoint_url = os.getenv("ENDPOINT_URL", "No configurado")
    model_provider = os.getenv("MODEL_PROVIDER", "openai")
    
    # 🎨 Determinar nombre amigable del proveedor basado en la URL
    provider_name = "OpenAI"
    if "github" in endpoint_url.lower() or "models.inference.ai.azure.com" in endpoint_url:
        provider_name = "GitHub Models"
    elif "ollama" in endpoint_url.lower() or model_provider == "ollama":
        provider_name = "Ollama (Local)"
    elif "azure.com" in endpoint_url.lower() and "openai" in endpoint_url.lower():
        provider_name = "Azure OpenAI"
    elif "openai.com" in endpoint_url.lower():
        provider_name = "OpenAI"

    return jsonify({
        "status": "ok",
        "config": {
            "router_model": os.getenv("LLM_ROUTER_MODEL_ID"),
            "answer_model": os.getenv("LLM_ANSWER_MODEL_ID"),
            "embeddings_model": embeddings_model,
            "k_documents": K_DOCUMENTS,
        },
        "provider": {
            "name": provider_name,
            "endpoint_url": endpoint_url,
            "model_provider": model_provider
        },
        "vector_store": {
            "collection": COLLECTION_NAME,
            "documents_count": doc_count,
            "status": "ready" if doc_count > 0 else "empty"
        }
    })


#══════════════════════════════════════════════════════════════════════════════
# 🚀 INICIO DEL SERVIDOR
#══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    console.print("[bold green]✅ Servidor configurado[/bold green]")
    console.print("\n[bold cyan]📡 Endpoints:[/bold cyan]")
    console.print("   🏠 GET  /       - Interfaz web")
    console.print("   💬 POST /chat   - Endpoint del chat")
    console.print("   ℹ️  GET  /info   - Información del servidor")
    console.print("\n[bold yellow]🌐 http://localhost:5500[/bold yellow]")
    console.print("[dim]Presiona Ctrl+C para detener[/dim]\n")

    app.run(debug=True, port=5500, host='0.0.0.0')
