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

¡Hola developer 👋🏻!

Este bloque de la serie compara el **mismo caso de uso** (generar 5 títulos optimizados de YouTube con estructura Pydantic) implementado de dos formas:

| Versión | Ruta | Enfoque | Cuándo usar |
|---------|------|---------|-------------|
| 🚫 Sin LangChain | `intro/01-sin-langchain/app.py` | SDK directo (`chat.completions.parse`) + `response_format=Suggestions` | Scripts simples, bajo nivel, entender la API raw |
| ✅ Con LangChain | `intro/02-con-langchain/app.py` | `ChatPromptTemplate` + `with_structured_output()` + `PydanticOutputParser` | Escalar a cadenas, añadir pasos, reutilizar componentes |

Objetivo: observar diferencias en ergonomía, extensibilidad y control del output sin perder claridad.

## Qué incluye ✨

- ✅ Configuración por entorno (GitHub Models vía OpenAI SDK compatible)
- ✅ Esquema Pydantic compartido (`Suggestions`) para ambas versiones
- ✅ Validación estricta: 5 títulos + longitud + emojis
- ✅ Logging colorido con `rich` (emojis, métricas de longitud) en ambas variantes
- ✅ En la versión LangChain: pipeline declarativa Prompt → Modelo → Parser

## Requisitos 🔧

- Python 3.10+
- Variables de entorno (ver `.env-sample` en cada carpeta)

Si no quieres tener que instalar absolutamente nada en tu máquina local puedes usar Dev Containers con la configuración que te he dejado como parte del repo. Si no sabes qué es esto, puedes echar un vistazo a este otro vídeo de mi canal:

<a href="https://youtu.be/DkKs29etRis">
	<img src="https://img.youtube.com/vi/DkKs29etRis/maxresdefault.jpg" alt="🐳 Dev containers: tu entorno de desarrollo dentro de un contenedor 💻 | Cap. 10" width="100%" />
</a>

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

Ejecuta cada variante desde la raíz (por imports relativos):

```bash
python -m frameworks.langchain.intro.01-sin-langchain.app
python -m frameworks.langchain.intro.02-con-langchain.app
```

## Diferencias clave 🔍

| Tema | Sin LangChain | Con LangChain | Beneficio práctico |
|------|---------------|---------------|--------------------|
| Prompt | Lista manual de dicts | `ChatPromptTemplate` | Reutilización y parametrización limpia |
| Estructura salida | `response_format` directo | `with_structured_output()` | Uniformidad entre proveedores futuros |
| Parser / Validación | Implícita (confías en el modelo) | Pydantic + error temprano | Menos post‑procesado manual |
| Escalado a más pasos | Copiar/pegar bloques | Composición funcional | Añadir retrieval / tools sin reescribir |
| Legibilidad | Muy explícito | Ligeramente más declarativo | Mejor para crecer |
| Cambiar modelo | Editas llamada cruda | Cambias init del chat model | Config centralizada |

## ¿Y el chat? 💬
En `01-sin-langchain/chat/` tienes un ejemplo más “real” (historial en SQLite, reconstrucción de contexto, formateo manual). Su futura versión con LangChain simplifica:

- Gestión de historial / memory abstraída
- Integración de herramientas o retrieval
- Reintentos + validación estructurada reutilizable

## Próximos pasos 🚀
1. Ejecuta ambas versiones y compara el código.
2. Modifica el esquema Pydantic (añade, por ejemplo, `categoria`) y observa el impacto.
3. Extiende la versión con LangChain añadiendo un paso de “resumen previo” antes de generar títulos.

¿Listo para hacer la versión con retrieval o herramientas? ¡Sigue explorando! 🤖
