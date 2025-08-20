# 🎧 Audio · Avanzado (Parte 2)

## 🎬 Vídeo de la Parte 2 (Cap.8)

[![Audio con IA – Parte 2 (Avanzado) | Cap.8](https://img.youtube.com/vi/B78mcUiPzbk/maxresdefault.jpg)](https://youtu.be/B78mcUiPzbk "Abrir en YouTube")

## Conversación por voz con IA (avanzado)

Este escenario muestra dos formas de mantener una conversación por voz con un modelo: usando una API «clásica» de Chat Completions con audio y usando la Realtime API con WebRTC para streaming bidireccional.

## 📁 Carpetas

- `chat-completions/`
  - `api/`: Flask que expone `POST /conversation` y sirve la UI
  - `web/`: UI «push-to-talk» que graba, envía el audio y reproduce la respuesta
- `realtime-api/`
  - `api/`: Flask que solo genera ephemeral keys (`/api/token`) y sirve la UI
  - `web/`: UI WebRTC que conecta directo con OpenAI Realtime (voz en streaming)

Consulta los README específicos en cada subcarpeta para instrucciones detalladas de ejecución.

---

## Enfoque 1: Chat Completions (voz en «turnos»)

Cómo funciona (flujo actual):
- El navegador graba audio con `MediaRecorder` (pulsar para hablar).
- Envía el audio a `POST /conversation` en el backend Flask como `multipart/form-data` (campo `audio`).
- Backend:
  - Detecta el formato real (sniff de cabecera). Si no es `wav/mp3` (p. ej. `webm`, `m4a`), lo convierte a WAV con `pydub`/FFmpeg.
  - Codifica el audio en base64 y lo envía como `input_audio` dentro del mensaje del usuario a `chat.completions.create` con `modalities=["text","audio"]` y `audio={voice:"nova", format:"wav"}` usando el modelo indicado en `MODEL_FOR_AUDIO`.
  - No se invoca Whisper explícitamente: el propio modelo procesa el audio de entrada y genera texto+audio en una sola llamada.
  - Devuelve un `audio/wav` al cliente.
- La UI reproduce la respuesta.

Ventajas:
- Simplicidad operacional: HTTP request/response; no requiere WebRTC.
- Una sola llamada al modelo (sin doble paso STT+TTS), menor complejidad y coste más simple de razonar.
- Fácil de depurar (logs y trazas en el servidor) y de proteger (la API key nunca sale del backend).
- Semántica de turnos clara: útil para «push-to-talk» y flujos sin interrupciones.
- Funciona en redes donde WebRTC está restringido.

Inconvenientes:
- Mayor latencia percibida frente a Realtime: no hay streaming parcial (se espera a la respuesta completa).
- Carga del servidor: procesa audio, mantiene estado y escala con la concurrencia.
- Sin barge‑in/interrupt (no se puede interrumpir al asistente mientras responde).
- El modelo debe soportar `input_audio` y salida de audio.

Cuándo elegirlo:
- Demos rápidas, entornos controlados o cuando no puedes usar WebRTC.
- Casos con turnos claros o donde prefieres centralizar lógica y cumplimiento en el backend.

---

## Enfoque 2: Realtime API (voz en streaming, baja latencia)

Cómo funciona (flujo):
- La UI solicita una ephemeral key a `GET/POST /api/token` (servidor Flask). La API key real nunca llega al navegador.
- La UI crea una conexión WebRTC con OpenAI Realtime (`/v1/realtime?model=...`).
- Se envía audio del micrófono en streaming y se recibe audio y texto en streaming.
- Eventos útiles manejados por la UI: `session.created`, `input_audio_buffer.speech_started/stopped`, `response.text.delta`, `response.audio.delta/done`, etc. También se configura `whisper-1` para transcripción interna.

Ventajas:
- Latencia muy baja con audio/texto parciales; experiencia conversacional más natural.
- Barge‑in/interrupción: puedes hablar mientras el asistente responde.
- Menos trabajo en tu backend: solo emite ephemeral keys y sirve la UI.
- Flexibilidad: control granular de sesión y eventos; diseño full‑duplex.

Inconvenientes:
- Mayor complejidad (WebRTC, NAT/Firewall, requisitos de HTTPS en producción).
- Observabilidad/registro y persistencia del estado requieren instrumentación adicional en cliente/servidor.
- Gestión segura de ephemeral keys y políticas de uso desde el backend.
- Dependencia de soporte WebRTC del navegador/dispositivo.

Cuándo elegirlo:
- Asistentes de voz «siempre listos» o manos libres con respuesta fluida.
- Experiencias donde la latencia y la naturalidad de la conversación son críticas.

---

## Comparativa rápida

- Latencia: Realtime API ≪ Chat Completions (sin streaming de audio en CC).
- Complejidad: Chat Completions es más simple (una llamada); Realtime requiere WebRTC y manejo de eventos.
- Coste: Chat Completions ahora es una sola llamada (STT+razonamiento+TTS integrados); Realtime depende de duración y eventos.
- Escalado: Realtime descarga trabajo del backend; Chat Completions concentra cómputo en tu API.
- Capacidades: Realtime habilita barge‑in, VAD y deltas; Chat Completions es por turnos.
- Red/Entorno: Chat Completions funciona donde WebRTC está bloqueado; Realtime necesita permisos y puertos.

---

## Ejecución rápida (resumen)

- Chat Completions
  - Variables: `OPENAI_API_KEY`, `MODEL_FOR_AUDIO` (p. ej. `gpt-4o-audio-preview`)
  - Formatos de entrada: `wav` y `mp3` nativos; `webm/m4a` se convierten a WAV automáticamente (requiere FFmpeg en el sistema)
  - Arranque: `python app.py` dentro de `chat-completions/api/`
  - UI: abrir `http://localhost:5000`

- Realtime API
  - Variables: `OPENAI_API_KEY`, `HOST`, `PORT` (opcional)
  - Arranque: `python server.py` dentro de `realtime-api/api/`
  - UI: abrir `http://localhost:8000`

Para pasos detallados, ver los README de cada subcarpeta.

---

## Ideas para ampliar (opcionales)

- Medición y reporte de latencia extremo a extremo (captura → primera sílaba → audio completo) y comparativa entre enfoques.
- Barge‑in/interrupt en Chat Completions (p.ej., VAD en cliente + cortes por chunking) y streaming de texto.
- Persistencia de conversaciones y analítica (transcripciones, coste por turno, calidad de audio, intentos/retries).
- Selección dinámica de voz/idioma y detección automática de idioma.
- Fallback automático: si falla WebRTC, usar Chat Completions; si el backend está saturado, redirigir a Realtime.
- Controles de calidad de audio (AEC/NS/AGC), visualización de nivel de entrada y pruebas A/B de voces/modelos.
- Seguridad: rate limiting en emisión de ephemeral keys, autorización por usuario/sesión y expiración estricta.

---

## Notas prácticas de la guía de Audio de OpenAI

- STT (Speech-to-Text):
  - Modelo recomendado: `whisper-1` (buena calidad multilenguaje, configurable `language` si conoces el idioma; en la demo usamos `es`).
  - Entrada: archivos como WAV/MP3/M4A/WEBM/MP4; para streaming en Realtime se usa PCM16 sin contenedor.
  - Consejos: audio mono, 16 kHz o 44.1 kHz; reduce ruido (echoCancellation/noiseSuppression/autoGainControl en getUserMedia).

- TTS (Text-to-Speech):
  - En Chat Completions con audio: usa `modalities=["text","audio"]` y `audio={voice:"nova", format:"wav"}`; hay otras voces (`alloy`, `shimmer`, `verse`, etc.) y formatos (wav, mp3, opus/webm).
  - En Realtime: especifica `output_audio_format` (p. ej. `pcm16`) para minimizar latencia; el navegador reproduce vía WebRTC.

- Formatos y calidad:
  - PCM16 es óptimo para streaming (baja latencia, sin compresión). WAV es PCM16 con cabecera; MP3/Opus reducen tamaño pero añaden latencia/compresión.
  - Usa canal mono y evita resampleos innecesarios; el VAD del modelo funciona mejor con capturas limpias.

- Streaming y latencia:
  - Realtime entrega `response.text.delta` y `response.audio.delta` para respuestas parciales.
  - Habilita VAD/auto stop: eventos `speech_started/speech_stopped` permiten UX natural sin pulsar botones.
  - Barge‑in: el cliente puede hablar durante la respuesta y el modelo puede interrumpir/sobrescribir.

- Seguridad y despliegue:
  - Nunca expongas tu `OPENAI_API_KEY` en el cliente; usa ephemeral keys (servidor ↔ OpenAI) y expíralas rápido.
  - En producción, sirve sobre HTTPS (requisito para getUserMedia y WebRTC estable), configura CORS con origenes explícitos y aplica rate limiting.

- Buenas prácticas:
  - Maneja reconexiones de WebRTC y muestra estados de envío/recepción/transcripción.
  - Loguea métricas: latencia a primera palabra, a audio completo, tasa de fallos; útil para tuning de modelos/voz.
  - Persistencia opcional: guarda transcripciones y metadatos (idioma detectado, duración, coste) respetando privacidad.

---

## Referencias útiles

- OpenAI Realtime API: https://platform.openai.com/docs/guides/realtime
- OpenAI Audio (guía): https://platform.openai.com/docs/guides/audio
- WebRTC API (MDN): https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
- Whisper (transcripción): https://platform.openai.com/docs/guides/speech-to-text
