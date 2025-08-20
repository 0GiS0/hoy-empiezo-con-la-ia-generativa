# LangChain Demos

Ejemplos y demos usando LangChain para diferentes casos de uso de IA.

## Estructura

### 📚 Intro
Conceptos básicos de LangChain:
- Configuración inicial
- LLMs y Chat Models
- Prompts y Templates
- Chains básicas

### 🔗 Chains
Cadenas de procesamiento:
- Sequential Chains
- Router Chains
- Transform Chains
- Custom Chains

### 🤖 Agents
Agentes inteligentes:
- ReAct Agents
- Tool-using Agents
- Custom Tools
- Memory y contexto

### 🔍 RAG
Retrieval Augmented Generation:
- Document Loading
- Vector Stores
- Retrievers
- RAG Chains

### 💬 Chat
Aplicaciones conversacionales:
- Chat Memory
- Conversation Chains
- Multi-turn conversations
- Streaming responses

## Instalación

```bash
cd frameworks/langchain/[demo]/api
pip install -r requirements.txt
python app.py
```

## Variables de entorno

Usa las mismas variables que el resto del repositorio:
- `GITHUB_MODELS_API_KEY` o `GITHUB_TOKEN`
- `OPENAI_API_KEY`
- `OLLAMA_URL`
