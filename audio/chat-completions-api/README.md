# 🎤 Generador de RAP AI - Chat Completions API con Audio

¡Bienvenido al Generador de RAP AI! 🎵🤖 Esta demo te permite crear raps personalizados con beatbox usando IA Generativa y diferentes voces sintéticas.

## 🎯 ¿Qué hace esta demo?

Esta aplicación web te permite:
- ✍️ **Escribir cualquier texto** que quieras convertir en rap
- 🎭 **Elegir entre 9 voces diferentes** para tu MC virtual
- 🎵 **Generar automáticamente un rap con beatbox** usando GPT-4o con capacidades de audio
- 🎧 **Reproducir y descargar** el audio generado
- 📊 **Visualizar el audio** con un espectrograma en tiempo real

## 🏗️ Arquitectura del proyecto

```
chat-completions-api/
├── 📄 README.md              # Esta guía
├── 🔧 .env                   # Variables de entorno
├── 🖥️ api/
│   └── app.py               # Servidor Flask (Backend)
└── 🌐 web/
    ├── index.html           # Interfaz de usuario
    ├── main.js              # Lógica del frontend
    ├── styles.css           # Estilos CSS
    └── visualizer.js        # Visualizador de audio
```

## 🚀 Pasos para ejecutar la demo

### 1. Prerrequisitos

Asegúrate de tener instalado:
- **Python 3.8+** 
- **Node.js** (opcional, para servidor local)
- **Acceso a OpenAI API** con el modelo `gpt-4o-audio-preview`

### 2. Configuración del entorno

#### 🔑 Configura las variables de entorno

Edita el archivo `.env` en este directorio:

```env
# OpenAI Configuration for Audio API
ENDPOINT_URL="https://api.openai.com/v1"
API_KEY="tu_api_key_de_openai_aqui"
MODEL_FOR_AUDIO="gpt-4o-audio-preview"
```

**⚠️ IMPORTANTE:** 
- Reemplaza `"tu_api_key_de_openai_aqui"` con tu API key real de OpenAI
- El modelo `gpt-4o-audio-preview` requiere acceso especial (puede estar en beta)
- **NUNCA** subas tu archivo `.env` con la API key real al repositorio

#### 📦 Instala las dependencias

Desde el directorio raíz del proyecto de audio:

```bash
# Instalar dependencias principales
pip install -r ../requirements.txt

# O específicamente para esta demo
pip install openai flask flask-cors python-dotenv rich
```

### 3. Ejecutar el backend (API)

```bash
# Navega al directorio de la API
cd api

# Ejecuta el servidor Flask
python app.py
```

Deberías ver algo como:
```
🚀 Iniciando Radio AI Station API...
📻 Servidor corriendo en: http://localhost:5001
```

### 4. Ejecutar el frontend (Interfaz web)

Tienes varias opciones para servir la interfaz web:

#### Opción A: Servidor integrado (Recomendado)
El servidor Flask ya sirve los archivos estáticos. Simplemente abre:
```
http://localhost:5001
```

#### Opción B: Servidor local independiente
```bash
# Desde el directorio web/
cd web

# Con Python
python -m http.server 8000

# Con Node.js (si tienes npx)
npx serve .

# Con Live Server en VS Code
# Haz clic derecho en index.html > "Open with Live Server"
```

### 5. Usar la aplicación

1. **Abre tu navegador** en `http://localhost:5001`
2. **Escribe tu texto** en el área de texto (viene con un ejemplo pre-cargado)
3. **Selecciona una voz** de las 9 opciones disponibles:
   - **ALLOY** - Neutral
   - **ASH** - Grave  
   - **BALLAD** - Melódica
   - **CORAL** - Suave
   - **ECHO** - Resonante (seleccionada por defecto)
   - **FABLE** - Narrativa
   - **ONYX** - Profunda
   - **NOVA** - Vibrante
   - **SHIMMER** - Brillante
4. **Haz clic en "🎤 GENERAR RAP"**
5. **Espera a que se genere** (puede tomar 10-30 segundos)
6. **Disfruta tu rap** con el reproductor y visualizador integrados

## 🔧 Cómo funciona técnicamente

### Backend (Flask API)
- **Endpoint principal:** `/generate-audio` (POST)
- **Recibe:** Mensaje de texto y voz seleccionada
- **Procesa:** Añade prompt para generar rap con beatbox
- **Llama a:** OpenAI GPT-4o con modalidad de audio
- **Devuelve:** Archivo WAV generado

### Frontend (Web)
- **HTML:** Interfaz responsive con estilo hip-hop
- **JavaScript:** Manejo de formularios y reproducción de audio
- **Visualizador:** Análisis en tiempo real del espectro de audio
- **CSS:** Diseño moderno con tema musical

### Flujo de datos
```
Usuario escribe texto → Frontend → Flask API → OpenAI → Audio WAV → Visualizador
```

## 🎨 Personalización

### Cambiar el prompt del rap
Edita la línea en `api/app.py`:
```python
prompt = "Puedes generar un rap (si añades beatbox mejor) con el mensaje siguiente: "
```

### Añadir más voces
OpenAI soporta estas voces (ya incluidas):
- alloy, ash, ballad, coral, echo, fable, onyx, nova, shimmer, sage

### Modificar estilos
Edita `web/styles.css` para cambiar la apariencia visual.

## 🐛 Solución de problemas

### Error: "Module not found"
```bash
pip install -r ../requirements.txt
```

### Error: "Invalid API key"
- Verifica que tu API key sea correcta en `.env`
- Asegúrate de tener acceso al modelo `gpt-4o-audio-preview`

### Error: "CORS policy"
- El servidor Flask ya tiene CORS configurado
- Si usas otro puerto, añádelo a la configuración CORS en `app.py`

### El audio no se reproduce
- Verifica que tu navegador soporte archivos WAV
- Revisa la consola del desarrollador (F12) para errores

### Carga lenta
- La generación de audio puede tomar tiempo
- Textos más largos requieren más procesamiento

## 💡 Ideas para expandir

- 🎵 **Múltiples géneros musicales** (rock, jazz, blues)
- 🎤 **Grabación de voz propia** como input
- 💾 **Guardar historial** de raps generados
- 🔀 **Mezcla de voces** en un mismo rap
- 🎼 **Añadir música de fondo** real
- 📱 **Versión móvil** optimizada
- 🤝 **Colaboración en tiempo real** entre usuarios

## 📚 Recursos adicionales

- [OpenAI Audio API Documentation](https://platform.openai.com/docs/guides/audio)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

## 🔐 Notas de seguridad

- ⚠️ **Nunca expongas tu API key** en el código del frontend
- 🔒 **Usa HTTPS en producción**
- 🛡️ **Implementa rate limiting** para evitar abuso
- 🔑 **Considera usar variables de entorno del sistema** en lugar de archivos .env

---

¡Disfruta creando raps con IA! 🎤🤖🔥

¿Problemas? Abre un issue en el repositorio o revisa los logs del servidor para más detalles.
