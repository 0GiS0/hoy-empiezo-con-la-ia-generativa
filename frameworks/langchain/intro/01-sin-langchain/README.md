## Mi vida sin Langchain 😅

¡Hola developer 👋🏻!

En esta intro te muestro cómo, con el **SDK oficial de OpenAI** (en este caso GitHub Models vía API compatible), podemos pedir **5 sugerencias estructuradas** de títulos para un vídeo de YouTube 📺✨. El script principal está en `app.py` y devuelve un objeto validado con Pydantic (`Suggestions`) que incluye para cada propuesta:

- 🏷️ Título optimizado (con emojis)
- 🔢 Longitud calculada
- 😀 Lista de emojis relevantes

### ¿Qué hace exactamente este ejemplo?
1. Carga variables de entorno (`.env`) con el modelo, temperatura y título base.
2. Construye un `system` prompt explícito en español 🧠.
3. Llama a `chat.completions.parse` pasando `response_format=Suggestions` para forzar salida estructurada (tipado fuerte con Pydantic) ✅.
4. Pinta el resultado bonito en terminal usando `rich` con colores y emojis 🎨.

### Comparación rápida con la versión "con LangChain" (`../02-con-langchain/app.py`)
| Aspecto | Sin LangChain | Con LangChain |
|---------|---------------|---------------|
| Construcción de prompt | Lista manual de mensajes (`[{role, content}]`) | `ChatPromptTemplate` con variables `{title}` 🧩 |
| Parser de salida | `response_format=Suggestions` directo | `PydanticOutputParser` + `with_structured_output()` 🔧 |
| Llamada al modelo | `client.chat.completions.parse(...)` | `model_with_structured_output.invoke(prompt_value)` ⚡ |
| Abstracción / reutilización | Todo en un script | Componentes encadenables (prompt + modelo + parser) 🏗️ |
| Evolución a cadenas complejas | Manual | Facilita pipelines, tools, memory 🔄 |

En este caso las diferencias aparentes no son enormes (ambos obtienen 5 títulos estructurados). Peeero… cuando el flujo crece (retrieval, herramientas, multi‑step) la capa de LangChain aporta más organización y extensibilidad 📈.

### Chat más realista: mira el subdirectorio `chat/` 🗂️
Dentro de `chat/` tienes un ejemplo más “de verdad” comparado con su contraparte en la versión LangChain (en el directorio `02-con-langchain`). Ahí se ve:

- 💾 Persistencia de historial en SQLite.
- 🗨️ Reconstrucción del contexto previo.
- 🧱 Formateo dinámico de mensajes (system + user + assistant).
- 🔄 Preparación para extender a streaming / multi backend.

Al comparar ambos (sin vs con LangChain) notarás cómo LangChain simplifica la gestión de historial, parsing y composición de pasos cuando la lógica crece.

### Cómo ejecutar 🚀
Al usar imports relativos, ejecuta desde la raíz del repo:

```bash
python -m frameworks.langchain.intro.01-sin-langchain.app
```

> Tip: Asegúrate de tener las variables de entorno cargadas (`GITHUB_MODELS_URL`, `GITHUB_MODEL_ID`, `GITHUB_TOKEN`, `YOUTUBE_TITLE`, etc.).

### Próximo paso ➡️
Revisa ahora `../02-con-langchain/app.py` y luego el ejemplo `chat/` para apreciar mejor los beneficios de la abstracción. 

¡Seguimos! 🤖🚀