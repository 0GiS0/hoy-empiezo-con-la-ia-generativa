# 🎙️ Chat Completions (voz simple)

Demo de conversación por voz: hablas al micro, se transcribe con Whisper, el modelo genera la respuesta y la API devuelve audio WAV que el navegador reproduce.

## Qué hace
- Graba audio en el navegador ([MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder))
- Envía el audio a `POST /conversation` (multipart/form-data)
- API: transcribe con `whisper-1`, llama a Chat Completions con modalidades `["text","audio"]` (voz `nova`) y devuelve `audio/wav`
- La UI reproduce el audio de respuesta y muestra estados (enviando/recibiendo)


## Instalación y ejecución
1) Backend (Flask)
- Ir a `audio/avanzado/chat-completions/api`
- Instalar dependencias: `pip install -r requirements.txt`
- Copiar `.env.example` a `.env` y rellenar valores:
  - `cp .env.example .env`
  - Edita `.env` y añade tu `OPENAI_API_KEY`
- Ejecutar: `python app.py`

2) Frontend
- No requiere servidor aparte; Flask sirve la UI en `http://localhost:5000`

## Variables de entorno
- `OPENAI_API_KEY` (requerida): clave de OpenAI.
- `MODEL_FOR_AUDIO` (opcional): modelo compatible con Chat Completions con audio. Recomendado: `gpt-4o-audio-preview`.

Notas:
- La app usa valores directos en `app.py` (host `0.0.0.0`, puerto `5000`).
- Define `MODEL_FOR_AUDIO` explícitamente en `.env` para evitar errores si el modelo por defecto cambia.

## Endpoints
- `POST /conversation`
  - Entrada: `multipart/form-data` con campo `audio` (archivo de audio)
  - Salida: binario `audio/wav` (la UI lo reproduce). En caso de error, JSON `{ "error": "..." }`.
- `GET /`
  - Sirve la interfaz web.
- `GET /<assets>`
  - Archivos estáticos (JS/CSS) desde `web/`.

## Uso rápido
- Abre `http://localhost:5000`
- Mantén pulsado el botón “Grabar” para hablar; suéltalo para enviar.
- Atajo: barra espaciadora para grabar/soltar.

## Cómo funciona (resumen)
1. La UI graba con `MediaRecorder` y envía un `Blob` como `recording.wav`.
2. La API guarda temporalmente, transcribe con `whisper-1` → texto usuario.
3. Construye historial en memoria y llama a `chat.completions.create` con `modalities=["text","audio"]`, `audio={voice:"nova", format:"wav"}` usando el modelo de `MODEL_FOR_AUDIO`.
4. Devuelve el WAV (base64 decodificado) al navegador.

## Problemas comunes
- “OPENAI_API_KEY no está configurada”: exporta la variable en tu shell.
- 400 “No se encontró archivo de audio”: asegúrate de que el front envía el campo `audio`.
- El audio no suena: revisa permisos de micrófono/sonido del navegador y que no haya otro audio en reproducción.
- Safari/iOS: verifica soporte de MediaRecorder y permisos; si falla, prueba Chrome/Edge.

## Siguientes mejoras sugeridas
- Añadir `GET /health` si se necesita monitorización.
- Persistir/mostrar historial y controles de voz.
