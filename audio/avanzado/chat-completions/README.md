# Conversación por Voz con IA

Para este ejemplo la idea es que puedas hablarle a la IA utilizando tu voz y que ella te responda también de forma hablada.

## 🎯 Descripción

Esta aplicación permite mantener conversaciones naturales con la IA de OpenAI usando únicamente la voz. Hablas, la IA procesa tu mensaje y te responde tanto por texto como por audio, creando una experiencia de conversación completamente fluida.

## ✨ Características

- **Conversación por voz completa**: Habla y escucha respuestas
- **Interfaz intuitiva**: Mantén presionado para hablar
- **Historial de conversación**: Ve todo el intercambio de mensajes
- **Respuestas en audio**: La IA responde con voz natural
- **Exportar conversaciones**: Guarda tus conversaciones como texto
- **Responsive**: Funciona en desktop y móvil

## 🛠️ Tecnologías Utilizadas

### Backend (API)
- **Flask**: Servidor web Python
- **OpenAI API**: 
  - Whisper (speech-to-text)
  - GPT-4o-mini (conversación)
  - TTS (text-to-speech)
- **CORS**: Para comunicación cross-origin

### Frontend (Web)
- **HTML5**: Estructura semántica
- **CSS3**: Diseño moderno y responsive
- **JavaScript**: Lógica de la aplicación
- **Web APIs**:
  - MediaRecorder (grabación)
  - getUserMedia (acceso al micrófono)
  - Audio API (reproducción)

## 📋 Prerequisitos

1. **Python 3.8+** instalado
2. **API Key de OpenAI** ([obtenerla aquí](https://platform.openai.com/api-keys))
3. **Navegador moderno** con soporte para:
   - MediaRecorder API
   - getUserMedia API
   - Web Audio API
4. **Micrófono** funcionando
5. **Conexión a internet** estable

## 🚀 Instalación y Configuración

### 1. Configurar el Backend

```bash
# Navegar al directorio de la API
cd audio/conversation/api

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar y agregar tu OPENAI_API_KEY
```

### 2. Configurar Variables de Entorno

Edita el archivo `.env`:

```env
# API Key de OpenAI (REQUERIDA)
OPENAI_API_KEY=tu_api_key_aqui

# Configuración del servidor (opcional)
DEBUG=True
HOST=0.0.0.0
PORT=5000
```

### 3. Ejecutar la Aplicación

```bash
# Desde el directorio api/
python app.py
```

El servidor estará disponible en: `http://localhost:5000`

### 4. Abrir la Interfaz Web

Abre tu navegador y ve a:
```
file:///ruta/completa/a/audio/conversation/web/index.html
```

O usa un servidor local:
```bash
# Desde el directorio web/
python -m http.server 8000
# Luego abre: http://localhost:8000
```

## 📱 Cómo Usar

### Conversación Básica
1. **Permitir acceso al micrófono** cuando se solicite
2. **Mantener presionado** el botón azul del micrófono
3. **Hablar claramente** en español
4. **Soltar el botón** para enviar tu mensaje
5. **Esperar** la respuesta por texto y audio

### Atajos de Teclado
- **Barra espaciadora**: Grabar (mantener presionado)
- **Ctrl+Enter**: Exportar conversación
- **Ctrl+Shift+C**: Limpiar conversación
- **Escape**: Cerrar modales
- **F1**: Mostrar ayuda

### Funciones Adicionales
- **Limpiar conversación**: Botón "Limpiar conversación"
- **Exportar**: Botón "Exportar" para descargar como texto
- **Reproducir audio**: Clic en ▶️ junto a respuestas de la IA

## 🔧 Configuración Avanzada

### Modificar Modelos de IA

En `api/config.py`:

```python
# Cambiar modelos de OpenAI
WHISPER_MODEL = "whisper-1"          # Para transcripción
CHAT_MODEL = "gpt-4o-mini"           # Para conversación  
TTS_MODEL = "tts-1"                  # Para síntesis de voz
TTS_VOICE = "nova"                   # Voz española femenina
```

### Personalizar Respuestas

En `api/app.py`, modifica el sistema prompt:

```python
conversation_history = [
    {"role": "system", "content": "Tu prompt personalizado aquí"}
]
```

### Ajustar Calidad de Audio

En `web/js/audio-recorder.js`:

```javascript
// Configuración de grabación
audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    sampleRate: 44100  // Calidad CD
}
```

## 🐛 Solución de Problemas

### Error: "No se puede acceder al micrófono"
- Verifica permisos del navegador
- Asegúrate de usar HTTPS (excepto localhost)
- Revisa que el micrófono esté conectado

### Error: "API no responde"
- Verifica que el servidor esté ejecutándose en puerto 5000
- Confirma que la OPENAI_API_KEY esté configurada
- Revisa la conexión a internet

### Audio no se reproduce
- Verifica permisos de audio del navegador
- Asegúrate de que los altavoces/auriculares funcionen
- Prueba con otro navegador

### Respuestas lentas
- Verifica velocidad de internet
- Considera usar `gpt-3.5-turbo` para respuestas más rápidas
- Reduce `max_tokens` en la configuración

## 📊 Endpoints de la API

### `POST /conversation`
Procesa audio y devuelve respuesta

**Request:**
- `audio`: Archivo de audio (multipart/form-data)

**Response:**
```json
{
    "user_message": "Texto transcrito",
    "assistant_message": "Respuesta de la IA",
    "audio_url": "/audio/response.wav",
    "conversation_length": 2
}
```

### `GET /conversation/history`
Obtiene historial de conversación

### `POST /conversation/clear`
Limpia el historial

### `GET /conversation/export`
Exporta conversación como texto

### `GET /health`
Verifica estado del servidor

## 🔒 Consideraciones de Seguridad

- **API Keys**: Nunca expongas tu OPENAI_API_KEY en el frontend
- **HTTPS**: Usa HTTPS en producción para getUserMedia
- **Validación**: La API valida archivos de audio
- **Rate Limiting**: Considera implementar límites de uso

## 🚀 Despliegue en Producción

### Usando Docker

```dockerfile
# Dockerfile para la API
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Variables de Entorno para Producción

```env
DEBUG=False
HOST=0.0.0.0
PORT=5000
OPENAI_API_KEY=tu_api_key_produccion
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ve el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Verifica que tengas las dependencias correctas
3. Asegúrate de que tu API key de OpenAI sea válida
4. Prueba con diferentes navegadores

## 🔮 Próximas Funcionalidades

- [ ] Soporte para múltiples idiomas
- [ ] Conversaciones grupales
- [ ] Integración con WhatsApp/Telegram
- [ ] Modo offline básico
- [ ] Reconocimiento de emociones en voz
- [ ] Personalización de voces
- [ ] Transcripción en tiempo real 