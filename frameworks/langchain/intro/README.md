# Introducción a LangChain (con vs. sin LangChain) ⚖️

¡Hola developer 👋🏻! En esta sección quise hacer un par de vídeos donde te muestro cuál es la diferencia entre usar directamente un SDK como OpenAI para tus integraciones con la IA Generativa vs usar un framework como puede ser LangChain, para que puedas ver todas las cosas que debes tener en cuenta cuando desarrollas de una forma y de otra.

## Introducción a LangChain

<div align="center">

<!-- Vídeo 1 (Cap. 10) comparativa inicial sin vs con LangChain -->
<a href="https://youtu.be/Q40WpsPLfH8">
	<img src="https://img.youtube.com/vi/Q40WpsPLfH8/maxresdefault.jpg" alt="🦜🔗 LangChain explicado con ejemplos: tu primera comparativa 🚀 | Cap. 10" width="100%" />
</a>
<br/>
<strong>🦜🔗 LangChain explicado con ejemplos: tu primera comparativa 🚀 | Cap. 10</strong>
<br/>
<a href="https://youtu.be/Q40WpsPLfH8">Ver vídeo</a>

En este vídeo se compara **mismo caso de uso** (generar 5 títulos optimizados de YouTube con estructura Pydantic) implementado de dos formas:

| Versión | Ruta | Enfoque | Cuándo usar |
|---------|------|---------|-------------|
| 🚫 Sin LangChain | `intro/01-sin-langchain/app.py` | SDK directo (`chat.completions.parse`) + `response_format=Suggestions` | Scripts simples, bajo nivel, entender la API raw |
| ✅ Con LangChain | `intro/02-con-langchain/app.py` | `ChatPromptTemplate` + `with_structured_output()` + `PydanticOutputParser` | Escalar a cadenas, añadir pasos, reutilizar componentes |

Objetivo: observar diferencias en ergonomía, extensibilidad y control del output sin perder claridad.

## Qué incluye ✨

✅ Configuración por entorno (GitHub Models vía OpenAI SDK compatible)
✅ Esquema Pydantic compartido (`Suggestions`) para ambas versiones
✅ Validación estricta: 5 títulos + longitud + emojis
✅ Logging colorido con `rich` (emojis, métricas de longitud) en ambas variantes

## Cómo crear un chat con histórico persistente

<!-- Vídeo 2 (chat avanzado) -->
<a href="https://youtu.be/PM33QnrClzU">
	<img src="https://img.youtube.com/vi/PM33QnrClzU/maxresdefault.jpg" alt="Construyendo chats con IA 🤖 OpenAI SDK vs LangChain explicado fácil 🎯 | Cap. 11" width="100%" />
</a>
<br/>
<strong>Construyendo chats con IA 🤖 OpenAI SDK vs LangChain explicado fácil 🎯 | Cap. 11</strong>
<br/>
<a href="https://youtu.be/PM33QnrClzU">Ver vídeo</a>

</div>

En este segundo vídeo se profundiza en un **chat con memoria y formato de salida consistente** implementado de dos maneras: a manos con el SDK y con LangChain.

| Versión | Directorio | Enfoque técnico | Puntos clave |
|---------|------------|-----------------|--------------|
| 🚫 Sin LangChain | `frameworks/langchain/intro/01-sin-langchain/chat` | SDK directo + SQLite | Persistencia manual del historial, reconstrucción de contexto concatenando turnos, control explícito de tokens, manejo de errores artesanal |
| ✅ Con LangChain | `frameworks/langchain/intro/02-con-langchain/chat` | `ChatPromptTemplate` + Memory + Parsers | Memory integrada (separa lógica del formateo), fácil añadir herramientas / retrieval, reintentos y validación estructurada reutilizable |


Y esto es solo un ejemplo de todo lo que tendrías que hacer de forma manual si no usas un framework que te abstraiga muchas de estas tareas comunes (que después de crear y editar el vídeo se me ocurrieron muchas más 😅...). Y lo mismo me ocurrió con LangChain, que tiene muchas más funcionalidades que no he podido cubrir en este vídeo introductorio ¡Que además están en constante evolución! (Sin hablar todavía de LangGraph o LangSmith 🥲)

Entra en cada uno de los dos directorios (`chat` dentro de cada variante) para ver el código y diferencias.

