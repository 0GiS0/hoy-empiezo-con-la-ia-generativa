# LangChain - Introducción

Demo básica de LangChain mostrando conceptos fundamentales.

## Características

- ✅ Configuración básica de LangChain
- ✅ LLMs y Chat Models
- ✅ Prompt Templates
- ✅ Simple Chains
- ✅ Streaming responses
- ✅ Múltiples proveedores (OpenAI, GitHub Models, Ollama)

## Endpoints

### POST /generate
Genera texto usando LangChain chains.

**Request:**
```json
{
  "prompt": "Explica qué es la inteligencia artificial",
  "source": "github|openai|ollama",
  "temperature": 0.7
}
```

**Response:** SSE stream con el texto generado

### POST /chat
Chat conversacional con memoria.

**Request:**
```json
{
  "message": "Hola, ¿cómo estás?",
  "source": "github|openai|ollama",
  "session_id": "unique-session-id"
}
```

**Response:** SSE stream con la respuesta

## Uso

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (ver config.py)

3. Ejecutar la API:
```bash
python app.py
```

4. Abrir la UI en `web/index.html`
