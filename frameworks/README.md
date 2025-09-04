# Frameworks de IA 🚀

¡Hola developer 👋🏻!  Esta sección agrupa demos que muestran **cómo orquestar LLMs** usando distintos frameworks / librerías. 

## Estado actual

### 🦜 LangChain (incluido ya)

Primer framework añadido. En `frameworks/langchain/intro/` tienes dos variantes:

- `01-sin-langchain/`: uso directo del SDK (baseline)
- `02-con-langchain/`: misma tarea con abstracciones (prompt template + structured output)


Objetivos cubiertos hasta ahora:
- ✅ Comparar raw SDK vs cadena declarativa

## Próximos frameworks planificados 🧭
| Framework | Enfoque principal | Cuándo destaca |
|-----------|------------------|----------------|
| Semantic Kernel (SK) | Orquestación y “skills” (plugins), planificación, fuerte integración .NET / C# | Apps enterprise .NET, planners automáticos, composición de funciones semánticas + nativas |


## Diferencias clave: LangChain vs Semantic Kernel 🔍

| Dimensión | LangChain | Semantic Kernel |
|----------|-----------|-----------------|
| Lenguajes maduros | Python, JS/TS | C# (.NET), Python, Java (en progreso) |
| Modelo mental | Chains / Graphs / Tools / Agents | Skills (semantic + native) + Planners |
| Structured output | Parsers + Pydantic (`with_structured_output`) | Functions con parámetros + JSON parsing manual o plugins |
| Planificación | Tools y experimental planners (LangGraph, ReAct, etc.) | Planners integrados (Goal → plan → ejecución) fuerte enfoque |
| Integraciones | Amplísima (vectores, DBs, retrievers) | Buenas integraciones Azure / .NET ecosistema |
| Curva de aprendizaje | Rápida para cadenas simples | Familiar a devs .NET, conceptos de “skills” nuevos para otros |
| Caso rápido prototipo | Muy ágil (prompt + chain) | Algo más setup si no estás en .NET |
| Enterprise .NET | Indirecto (bindings) | Nativo (telemetría y patrones .NET) |

Resumen: **LangChain** es muy versátil para prototipado y expansión multi‑proveedor; **Semantic Kernel** brilla cuando quieres planificación automática y estás en ecosistema .NET / Azure.

## Estructura común de demos 📁

Cada framework seguirá (o adaptará mínimamente) la convención global del repo:
```
framework-name/
├── intro/                # Ejemplos básicos / comparación
├── feature-x/            # Demos temáticas (RAG, agents, tools...)
│   ├── api/              # Flask (o FastAPI si se justifica) backend
│   └── web/              # Frontend estático (HTML/CSS/JS)
└── common/               # Reutilizables (modelos Pydantic, utilidades) si aplica
```

## Variables de entorno 🔐
Se reutilizan las mismas claves que el resto del repositorio (no duplicar nombres):
- `GITHUB_TOKEN` / `GITHUB_MODELS_API_KEY`
- `GITHUB_MODELS_URL`
- `GITHUB_MODEL_ID`
