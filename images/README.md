# Jugando con imágenes y la Inteligencia Artificial Generativa 🖼️🤖

¡Hola developer 👋🏻! En este directorio encontrarás un montón de pruebas/demos con las que jugar para que puedas entender mejor cómo puedes usar la inteligencia artificial para entender qué hay en una imagen, crear nuevas, componer en base a otras e incluso editarlas. También te ayudará a entender los diferentes endpoints que existen.

Cuando hablamos de imágenes en IA podemos referirnos a:

- **Entender imágenes** 🧐: Analizar y comprender el contenido de una imagen, como identificar objetos, personas, texto, etc.
- **Generación de imágenes** 🎨: Crear imágenes nuevas a partir de descripciones textuales.
- **Composición de imágenes** 🧩: Combinar varias imágenes para crear una nueva.
- **Edición de imágenes** ✏️: Modificar imágenes existentes, como cambiar colores, añadir o eliminar elementos.


>[!NOTE]
Para estas demos me he basado fundamentalmente en cómo funcion OpenAI por lo que algunos endpoints puedes no estar disponibles si no tienes acceso a la API de OpenAI. Sin embargo, puedes adaptarlos fácilmente a otros servicios similares como Hugging Face, Stability AI, etc.


El primer punto, "Entender imágenes", es lo que se conoce como **Computer Vision** o simplemente **Vision**. Así que vamos a empezar por eso:


## Vision 👁️

En el directorio [vision](vision) encontrarás diferentes demos que muestran cómo puedes trabajar con imágenes usando IA generativa. 

Antes de entrar en cada demos es importante que sepas que para poder analizar imágenes podemos usar dos endpoints diferentes:

- `/v1/chat/completions`: Este ya lo conoces de secciones anteriores, si has seguido mi serie de IA Generativa 😇 y es el mismo que se utiliza para generar un chat o incluso text completion.
- `/v1/responses`: Este te permite enviar una imagen y recibir una respuesta generada por un modelo de IA que ha sido entrenado para entender imágenes. Este endpoint también nos servirá para generar imágenes.

### Usando `/v1/chat/completions` para analizar imágenes

Para analizar imágenes usando el endpoint `/v1/chat/completions`, debes enviar un mensaje que incluya la imagen como parte del contenido. En el archivo [vision/chat-completions-api/app.py](vision/chat-completions-api/app.py) encontrarás un ejemplo de cómo hacerlo. Aquí se muestra cómo enviar una imagen y recibir una respuesta generada por el modelo.

Lo bueno de este ejemplo es que puedes utilizar tanto Ollama, GitHub Models como OpenAI (entre otros) para analizar imágenes usando este endpoint. En el archivo `.env-sample` encontrarás un ejemplo de cómo configurar las variables de entorno para cada uno de ellos y en base a la sección que tengas descomentadas podrás usar uno u otro.

### Usando `/v1/responses` para analizar imágenes

En el caso de este endpoint, `/v1/responses`, es muy similar al anterior, desde el punto de vista de cómo se envía la imagen, pero la respuesta que obtendrás será diferente. Este endpoint está diseñado específicamente para analizar imágenes y generar respuestas basadas en su contenido. Además tiene un parámetro adicional que te permite controlar el nivel de detalle del análisis.

- `detail`: te permite decirle al modelo el nivel de detalle a usar cuando analice la imagen (`low`, `high`o `auto`). El objetivo de esto es que puedas ahorrar tokens si no necesitas un análisis muy detallado.

Por otro lado, este endpoint nos permite generar e editar imágenes, cosa que no puedes hacer con el anterior. En el archivo [vision/responses-api/app.py](vision/responses-api/app.py) encontrarás un ejemplo de cómo hacerlo.

Sin embargo, este endpoint no está disponible en Ollama ni en GitHub Models, por lo que si quieres usarlo tendrás que usar OpenAI o algún otro servicio que lo implemente. Si intentas ejecutar el ejemplo de este endpoint con Ollama o GitHub Models, obtendrás un error indicando que el endpoint no se encuentra (404 Not Found).


## Generación de imágenes 🖼

Ahora que ya ️