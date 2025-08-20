# Frameworks de IA

Esta sección contiene demos y ejemplos usando diferentes frameworks de IA para desarrollo de aplicaciones.

## Frameworks incluidos

### 🦜 LangChain
Framework completo para el desarrollo de aplicaciones con LLMs que incluye:
- **Intro**: Conceptos básicos y primeros pasos
- **Chains**: Cadenas de procesamiento
- **Agents**: Agentes inteligentes
- **RAG**: Retrieval Augmented Generation
- **Chat**: Aplicaciones conversacionales

## Estructura común

Cada demo sigue la estructura estándar del repositorio:
```
framework-name/
├── README.md
├── topic/
│   ├── api/          # Flask API
│   │   ├── app.py
│   │   ├── config.py
│   │   └── requirements.txt
│   └── web/          # Frontend vanilla
│       ├── index.html
│       ├── styles.css
│       └── ui.js
```

## Configuración

LangChain utiliza las mismas variables de entorno que el resto del repositorio:
- `GITHUB_MODELS_API_KEY` / `GITHUB_TOKEN`
- `OPENAI_API_KEY`
- `OLLAMA_URL`

Consulta el README principal para más detalles sobre configuración.
