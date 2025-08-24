## Mi vida CON LangChain 🤝🦜

¡Hola developer 👋🏻!

Este ejemplo es la contraparte del directorio `../01-sin-langchain` pero usando **LangChain** para estructurar mejor el flujo. Seguimos generando **5 sugerencias estructuradas** de títulos para YouTube, pero ahora delegamos en utilidades de la librería para hacer el código más componible y escalable.

### ¿Qué cambia respecto a la versión "sin"?
| Aspecto | Sin LangChain | Con LangChain |
|---------|---------------|---------------|
| Prompt | Lista manual de dicts | `ChatPromptTemplate` con placeholders `{title}` |
| Parser | `response_format=Suggestions` directo | `PydanticOutputParser` + `with_structured_output()` |
| Ejecución | `client.chat.completions.parse(...)` | `model_with_structured_output.invoke(prompt_value)` |
| Reusabilidad | Script monolítico | Componentes combinables (prompt, modelo, parser) |
| Extender (RAG, tools) | Más código manual | Se añaden cadenas / wrappers fácilmente |
| Control temperatura / provider | Parámetros crudos | Config centralizada al inicializar el chat model |

### Puntos clave del código (`app.py`)
1. `init_chat_model(...)` inicializa un modelo OpenAI/GitHub Models con provider unificado.
2. `PydanticOutputParser` define el esquema `Suggestions` (mismo Pydantic que la versión sin LC) ✅.
3. `model.with_structured_output(parser.get_output_schema())` fuerza formato estructurado sin repetir lógica.
4. `ChatPromptTemplate` construye el mensaje final y permite inyectar variables fácilmente.
5. Logging con `rich` mantiene trazabilidad (config, prompt generado, respuesta, métricas de longitud) 🎨.

### ¿Por qué esto escala mejor? 🚀
- Añadir otro paso (ej: resumen previo, verificación, re-rank) = encadenar más prompts/models.
- Integrar herramientas / retrieval = plug-ins estándar de LangChain en vez de escribir glue manual.
- Cambiar de modelo/proveedor = ajustar un único inicializador.

### Cómo ejecutar 🏁
Ejecuta desde la raíz para que funcionen los imports relativos:

```bash
python -m frameworks.langchain.intro.02-con-langchain.app
```

> Tip: Reutiliza las mismas variables de entorno (`GITHUB_MODELS_URL`, `GITHUB_MODEL_ID`, `GITHUB_TOKEN`, `YOUTUBE_TITLE`, `TEMPERATURE`).

### Siguiente paso
Compara ahora los subdirectorios `chat/` (sin LC) y su versión equivalente futura con LangChain para ver ventajas en manejo de historial, persistencia y formateo avanzado. 🤖🔄

¡A experimentar! 💡