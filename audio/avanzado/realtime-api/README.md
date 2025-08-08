# 🎤 Cliente OpenAI Realtime API

Este proyecto implementa un cliente para la [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) usando WebRTC, basado en el ejemplo oficial de OpenAI.

## 🏗️ Arquitectura

### Nueva Arquitectura (Actual)
```
[Cliente Web] --WebRTC--> [OpenAI Realtime API]
      ↓                           ↑
[Servidor Python] --Ephemeral Key--┘
```

- **Cliente JavaScript**: Se conecta directamente a OpenAI usando WebRTC
- **Servidor Python**: Solo genera ephemeral keys para autenticación
- **OpenAI Realtime API**: Maneja toda la lógica de conversación y procesamiento de audio

### Ventajas de esta Arquitectura
- ✅ Conexión directa de baja latencia con OpenAI
- ✅ Streaming de audio en tiempo real
- ✅ Seguridad: No expone la API key del servidor
- ✅ Escalabilidad: El servidor solo maneja autenticación

## 🚀 Instalación y Uso

### Requisitos Previos
- Node.js (para servir archivos estáticos)
- Python 3.8+
- API Key de OpenAI

### 1. Configurar el Servidor Python

```bash
cd api
pip install -r requirements.txt
```

Crear archivo `.env`:
```bash
OPENAI_API_KEY=tu-api-key-aquí
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

Iniciar el servidor:
```bash
python server.py
```

### 2. Servir el Cliente Web

```bash
cd web
# Opción 1: Servido por el propio servidor Python (modo simple)
# Abre en el navegador: http://localhost:8000/simple.html

# Opción 2: Servir la carpeta web aparte (UI avanzada existente)
# Usando Python
python -m http.server 3000
# Usando Node.js
npx serve -p 3000
```

### 3. Usar la Aplicación

1. Modo simple (didáctico y minimal): abre `http://localhost:8000/simple.html`
      - Pulsa "Conectar" y acepta el permiso del micrófono
      - Habla y verás la transcripción + respuesta con voz y texto
      - También puedes escribir texto y pulsar Enviar
2. Modo avanzado (UI completa): abre `http://localhost:3000` o `http://localhost:8000/`
      - Ofrece métricas, logs detallados y más controles

## 🧪 Modo simple (qué incluye)

- Conectar/Desconectar una sesión con Realtime API
- Envío de audio del micrófono (WebRTC) y reproducción de la respuesta
- Transcripción automática (Whisper) y visualización del texto del asistente
- Entrada de texto opcional con generación de respuesta
- Código en ~200 líneas, centrado en lo esencial

Abre `web/simple.html` directamente desde el servidor Python: `http://localhost:8000/simple.html`.

## 🔧 Funcionalidades

### Audio en Tiempo Real
- ✅ Captura de micrófono con WebRTC
- ✅ Reproducción automática de respuestas de OpenAI
- ✅ Detección automática de inicio/fin de habla
- ✅ Audio streaming bidireccional

### Configuración de Sesión
- ✅ Instrucciones personalizables para el asistente
- ✅ Selección de voz (verse por defecto)
- ✅ Formato de audio configurable
- ✅ Transcripción automática con Whisper

### Interfaz de Usuario
- ✅ Estado de conexión en tiempo real
- ✅ Log detallado de eventos
- ✅ Controles de configuración
- ✅ Indicadores visuales de estado

## 📡 Eventos de la API

El cliente maneja automáticamente los siguientes eventos de OpenAI:

### Eventos del Cliente → OpenAI
- `session.update`: Configuración inicial de la sesión
- `conversation.item.create`: Crear nuevos elementos de conversación
- `response.create`: Solicitar respuesta del modelo

### Eventos de OpenAI → Cliente
- `session.created`: Sesión creada correctamente
- `input_audio_buffer.speech_started`: Inicio de habla detectado
- `input_audio_buffer.speech_stopped`: Fin de habla detectado
- `response.audio.delta`: Streaming de audio de respuesta
- `response.text.delta`: Streaming de texto de respuesta
- `error`: Errores de la API

## 🐛 Solución de Problemas

### Error de Ephemeral Key
Si ves errores relacionados con la ephemeral key:
1. Verifica que `OPENAI_API_KEY` esté configurada
2. Asegúrate de que el servidor Python esté ejecutándose
3. Revisa la consola del navegador para más detalles

### Error de Micrófono
Si no funciona el micrófono:
1. Verifica permisos del navegador
2. Usa HTTPS para sitios remotos
3. Prueba con diferentes navegadores

### Error de Conexión WebRTC
Si falla la conexión:
1. Verifica la conexión a internet
2. Revisa firewalls y proxies
3. Asegúrate de que OpenAI API esté disponible

## 🔍 Debug

### Logs del Cliente
El cliente registra eventos detallados en:
- Interfaz web (panel de logs)
- Consola del navegador
- Variable global `window.realtimeClient.events`

### Funciones de Debug
```javascript
// Enviar mensaje de texto desde la consola
sendMessage("Hola, ¿cómo estás?");

// Acceder al cliente
window.realtimeClient.isSessionActive
window.realtimeClient.events
```

### Logs del Servidor
El servidor Python registra:
- Solicitudes de ephemeral keys
- Errores de OpenAI API
- Estado de salud del servicio

## 📚 Referencias

- [OpenAI Realtime API Docs](https://platform.openai.com/docs/guides/realtime)
- [OpenAI Realtime Console (Oficial)](https://github.com/openai/openai-realtime-console)
- [WebRTC API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles.
