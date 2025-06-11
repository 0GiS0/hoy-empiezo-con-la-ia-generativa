# Capítulo 4: Crear un chat con IA Generativa

¡Hola developer 👋🏻! En este directorio encontrarás un ejemplo de cómo crear un chat que utilice IA Generativa para responder a los usuarios. Si quieres ver el vídeo relacionado con este

En este caso lo que mostré fueron estos dos directorios:

- `api`: Aquí encontrarás el código que implementa la API del chat.
- `web`: Aquí encontrarás el código que implementa la interfaz web del chat.


## API

### ¿Cómo está implementada la API del chat?

La API está implementada usando **Flask** (Python) y permite interactuar con modelos de IA generativa para responder a los mensajes de los usuarios. A continuación se describe su funcionamiento:

#### Estructura de la API

- **/api/app.py**: Archivo principal que define los endpoints y la lógica del servidor.
- **/api/config.py**: Configuración de variables de entorno y modelos.
- **/api/requirements.txt**: Dependencias necesarias para ejecutar la API.

#### Endpoints principales

- **POST `/chat`**  
  Este endpoint recibe mensajes del usuario y retorna respuestas generadas por un modelo de IA.  
  - **Body JSON**:
    - `messages`: Lista de mensajes previos del chat (puede ser un string o un array de objetos `{role, content}`).
    - `source`: (opcional) Fuente del modelo a usar (`github` o `ollama`). Por defecto es `github`.
  - **Respuesta**:  
    Respuesta en formato *stream* (text/event-stream) con el texto generado por la IA.

#### Funcionamiento general

1. **Inicialización**:  
   Al iniciar, la API carga la configuración de los modelos y las claves necesarias desde variables de entorno.

2. **Recepción de mensajes**:  
   El endpoint `/chat` recibe los mensajes del usuario y determina qué modelo utilizar según el parámetro `source`.

3. **Construcción del prompt**:  
   Se añade un mensaje de sistema para guiar a la IA y se combinan los mensajes del usuario.

4. **Llamada al modelo**:  
   Utiliza la librería `openai` para interactuar con el modelo seleccionado (puede ser un modelo propio o uno de Ollama).

5. **Respuesta en streaming**:  
   La respuesta se envía en tiempo real al cliente usando *Server-Sent Events* (SSE), permitiendo mostrar la respuesta de la IA a medida que se genera.

#### Ejemplo de uso

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "¿Cómo optimizo mi canal de Youtube?"}], "source": "github"}'
```

#### Personalización

- Puedes cambiar el modelo o la fuente modificando las variables de entorno en `.env`.
- El prompt del sistema puede adaptarse en `app.py` para cambiar el comportamiento de la IA.

#### Dependencias

- Flask
- flask-cors
- openai
- python-dotenv
- tiktoken

---

Para más detalles revisa el código en el directorio `api`.

## Web

### ¿Cómo está implementada la web del chat?

La interfaz web está implementada usando **HTML**, **CSS** y **JavaScript** puro, sin frameworks. Permite a los usuarios interactuar con la API del chat y visualizar las respuestas generadas por la IA en tiempo real.

#### Estructura de la web

- **/web/index.html**: Estructura principal de la página y elementos del chat.
- **/web/styles.css**: Estilos visuales, animaciones y diseño responsivo.
- **/web/ui.js**: Lógica de interacción, manejo del historial y comunicación con la API.

#### Funcionamiento general

1. **Interfaz de usuario**:  
   La web muestra un área de historial de chat, un campo de entrada y un botón para enviar mensajes. Incluye un selector para elegir el modelo de IA (GitHub u Ollama).

2. **Envío de mensajes**:  
   Al enviar un mensaje, este se agrega al historial y se envía a la API mediante una petición `POST` a `/chat`.

3. **Recepción de respuestas**:  
   La respuesta de la IA se recibe en *stream* y se muestra en tiempo real, permitiendo ver cómo la IA "escribe" la respuesta.

4. **Historial y formato**:  
   El historial se mantiene en memoria y se renderiza usando Markdown para soportar respuestas enriquecidas (código, listas, enlaces, etc).

5. **Personalización visual**:  
   Los mensajes del usuario y del bot tienen estilos y avatares diferenciados, con animaciones y efectos visuales.

#### Ejemplo de flujo

1. El usuario escribe una pregunta y pulsa "Enviar".
2. El mensaje aparece en el chat con un avatar personalizado.
3. El bot muestra un indicador de "escribiendo..." mientras espera la respuesta de la API.
4. La respuesta de la IA aparece progresivamente, renderizada como Markdown.

#### Personalización

- Puedes modificar los estilos en `styles.css` para cambiar colores, fuentes o animaciones.
- El archivo `ui.js` permite ajustar la lógica de interacción, agregar nuevas funcionalidades o cambiar el comportamiento del chat.
- El selector de modo permite alternar entre diferentes modelos de IA disponibles en la API.

#### Dependencias

- [marked.js](https://marked.js.org/) para renderizar Markdown en las respuestas del bot.
- [Font Awesome](https://fontawesome.com/) para iconos.

---

Para más detalles revisa el código en el directorio `web`.

