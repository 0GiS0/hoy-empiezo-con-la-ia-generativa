# 🦜🔗 RAG con LangChain

> **Demo de Retrieval-Augmented Generation (RAG) usando LangChain, Qdrant y OpenAI**

Esta demo muestra cómo construir un sistema RAG completo utilizando LangChain para crear un asistente inteligente que ayuda a los creadores de contenido de YouTube con información actualizada de la documentación oficial de Google.

---

## 📋 ¿Qué es RAG?

**Retrieval-Augmented Generation (RAG)** es una técnica que combina:

1. 🔍 **Recuperación de información** - Busca documentos relevantes en una base de datos vectorial
2. 🤖 **Generación de respuestas** - Usa un modelo de lenguaje (LLM) para generar respuestas basadas en la información recuperada

Esto permite que los modelos de IA accedan a información específica de tu dominio, actualizada y precisa, sin necesidad de reentrenarlos.

---

## 🏗️ Arquitectura de la Demo

### 📦 Componentes Principales

1. **`document-loaders.py`** 📥
   - Carga y procesa URLs de la documentación de YouTube
   - Divide el contenido en chunks manejables
   - Genera embeddings y los almacena en Qdrant
   - Usa `WebBaseLoader` y `RecursiveCharacterTextSplitter` de LangChain

2. **`api/server.py`** 🚀
   - API Flask que expone el sistema RAG
   - **Router inteligente**: clasifica si una pregunta necesita RAG o puede responderse directamente
   - **Historial de conversación**: usa SQLite para persistir el contexto
   - **Búsqueda semántica**: consulta Qdrant para recuperar información relevante

3. **`web/`** 🌐
   - Interfaz de chat moderna y responsive
   - Persistencia de sesiones con `localStorage`
   - Comunicación asíncrona con el backend

4. **`api/models.py`** 📐
   - Define el modelo Pydantic para las decisiones del router
   - Estructura las respuestas JSON

---

## 🎯 Flujo de Trabajo

### 1️⃣ Indexación (una sola vez)

```bash
python document-loaders.py
```

**¿Qué hace?**
- 🌐 Carga 18 guías oficiales de YouTube sobre creación de contenido
- ✂️ Divide cada documento en chunks de 1000 caracteres (con overlap de 200)
- 🧮 Genera embeddings usando el modelo configurado (ej: `text-embedding-3-large`)
- 💾 Almacena todo en Qdrant (colección: `youtube_guides`)

### 2️⃣ Consultas (API + Web)

```bash
# Iniciar el servidor
cd api
python server.py
```

**Flujo de una consulta:**

```
Usuario hace pregunta
      ↓
🤖 Router LLM clasifica:
   - ¿Necesita RAG? → "retrieve"
   - ¿Conocimiento general? → "direct"
      ↓
   [Si "retrieve"]
      ↓
🔍 Búsqueda semántica en Qdrant
      ↓
📚 Recupera documentos relevantes
      ↓
💬 LLM genera respuesta con contexto
      ↓
💾 Guarda en historial (SQLite)
      ↓
✅ Responde al usuario
```

---

## 🚀 Cómo Ejecutar la Demo

### Prerrequisitos

- 🐳 Docker (para Qdrant)
- 🐍 Python 3.8+
- 🔑 API Key de OpenAI o GitHub Models

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en la carpeta `api/`:

```env
# Endpoints
ENDPOINT_URL=https://models.inference.ai.azure.com
API_KEY=tu_github_token_aqui

# Modelo para el router (clasifica preguntas)
LLM_ROUTER_MODEL_ID=gpt-4o-mini
MODEL_PROVIDER=openai

# Modelo para respuestas
LLM_ANSWER_MODEL_ID=gpt-4o

# Modelo de embeddings
EMBEDDINGS_MODEL_ID=text-embedding-3-large
```

### 2. Instalar Dependencias

```bash
# En la raíz del proyecto RAG
pip install -r requirements.txt

# En la carpeta api/
cd api
pip install -r requirements.txt
```

### 3. Levantar Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

🔍 Accede al dashboard: http://localhost:6333/dashboard

### 4. Indexar Documentos

```bash
python document-loaders.py
```

**Salida esperada:**
```
🔍 Indexando: Configurar la audiencia de un canal...
🔍 Indexando: Consejos para subir vídeos...
...
🚀 Indexación completada.
```

### 5. Iniciar el Servidor

```bash
cd api
python server.py
```

El servidor estará disponible en: http://127.0.0.1:5500

### 6. Abrir la Interfaz Web

Abre `web/index.html` en tu navegador o usa un servidor estático:

```bash
cd web
python -m http.server 5500
```

---

## 🎨 Características Clave

### 🧠 Router Inteligente

El sistema usa un LLM para clasificar preguntas automáticamente:

- **"retrieve"** → Preguntas sobre documentación, políticas, hechos específicos
- **"direct"** → Saludos, traducciones, conocimiento general

