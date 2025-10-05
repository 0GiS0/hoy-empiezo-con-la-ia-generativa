"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    🦜 RAG con LangChain - API Server                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

📚 Sistema de RAG (Retrieval Augmented Generation) con routing inteligente

🔄 FLUJO DE OPERACIÓN:
┌─────────────┐
│   Usuario   │ Envía pregunta
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  🤖 Router LLM  │ Clasifica: ¿Necesita docs o respuesta directa?
└────┬─────┬──────┘
     │     │
  retrieve direct
     │     │
     ▼     ▼
┌─────────────┐  ┌──────────────┐
│ 📚 RAG      │  │ ⚡ Respuesta  │
│ (consulta   │  │ directa      │
│  vectores)  │  │ (sin docs)   │
└──────┬──────┘  └──────┬───────┘
       │                │
       └────────┬───────┘
                ▼
         ┌──────────────┐
         │  💬 Respuesta │
         │  + Referencias│
         └──────────────┘

🎯 COMPONENTES PRINCIPALES:
- Router: Decide si usar RAG o respuesta directa
- RAG Chain: Busca en documentos y genera respuesta contextual
- Direct Chain: Responde con conocimiento general del modelo
- Vector Store: Base de datos Qdrant con embeddings de documentos
- History: SQLite para mantener contexto de conversación
"""

import os

# 🌐 Framework web para crear la API REST
from flask import Flask, request, jsonify

# 🦜 LangChain - Framework para aplicaciones con LLMs
from langchain_openai import OpenAIEmbeddings  # 🧮 Para crear embeddings de texto
from langchain.chat_models import init_chat_model  # 🤖 Inicializar modelos de chat
from langchain_community.chat_message_histories import SQLChatMessageHistory  # 💾 Historial persistente
from langchain_qdrant import QdrantVectorStore  # 📚 Integración con Qdrant

# 🔍 Qdrant - Base de datos vectorial
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# 🔧 Utilidades de LangChain
from langchain_core.output_parsers import JsonOutputParser  # 📋 Parsear respuestas JSON
from langchain_core.prompts import ChatPromptTemplate  # 📝 Templates para prompts

# 🎨 Rich - Salida bonita en terminal
from rich.console import Console

# 🔐 Dotenv - Cargar variables de entorno
from dotenv import load_dotenv

# 📊 Modelo de datos para el routing
from models import RouteDecision

# ⚙️ Cargar variables de entorno desde .env
load_dotenv()

# 🌐 Inicializar aplicación Flask
app = Flask(__name__, static_folder='../web', static_url_path='')
console = Console()

# 📊 Constantes de configuración (facilita ajustes y hace el código más claro)
K_DOCUMENTS = 3  # 📚 Número de documentos a recuperar del vector store
MAX_HISTORY_MESSAGES = 6  # 💬 Máximo de mensajes del historial a considerar para contexto
COLLECTION_NAME = "youtube_guides"  # 🗂️ Nombre de la colección en Qdrant

console.print("\n[bold cyan]🚀 Iniciando servidor RAG con LangChain...[/bold cyan]\n")

###############################################################################
# 🤖 CONFIGURACIÓN DE MODELOS LLM
###############################################################################

# 🧭 Modelo para CLASIFICAR preguntas (router)
# Este modelo decide si la pregunta necesita buscar en documentos o puede
# responderse directamente con conocimiento general
console.print("📋 [yellow]Configurando modelo Router...[/yellow]")
llm_router = init_chat_model(
    model=os.getenv("LLM_ROUTER_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER", "openai"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("ENDPOINT_URL"),
)
console.print(f"   ✓ Router: {os.getenv('LLM_ROUTER_MODEL_ID')}")

# 💬 Modelo para RESPONDER preguntas
# Este modelo genera las respuestas finales (tanto RAG como directas)
console.print("📋 [yellow]Configurando modelo de Respuesta...[/yellow]")
llm_answer = init_chat_model(
    model=os.getenv("LLM_ANSWER_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER", "openai"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("ENDPOINT_URL"),
)
console.print(f"   ✓ Answer: {os.getenv('LLM_ANSWER_MODEL_ID')}\n")


###############################################################################
# 📝 PROMPTS Y CADENAS (CHAINS)
###############################################################################

# 🧭 Prompt para el ROUTER - Clasifica preguntas
# Este prompt enseña al modelo a decidir cuándo buscar en documentos
router_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un clasificador. Decide si la pregunta NECESITA búsqueda externa (retrieve) o se puede responder con conocimiento general (direct). "
     "Responde SOLO en JSON con las claves: action, rationale. "
     "Reglas: "
     "- retrieve: preguntas sobre YouTube o relacionadas con vídeos. "
     "- direct: saludos, chit-chat, traducciones, reescrituras, programación genérica que no depende de tu corpus, instrucciones de uso generales."
     ),
    ("user",
     "Pregunta: {question}\n"
     "Contexto breve (opcional): {chat_hint}\n"
     "Devuélveme JSON.")
])

# 🔗 Cadena del router: Prompt → LLM → Parser JSON
router = router_prompt | llm_router | JsonOutputParser(
    pydantic_object=RouteDecision)


# ⚡ Prompt para respuestas DIRECTAS (sin RAG)
# Para preguntas generales que no requieren consultar documentos
direct_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Responde con precisión usando solo tu conocimiento general. "
     "Si crees que faltan datos del usuario o de documentos, sugiere consultarlos, pero no inventes."),
    ("user", "{question}")
])

# 🔗 Cadena directa: Prompt → LLM
direct_chain = direct_prompt | llm_answer


# 📚 Prompt para RAG (Retrieval Augmented Generation)
# Para preguntas que requieren consultar documentos específicos
rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente experto. Responde la pregunta del usuario basándote en el contexto proporcionado. "
     "Si el contexto no contiene información relevante, indica que no tienes esa información en los documentos disponibles. "
     "Contexto:\n{context}"),
    ("user", "{question}")
])

# 🔗 Cadena RAG: Prompt → LLM
rag_chain = rag_prompt | llm_answer


rag_chain = rag_prompt | llm_answer


###############################################################################
# 💾 CONFIGURACIÓN DEL HISTORIAL DE CONVERSACIÓN
###############################################################################
# El historial permite mantener contexto entre mensajes del mismo usuario
# Se guarda en SQLite para persistencia entre reinicios

console.print("💾 [yellow]Configurando base de datos de historial...[/yellow]")

# 📁 Crear directorio para datos si no existe
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 🗄️ Archivo de base de datos SQLite
DB_FILE = os.path.join(DATA_DIR, "message_history.sqlite")
console.print(f"   ✓ Base de datos: {DB_FILE}\n")


###############################################################################
# 🔍 CONFIGURACIÓN DEL VECTOR STORE (Base de datos vectorial)
###############################################################################
# Aquí se almacenan los documentos convertidos a embeddings para búsqueda
# semántica. Permite encontrar documentos relevantes para cada pregunta.

console.print("🔍 [yellow]Configurando Vector Store (Qdrant)...[/yellow]")

# 🔐 Validar API KEY (permitir dummy para Ollama/modelos locales)
api_key = os.getenv("API_KEY")
if not api_key or api_key == "__PON_AQUI_TU_API_KEY__":
    console.print(
        "   ℹ️  [yellow]API_KEY no configurado, usando valor dummy (útil para Ollama/Model Runner)[/yellow]")
    api_key = "dummy-key"

# 🧮 Configurar modelo de embeddings
# Los embeddings convierten texto en vectores numéricos para comparación semántica
embeddings_model = os.getenv("EMBEDDINGS_MODEL_ID", "ai/embeddinggemma")
console.print(
    f"   📊 Modelo de embeddings: [bold]{embeddings_model}[/bold]")

embeddings = OpenAIEmbeddings(
    model=embeddings_model,
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=api_key
)

# 📏 Determinar dimensionalidad del vector según el modelo
# Cada modelo de embeddings produce vectores de diferente tamaño
if "embeddinggemma" in embeddings_model:
    vector_size = 768  # 🔢 Google's embeddinggemma
elif "text-embedding-3-large" in embeddings_model:
    vector_size = 3072  # 🔢 OpenAI large
elif "text-embedding-3-small" in embeddings_model:
    vector_size = 1536  # 🔢 OpenAI small
else:
    console.print(
        f"   ⚠️  [yellow]Modelo desconocido, usando 768 dimensiones por defecto[/yellow]")
    vector_size = 768

console.print(
    f"   📐 Dimensionalidad: [bold]{vector_size}[/bold] dimensiones")

# 🔌 Conectar con Qdrant (base de datos vectorial)
# Qdrant almacena los vectores y permite búsqueda por similitud
client = QdrantClient("http://qdrant:6333")
console.print(f"   🔌 Conectado a Qdrant")

# ✅ Verificar si la colección existe
# La colección debe ser creada primero ejecutando document-loaders.py
if not client.collection_exists(COLLECTION_NAME):
    console.print(
        f"   ⚠️  [red]La colección '[bold]{COLLECTION_NAME}[/bold]' no existe. Ejecuta document-loaders.py primero.[/red]")
    console.print(
        "   ℹ️  [yellow]Creando colección vacía temporalmente...[/yellow]")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=vector_size, distance=Distance.COSINE),
    )
else:
    console.print(
        f"   ✓ Colección '[bold]{COLLECTION_NAME}[/bold]' encontrada")

# 🏪 Crear objeto vector store para interactuar con Qdrant
vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)

console.print("   ✓ Vector Store listo\n")
console.print("   ✓ Vector Store listo\n")


###############################################################################
# 🔧 FUNCIONES AUXILIARES
###############################################################################

def retrieve(query):
    """
    🔍 Recupera documentos relevantes del vector store usando búsqueda semántica
    
    Args:
        query (str): Pregunta o texto a buscar
        
    Returns:
        list: Lista de documentos relevantes (objetos Document)
        
    Ejemplo:
        >>> docs = retrieve("¿Cómo hacer buenas miniaturas?")
        >>> print(f"Encontrados {len(docs)} documentos")
    """
    # 📚 Búsqueda por similitud semántica (no por palabras clave)
    retrieved_docs = vector_store.similarity_search(query, k=K_DOCUMENTS)
    console.print(
        f"   🔍 [cyan]Documentos recuperados:[/cyan] {len(retrieved_docs)}")

    # 📋 Mostrar preview de cada documento (útil para debugging)
    for i, doc in enumerate(retrieved_docs, 1):
        console.print(f"\n   [bold yellow]📄 Documento {i}:[/bold yellow]")
        console.print(f"   [dim]Metadata:[/dim] {doc.metadata}")
        content_preview = doc.page_content[:200] + "..." if len(
            doc.page_content) > 200 else doc.page_content
        console.print(f"   [dim]Contenido (preview):[/dim] {content_preview}")

    return retrieved_docs


def format_docs(docs):
    """
    📝 Formatea los documentos recuperados en un string para el contexto del LLM
    
    Args:
        docs (list): Lista de documentos recuperados
        
    Returns:
        str: Documentos formateados como texto concatenado
        
    Ejemplo:
        >>> formatted = format_docs(docs)
        >>> print(f"Contexto de {len(formatted)} caracteres")
    """
    # 🔗 Concatenar todos los documentos con separadores claros
    formatted = "\n\n".join(
        [f"--- Documento {i} ---\n{doc.page_content}" for i, doc in enumerate(docs, 1)])
    console.print(
        f"\n   [bold green]📝 Contexto formateado para el modelo:[/bold green]")
    console.print(f"   [dim]Longitud total: {len(formatted)} caracteres[/dim]")
    return formatted


def build_chat_hint(messages, max_messages=MAX_HISTORY_MESSAGES):
    """
    💬 Construye un resumen del historial reciente para ayudar al router
    
    El router usa este hint para entender el contexto de la conversación
    y tomar mejores decisiones sobre si usar RAG o respuesta directa.
    
    Args:
        messages (list): Lista de mensajes del historial
        max_messages (int): Número máximo de mensajes a incluir
        
    Returns:
        str: Resumen compacto del historial
        
    Ejemplo:
        >>> hint = build_chat_hint(history.messages)
        >>> print(hint)
        "human: Hola | ai: ¡Hola! ¿En qué puedo ayudarte? | human: ¿C..."
    """
    # 📜 Tomar solo los mensajes más recientes (evitar context overflow)
    recent = messages[-max_messages:]
    if not recent:
        return ""
    
    # 🔗 Crear resumen compacto: "tipo: contenido | tipo: contenido..."
    return " | ".join(f"{msg.type}: {msg.content[:50]}" for msg in recent)


def decide_route(question, chat_hint):
    """
    🧭 Clasifica la pregunta usando el modelo router
    
    Decide si la pregunta requiere:
    - 📚 "retrieve": Buscar en documentos (RAG)
    - ⚡ "direct": Responder directamente
    
    Args:
        question (str): Pregunta del usuario
        chat_hint (str): Resumen del historial de conversación
        
    Returns:
        tuple: (acción, razonamiento)
        
    Ejemplo:
        >>> action, reason = decide_route("¿Cómo hacer miniaturas?", "")
        >>> print(f"Acción: {action}, Razón: {reason}")
    """
    console.print("   🤔 [yellow]Clasificando pregunta...[/yellow]")
    
    try:
        # 🎯 Invocar el router con la pregunta y contexto
        routing_decision = router.invoke({
            "question": question,
            "chat_hint": chat_hint
        })

        # 📊 Extraer decisión y razonamiento
        action = routing_decision.get("action", "direct")
        rationale = routing_decision.get("rationale", "Sin explicación")

        console.print(
            f"   🤖 [magenta]Decisión:[/magenta] [bold]{action}[/bold]")
        console.print(f"   💡 [dim]Razón: {rationale}[/dim]")
        
        return action, rationale
        
    except Exception as e:
        # ⚠️ Si el router falla, usar modo seguro (direct)
        console.print(f"   ⚠️  [red]Error en router: {str(e)}[/red]")
        console.print(f"   ℹ️  [yellow]Usando modo 'direct' por seguridad[/yellow]")
        return "direct", f"Error en clasificación: {str(e)}"


        return "direct", f"Error en clasificación: {str(e)}"


def run_retrieve_chain(question):
    """
    📚 Ejecuta la cadena RAG completa
    
    Proceso:
    1. 🔍 Recupera documentos relevantes del vector store
    2. 📝 Formatea documentos como contexto
    3. 🤖 Genera respuesta usando el contexto
    4. 🔗 Agrupa referencias por URL (evita duplicados)
    
    Args:
        question (str): Pregunta del usuario
        
    Returns:
        dict: {
            "content": respuesta generada,
            "references": lista de documentos únicos consultados
        }
        
    Ejemplo:
        >>> result = run_retrieve_chain("¿Cómo optimizar títulos?")
        >>> print(result["content"])
        >>> print(f"{len(result['references'])} referencias")
    """
    console.print(f"   📚 [cyan]Ejecutando cadena RAG...[/cyan]")
    
    try:
        # 🔍 PASO 1: Recuperar documentos relevantes
        retrieved_docs = retrieve(question)
        context = format_docs(retrieved_docs)

        # 🤖 PASO 2: Generar respuesta con contexto
        console.print(f"   🤖 [green]Generando respuesta con RAG...[/green]")
        response = rag_chain.invoke({
            "question": question,
            "context": context
        })
        
        # 📚 PASO 3: Formatear referencias (agrupar por URL para evitar duplicados)
        # Cada documento recuperado puede ser un chunk del mismo artículo
        unique_sources = {}
        for doc in retrieved_docs:
            source_url = doc.metadata.get("source", "Documento sin fuente")
            
            # ✅ Si ya tenemos este enlace, saltar (evita referencias duplicadas)
            if source_url in unique_sources:
                continue
                
            # 💾 Guardar primera aparición de cada URL
            unique_sources[source_url] = {
                "source": source_url,
                "title": doc.metadata.get("title", "Documento"),
                "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            }
        
        # 🔢 Convertir diccionario a lista con IDs secuenciales
        references = []
        for i, (url, ref_data) in enumerate(unique_sources.items(), 1):
            ref_data["id"] = i
            references.append(ref_data)
        
        console.print(
            f"   📖 [cyan]Referencias únicas:[/cyan] {len(references)} (de {len(retrieved_docs)} chunks)")
        
        return {
            "content": response.content,
            "references": references
        }
        
    except Exception as e:
        # ⚠️ Si RAG falla, retornar error informativo
        console.print(f"   ❌ [red]Error en RAG: {str(e)}[/red]")
        return {
            "content": f"Lo siento, hubo un error al buscar en los documentos: {str(e)}",
            "references": []
        }


def run_direct_chain(question):
    """
    ⚡ Genera respuesta directa sin consultar documentos
    
    Usa solo el conocimiento general del modelo LLM, sin RAG.
    Útil para preguntas generales, saludos, conversación casual, etc.
    
    Args:
        question (str): Pregunta del usuario
        
    Returns:
        dict: {
            "content": respuesta generada,
            "references": None (no hay referencias en modo directo)
        }
        
    Ejemplo:
        >>> result = run_direct_chain("¡Hola!")
        >>> print(result["content"])
    """
    console.print(f"   ⚡ [green]Generando respuesta directa...[/green]")
    
    try:
        # 🤖 Generar respuesta usando solo conocimiento del modelo
        response = direct_chain.invoke({
            "question": question
        })
        
        return {
            "content": response.content,
            "references": None  # 📝 Modo directo no tiene referencias
        }
        
    except Exception as e:
        # ⚠️ Si falla, retornar error
        console.print(f"   ❌ [red]Error en respuesta directa: {str(e)}[/red]")
        return {
            "content": f"Lo siento, hubo un error al procesar tu pregunta: {str(e)}",
            "references": None
        }


# 🗺️ Mapa de acciones: asocia cada decisión del router con su handler
ACTION_HANDLERS = {
    "retrieve": run_retrieve_chain,  # 📚 RAG con documentos
    "direct": run_direct_chain,      # ⚡ Respuesta directa
}


ACTION_HANDLERS = {
    "retrieve": run_retrieve_chain,  # 📚 RAG con documentos
    "direct": run_direct_chain,      # ⚡ Respuesta directa
}


###############################################################################
# 🌐 ENDPOINTS DE LA API
###############################################################################

@app.route('/')
def index():
    """
    🏠 Página principal - Sirve la interfaz web del chat
    
    Returns:
        HTML: Archivo index.html de la carpeta web/
    """
    return app.send_static_file('index.html')


@app.route('/<path:filename>')
def static_files(filename):
    """
    📁 Sirve archivos estáticos (CSS, JS, imágenes, etc.)
    
    Args:
        filename (str): Ruta del archivo solicitado
        
    Returns:
        File: Archivo estático de la carpeta web/
    """
    return app.send_static_file(filename)


@app.route("/info", methods=["GET"])
def info():
    """
    ℹ️ Endpoint de información y debug
    
    Retorna el estado actual del servidor, configuración y estadísticas.
    Útil para verificar que todo está funcionando correctamente.
    
    Returns:
        JSON: {
            "status": "ok",
            "config": {...},
            "vector_store": {...}
        }
        
    Ejemplo:
        >>> curl http://localhost:5500/info
    """
    try:
        # 📊 Obtener estadísticas de la colección
        collection_info = client.get_collection(COLLECTION_NAME)
        
        return jsonify({
            "status": "ok",
            "message": "🚀 Servidor RAG funcionando correctamente",
            "config": {
                "router_model": os.getenv("LLM_ROUTER_MODEL_ID"),
                "answer_model": os.getenv("LLM_ANSWER_MODEL_ID"),
                "embeddings_model": embeddings_model,
                "vector_dimensions": vector_size,
                "k_documents": K_DOCUMENTS,
                "max_history": MAX_HISTORY_MESSAGES,
            },
            "vector_store": {
                "collection": COLLECTION_NAME,
                "documents_count": collection_info.points_count,
                "status": "ready" if collection_info.points_count > 0 else "empty"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener información: {str(e)}"
        }), 500


@app.route("/chat", methods=["POST"])
def chat_invoke():
    """
    💬 Endpoint principal del chat
    
    Procesa mensajes del usuario siguiendo este flujo:
    1. 📥 Recibe mensaje y session_id
    2. 📜 Recupera historial de conversación
    3. 🧭 Clasifica pregunta (router)
    4. 🔄 Ejecuta cadena apropiada (RAG o directa)
    5. 💾 Guarda respuesta en historial
    6. 📤 Retorna respuesta con referencias (si aplica)
    
    Request Body:
        {
            "session_id": "unique-session-id",
            "message": "¿Cómo hacer buenas miniaturas?"
        }
        
    Response:
        {
            "session_id": "unique-session-id",
            "reply": "Para hacer buenas miniaturas...",
            "routing": {
                "action": "retrieve",
                "rationale": "Pregunta específica sobre YouTube"
            },
            "references": [...]  // Solo si action == "retrieve"
        }
    """
    console.print("\n" + "="*80)
    console.print("[bold cyan]📨 Nueva petición al chat[/bold cyan]")
    console.print("="*80)
    
    try:
        # 📥 PASO 1: Obtener y validar datos del request
        data = request.get_json(force=True)
        session_id = data.get("session_id")
        user_text = data.get("message", "")

        # ✅ Validación básica
        if not session_id or not user_text:
            console.print("   ❌ [red]Error: Faltan parámetros requeridos[/red]")
            return jsonify({"error": "session_id y message son requeridos"}), 400
        
        console.print(f"   👤 Session ID: [bold]{session_id[:8]}...[/bold]")
        console.print(f"   💬 Mensaje: [bold]{user_text[:100]}{'...' if len(user_text) > 100 else ''}[/bold]")

        # 📜 PASO 2: Recuperar historial de mensajes de la base de datos
        console.print(f"\n   💾 [yellow]Recuperando historial...[/yellow]")
        message_history = SQLChatMessageHistory(
            session_id=session_id, 
            connection_string=f'sqlite:///{DB_FILE}'
        )

        console.print(
            f"   📚 [cyan]Mensajes previos:[/cyan] {len(message_history.messages)}")

        # 💬 PASO 3: Construir hint de contexto del historial
        # Este hint ayuda al router a entender el contexto de la conversación
        chat_hint = build_chat_hint(message_history.messages)
        if chat_hint:
            console.print(f"   💡 [dim]Hint de contexto: {chat_hint[:100]}...[/dim]")

        # 🧭 PASO 4: Clasificar la pregunta (¿RAG o directa?)
        console.print(f"\n   🎯 [yellow]Clasificando pregunta...[/yellow]")
        action, rationale = decide_route(user_text, chat_hint)

        # 🔄 PASO 5: Ejecutar la cadena correspondiente
        console.print(f"\n   ⚙️  [yellow]Ejecutando handler '{action}'...[/yellow]")
        handler = ACTION_HANDLERS.get(action, run_direct_chain)
        result = handler(user_text)

        # 💾 PASO 6: Guardar en historial (tanto pregunta como respuesta)
        console.print(f"\n   💾 [yellow]Guardando en historial...[/yellow]")
        message_history.add_user_message(user_text)
        
        # 🏷️ Agregar metadata del routing al mensaje AI usando un marcador especial
        # Formato: [ROUTING:action] contenido_real
        ai_message_with_metadata = f"[ROUTING:{action}] {result['content']}"
        message_history.add_ai_message(ai_message_with_metadata)
        console.print(f"   ✓ Historial actualizado (routing: {action})")

        # 📋 PASO 7: Preparar respuesta
        response_data = {
            "session_id": session_id,
            "reply": result["content"],
            "routing": {
                "action": action,
                "rationale": rationale
            }
        }
        
        # ✨ Añadir referencias si están disponibles (solo en modo RAG)
        if result.get("references"):
            response_data["references"] = result["references"]
            console.print(
                f"   📚 [green]Enviando {len(result['references'])} referencias[/green]")

        console.print(f"\n   ✅ [bold green]Respuesta enviada exitosamente[/bold green]")
        console.print("="*80 + "\n")
        
        return jsonify(response_data)
        
    except Exception as e:
        # ⚠️ Manejo de errores generales
        console.print(f"\n   ❌ [bold red]Error en endpoint /chat:[/bold red] {str(e)}")
        console.print("="*80 + "\n")
        return jsonify({
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500


@app.route("/history/<session_id>", methods=["GET"])
def get_history(session_id):
    """
    📜 Obtiene el historial de conversación de una sesión
    
    Args:
        session_id (str): ID de la sesión
        
    Returns:
        JSON: {
            "session_id": "...",
            "messages": [
                {"type": "human", "content": "...", "timestamp": "..."},
                {"type": "ai", "content": "...", "timestamp": "..."}
            ],
            "count": 10
        }
        
    Ejemplo:
        >>> curl http://localhost:5500/history/abc123
    """
    try:
        console.print(f"\n📜 [cyan]Recuperando historial para sesión: {session_id[:8]}...[/cyan]")
        
        # 📚 Recuperar mensajes del historial
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection_string=f'sqlite:///{DB_FILE}'
        )
        
        # 🔄 Convertir mensajes a formato serializable
        messages = []
        for msg in message_history.messages:
            msg_data = {
                "type": msg.type,  # "human" o "ai"
                "content": msg.content
            }
            
            # 🏷️ Si es mensaje AI, extraer metadata de routing si existe
            if msg.type == "ai" and msg.content.startswith("[ROUTING:"):
                # Parsear formato: [ROUTING:action] contenido_real
                try:
                    end_marker = msg.content.index("]")
                    routing_info = msg.content[9:end_marker]  # Extraer "action"
                    real_content = msg.content[end_marker + 2:]  # Extraer contenido (saltar "] ")
                    
                    msg_data["content"] = real_content
                    msg_data["routing"] = routing_info  # "retrieve" o "direct"
                except (ValueError, IndexError):
                    # Si falla el parsing, dejar el contenido original
                    pass
            
            messages.append(msg_data)
        
        console.print(f"   ✓ {len(messages)} mensajes encontrados")
        
        return jsonify({
            "session_id": session_id,
            "messages": messages,
            "count": len(messages)
        })
        
    except Exception as e:
        console.print(f"   ❌ [red]Error al recuperar historial: {str(e)}[/red]")
        return jsonify({
            "error": "Error al recuperar historial",
            "details": str(e)
        }), 500


@app.route("/history/<session_id>", methods=["DELETE"])
def clear_history(session_id):
    """
    🗑️ Elimina el historial de conversación de una sesión
    
    Args:
        session_id (str): ID de la sesión a limpiar
        
    Returns:
        JSON: {
            "success": true,
            "message": "Historial eliminado",
            "session_id": "..."
        }
        
    Ejemplo:
        >>> curl -X DELETE http://localhost:5500/history/abc123
    """
    try:
        console.print(f"\n🗑️  [yellow]Eliminando historial para sesión: {session_id[:8]}...[/yellow]")
        
        # 📚 Obtener referencia al historial
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection_string=f'sqlite:///{DB_FILE}'
        )
        
        # 🗑️ Limpiar todos los mensajes de la sesión
        message_history.clear()
        
        console.print(f"   ✓ Historial eliminado correctamente")
        
        return jsonify({
            "success": True,
            "message": "Historial eliminado correctamente",
            "session_id": session_id
        })
        
    except Exception as e:
        console.print(f"   ❌ [red]Error al eliminar historial: {str(e)}[/red]")
        return jsonify({
            "error": "Error al eliminar historial",
            "details": str(e)
        }), 500


###############################################################################
# 🚀 INICIO DEL SERVIDOR
###############################################################################

if __name__ == '__main__':
    console.print("\n[bold green]✅ Servidor configurado correctamente[/bold green]")
    console.print("\n[bold cyan]📡 Endpoints disponibles:[/bold cyan]")
    console.print("   🏠 GET    /                    - Interfaz web del chat")
    console.print("   💬 POST   /chat                - Endpoint principal del chat")
    console.print("   ℹ️  GET    /info                - Información y debug del servidor")
    console.print("   📜 GET    /history/<session>   - Obtener historial de una sesión")
    console.print("   🗑️  DELETE /history/<session>   - Eliminar historial de una sesión")
    console.print("\n[bold yellow]🌐 Iniciando servidor en http://localhost:5500[/bold yellow]")
    console.print("[dim]Presiona Ctrl+C para detener[/dim]\n")
    
    # 🚀 Iniciar servidor Flask
    app.run(debug=True, port=5500, host='0.0.0.0')
