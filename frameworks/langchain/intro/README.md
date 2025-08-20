# Introducción a LangChain (con vs. sin LangChain) ⚖️

<div align="center">

<!-- Placeholder de carátula y link al vídeo (reemplaza VIDEO_ID y TÍTULO cuando esté listo) -->
<a href="https://youtu.be/VIDEO_ID_PENDIENTE">
	<img src="https://img.youtube.com/vi/VIDEO_ID_PENDIENTE/maxresdefault.jpg" alt="Cap. X - TÍTULO PENDIENTE" width="100%" />
</a>
<br/>
<strong>TÍTULO DEL VÍDEO PENDIENTE</strong>
<br/>
<a href="https://youtu.be/VIDEO_ID_PENDIENTE">Ver vídeo</a>

</div>

---

Este ejemplo muestra el mismo caso de uso implementado de dos formas:

- sin LangChain: `intro/01-sin-langchain/app.py` usando el SDK de OpenAI directamente (base_url a GitHub Models)
- con LangChain: `intro/02-con-langchain/app.py` usando cadenas y un parser estructurado

Objetivo: comparar claridad, control del output y ergonomía.

## Qué incluye ✨

- ✅ Configuración por entorno (GitHub Models compatible con OpenAI SDK)
- ✅ En la versión con LangChain: ChatPromptTemplate → Modelo → PydanticOutputParser
- ✅ Validación estricta del output: exactamente 5 títulos con metadatos (longitud y emojis)

## Requisitos 🔧

- Python 3.10+
- Variables de entorno (ver `.env-sample` en cada carpeta)

## Instalación 📦

Desde cada carpeta (`01-sin-langchain` o `02-con-langchain`):

```bash
pip install -r requirements.txt
```

## Configuración ⚙️

1) Copia el ejemplo de entorno y edítalo:

```bash
cp .env-sample .env
```

2) Asegúrate de definir:

- `GITHUB_MODELS_URL` (p. ej., `https://models.inference.ai.azure.com`)
- `GITHUB_TOKEN` (token con acceso a GitHub Models)
- `GITHUB_MODEL_ID` (p. ej., `openai/gpt-4.1`)
- `YOUTUBE_TITLE` (título base a mejorar)
- `TEMPERATURE` (opcional, por defecto 0.7)

## Uso ▶️

Ejecuta el script de tu elección:

```bash
python app.py
```

## Diferencias clave 🔍

- **Sin LangChain**: recibes texto libre y dependes del prompt para el formato.
- **Con LangChain**: `PydanticOutputParser` obliga a un JSON válido con 5 elementos y valida longitud y emojis, devolviendo una estructura tipada. Si el modelo no cumple, lanza error.

Esto hace visible el valor de LangChain en control del output y composabilidad (prompt → modelo → parser).