**Ejemplo:**
- ❓ "¿Cuál es la mejor resolución para miniaturas?" → `retrieve` (necesita docs)
- ❓ "¿Qué día es hoy?" → `direct` (conocimiento general)

### 💾 Historial Conversacional

Cada sesión se identifica con un `session_id` único almacenado en SQLite:

```python
message_history = SQLChatMessageHistory(
    session_id=session_id,
    connection_string=f'sqlite:///{DB_FILE}'
)
```

Esto permite conversaciones contextuales donde el modelo "recuerda" mensajes anteriores.

### 🔍 Búsqueda Semántica

Usa `QdrantVectorStore` para encontrar los chunks más relevantes:

```python
retrieved_docs = vector_store.similarity_search(query)
```

Los embeddings capturan el **significado semántico**, no solo palabras clave.

---

## 📚 Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| 🦜 Framework RAG | LangChain |
| 💾 Base de datos vectorial | Qdrant |
| 🤖 Modelos LLM | OpenAI / GitHub Models |
| 🔢 Embeddings | `text-embedding-3-large` |
| 🌐 Backend | Flask |
| 💬 Frontend | Vanilla JS + HTML/CSS |
| 🗄️ Historial | SQLite |

---

## 🔧 Estructura del Proyecto

```
frameworks/langchain/rag/
│
├── document-loaders.py      # 📥 Script de indexación
├── requirements.txt          # 📦 Dependencias Python
│
├── api/                      # 🚀 Backend Flask
│   ├── server.py             # API principal con router
│   ├── models.py             # Modelos Pydantic
│   ├── requirements.txt      # Dependencias API
│   ├── .env.sample           # Plantilla de variables
│   └── data/                 # 💾 SQLite (generado en runtime)
│
└── web/                      # 🌐 Frontend
    ├── index.html            # Interfaz de chat
    ├── chat.js               # Lógica del cliente
    └── styles.css            # Estilos
```

---

## 🎓 Conceptos Clave de LangChain

### 1. Document Loaders 📄

```python
from langchain_community.document_loaders.web_base import WebBaseLoader

loader = WebBaseLoader(web_path="https://example.com")
docs = loader.load()
```

Cargan contenido de diversas fuentes (web, PDFs, bases de datos, etc.).

### 2. Text Splitters ✂️

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(docs)
```

Dividen documentos grandes en pedazos manejables manteniendo coherencia.

### 3. Vector Stores 🗄️

```python
from langchain_qdrant import QdrantVectorStore

vector_store = QdrantVectorStore(
    client=client,
    collection_name="youtube_guides",
    embedding=embeddings
)
```

Almacenan embeddings para búsqueda semántica eficiente.

### 4. Chat Message History 💬

```python
from langchain_community.chat_message_histories import SQLChatMessageHistory

message_history = SQLChatMessageHistory(
    session_id=session_id,
    connection_string='sqlite:///chat.db'
)
```

Persisten conversaciones para contexto multi-turn.

### 5. Prompts & Chains ⛓️

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente experto..."),
    ("user", "{question}")
])

chain = prompt | llm | JsonOutputParser()
```

Componen flujos de trabajo complejos de manera declarativa.

---

## 🌟 Casos de Uso

Este patrón se puede adaptar para:

- 📖 **Documentación técnica**: Asistente para APIs, SDKs, manuales
- 🏢 **Conocimiento empresarial**: Políticas internas, procedimientos
- 📰 **Noticias y artículos**: Mantenerse actualizado con información reciente
- 🛒 **E-commerce**: Catálogos de productos, especificaciones
- ⚖️ **Legal/compliance**: Búsqueda en contratos, regulaciones

---

## 🔮 Próximas Mejoras

- [ ] Implementar streaming de respuestas (SSE)
- [ ] Agregar filtros por metadatos en Qdrant
- [ ] Sistema de re-ranking de documentos
- [ ] Interfaz para visualizar chunks recuperados
- [ ] Métricas de calidad (precision, recall)
- [ ] Soporte multi-idioma

---

## 📖 Recursos Adicionales

- 📘 [LangChain Documentation](https://python.langchain.com/docs/)
- 🔍 [Qdrant Vector Database](https://qdrant.tech/documentation/)
- 🤖 [GitHub Models](https://github.com/marketplace/models)
- 📚 [RAG Tutorial by LangChain](https://python.langchain.com/docs/tutorials/rag/)

---

## 💡 Notas Importantes

- **Calidad de los chunks**: El tamaño y overlap afectan directamente la precisión
- **Modelo de embeddings**: Modelos más grandes (`text-embedding-3-large`) son más precisos pero más costosos
- **Router threshold**: Puedes ajustar la sensibilidad del clasificador modificando el prompt
- **Historial**: Por defecto usa SQLite local; considera PostgreSQL para producción

---

## 🤝 Contribuciones

¿Ideas para mejorar esta demo? ¡Los PRs son bienvenidos! 🚀

---

**Happy RAG building! 🦜🔗✨**
