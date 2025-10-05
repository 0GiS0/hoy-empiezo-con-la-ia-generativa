# 🦜 API RAG con LangChain

Sistema de Retrieval Augmented Generation (RAG) con routing inteligente que decide automáticamente cuándo consultar documentos o responder directamente.

## 🎯 Características

- **🧭 Router Inteligente**: Clasifica automáticamente si una pregunta necesita RAG o respuesta directa
- **📚 RAG con Qdrant**: Búsqueda semántica en base de datos vectorial
- **💬 Historial Persistente**: Mantiene contexto de conversación en SQLite
- **🎨 Referencias Visuales**: Muestra fuentes consultadas con enlaces
- **⚡ Modo Dual**: Respuestas directas para preguntas generales, RAG para preguntas específicas

## 🏗️ Arquitectura

```
Usuario → Router LLM → [RAG | Direct] → Respuesta + Referencias
                ↓
          Vector Store (Qdrant)
          History (SQLite)
```

## 📋 Variables de Entorno Requeridas

Crea un archivo `.env` en la carpeta `api/`:

```env
# Modelos LLM
LLM_ROUTER_MODEL_ID=gpt-4o-mini          # Modelo para clasificación
LLM_ANSWER_MODEL_ID=gpt-4o               # Modelo para respuestas
MODEL_PROVIDER=openai                     # Proveedor (openai, ollama, etc.)

# Embeddings
EMBEDDINGS_MODEL_ID=text-embedding-3-small  # Modelo de embeddings

# API Configuration
API_KEY=tu-api-key-aqui                   # API key del proveedor
ENDPOINT_URL=https://api.openai.com/v1    # Endpoint base

# Qdrant (opcional, usa default)
QDRANT_URL=http://qdrant:6333
```

## 🚀 Instalación y Uso

### 1. Instalar dependencias

```bash
cd frameworks/langchain/rag/api
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus valores
```

### 3. Cargar documentos en Qdrant

```bash
cd ..
python document-loaders.py
```

### 4. Iniciar servidor

```bash
cd api
python server.py
```

El servidor estará disponible en `http://localhost:5500`

## 📡 Endpoints

### `GET /`
Interfaz web del chat

### `POST /chat`
Endpoint principal del chat

**Request:**
```json
{
  "session_id": "unique-session-id",
  "message": "¿Cómo hacer buenas miniaturas?"
}
```

**Response:**
```json
{
  "session_id": "unique-session-id",
  "reply": "Para hacer buenas miniaturas...",
  "routing": {
    "action": "retrieve",
    "rationale": "Pregunta específica sobre YouTube"
  },
  "references": [
    {
      "id": 1,
      "source": "https://...",
      "title": "Consejos sobre miniaturas",
      "content_preview": "...",
      "metadata": {...}
    }
  ]
}
```

### `GET /info`
Información del servidor y estadísticas

**Response:**
```json
{
  "status": "ok",
  "config": {
    "router_model": "gpt-4o-mini",
    "answer_model": "gpt-4o",
    "embeddings_model": "text-embedding-3-small",
    "k_documents": 3
  },
  "vector_store": {
    "collection": "youtube_guides",
    "documents_count": 150,
    "status": "ready"
  }
}
```

### `GET /history/<session_id>`
Recupera el historial de conversación de una sesión

**Response:**
```json
{
  "session_id": "abc123",
  "messages": [
    {
      "type": "human",
      "content": "¿Cómo hacer miniaturas?"
    },
    {
      "type": "ai",
      "content": "Para hacer buenas miniaturas...",
      "routing": "retrieve"  // 📚 Indica que usó RAG
    },
    {
      "type": "human",
      "content": "Gracias"
    },
    {
      "type": "ai",
      "content": "¡De nada!",
      "routing": "direct"  // ⚡ Indica respuesta directa
    }
  ],
  "count": 4
}
```

**Notas:**
- El campo `routing` puede ser `"retrieve"` (usó RAG) o `"direct"` (respuesta directa)
- Esto permite al frontend mostrar avatares diferentes según el tipo de respuesta
- Los mensajes `human` no tienen campo `routing`

### `DELETE /history/<session_id>`
Elimina todo el historial de una sesión específica

**Response:**
```json
{
  "message": "Historial eliminado exitosamente",
  "session_id": "abc123"
}
```

## 🔧 Configuración Avanzada

### Ajustar número de documentos recuperados

Edita `server.py`:
```python
K_DOCUMENTS = 5  # Cambiar de 3 a 5
```

### Cambiar tamaño de historial

```python
MAX_HISTORY_MESSAGES = 10  # Cambiar de 6 a 10
```

### Personalizar prompts

Los prompts están en `server.py` en la sección "PROMPTS Y CADENAS"

## 🐛 Troubleshooting

### "La colección no existe"
```bash
# Ejecutar primero el loader de documentos
python ../document-loaders.py
```

### "Error de conexión con Qdrant"
Verifica que Qdrant esté corriendo:
```bash
docker ps | grep qdrant
```

### "API Key inválida"
Revisa tu archivo `.env` y asegúrate de que la API key es correcta

## 📚 Conceptos Clave para Aprender

- **RAG (Retrieval Augmented Generation)**: Combina búsqueda de documentos con generación de texto
- **Embeddings**: Vectores numéricos que representan significado semántico
- **Vector Store**: Base de datos optimizada para búsqueda por similitud
- **Router Pattern**: Decisión inteligente sobre qué cadena ejecutar
- **Chain**: Secuencia de operaciones con LangChain (Prompt → LLM → Parser)

## 🎓 Para Estudiantes

Este código está diseñado con fines didácticos:
- ✅ Comentarios exhaustivos con emojis
- ✅ Logging detallado de cada paso
- ✅ Docstrings con ejemplos
- ✅ Manejo de errores explicativo
- ✅ Arquitectura clara y modular

## 📖 Referencias

- [LangChain Docs](https://python.langchain.com/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)

## 🤝 Contribuir

Este es un proyecto educativo. ¡Las mejoras son bienvenidas!
