# Jugando con imágenes y la Inteligencia Artificial Generativa 🖼️🤖

¡Hola developer 👋🏻! En este directorio encontrarás un montón de pruebas/demos con las que jugar para que puedas entender mejor cómo puedes usar la inteligencia artificial para entender qué hay en una imagen, crear nuevas, componer en base a otras e incluso editarlas. También te ayudará a entender los diferentes endpoints que existen.

Cuando hablamos de imágenes en IA podemos referirnos a:

- **Entender imágenes** 🧐: Analizar y comprender el contenido de una imagen, como identificar objetos, personas, texto, etc.
- **Generación de imágenes** 🎨: Crear imágenes nuevas a partir de descripciones textuales.
- **Composición de imágenes** 🧩: Combinar varias imágenes para crear una nueva.
- **Edición de imágenes** ✏️: Modificar imágenes existentes, como cambiar colores, añadir o eliminar elementos.


>[!NOTE]
Para estas demos me he basado fundamentalmente en cómo funcion OpenAI por lo que algunos endpoints pueden no estar disponibles si no tienes acceso a la API de OpenAI. ¿Por qué he usado esta? Porque a nivel personal es más barato a la hora de pagar.


Y ahora, veamos cada uno de estos aspectos en detalle.


## Vision 👁️

El primer punto, "Entender imágenes", es lo que se conoce como **Computer Vision** o simplemente **Vision**. Esto nos permite pasarle a un modelo de IA una imagen y que este nos diga qué hay en ella. Esto es muy útil para tareas como reconocimiento de objetos, análisis de escenas, etc.

En el directorio [vision](vision) encontrarás diferentes demos que muestran cómo puedes trabajar con imágenes usando IA generativa. Pero antes de entrar en cada demo es importante que sepas que para poder analizar imágenes podemos usar dos endpoints diferentes:

- `/v1/chat/completions`: Este ya lo conoces de secciones anteriores, si has seguido mi serie de IA Generativa 😇 y es el mismo que se utiliza para generar un chat o incluso text completion.
- `/v1/responses`: Este te permite enviar una imagen y recibir una respuesta generada por un modelo de IA que ha sido entrenado para entender imágenes. Este endpoint también nos servirá para generar imágenes, componerlas, editarlas, etc.

### Usando `/v1/chat/completions` para analizar imágenes

Para analizar imágenes usando el endpoint `/v1/chat/completions`, debes enviar un mensaje que incluya la imagen como parte del contenido. En el archivo [vision/chat-completions-api/app.py](vision/chat-completions-api/app.py) encontrarás un ejemplo de cómo hacerlo, tanto pasandole una URL como la imagen en base64.

Lo bueno de este ejemplo es que puedes utilizar tanto Ollama, GitHub Models como OpenAI (entre otros) para analizar imágenes usando este endpoint. En el archivo `.env-sample` encontrarás un ejemplo de cómo configurar las variables de entorno para cada uno de ellos y en base a la sección que tengas descomentadas podrás usar uno u otro.

### Usando `/v1/responses` para analizar imágenes

En el caso de este endpoint, `/v1/responses`, es muy similar al anterior, desde el punto de vista de cómo se envía la imagen, pero la respuesta que obtendrás será diferente. Este endpoint está diseñado específicamente para analizar imágenes y generar respuestas basadas en su contenido. Además  que te permite controlar el nivel de detalle del análisis.

-  Tiene un parámetro adicional `detail` que te permite decirle al modelo el nivel de detalle a usar cuando analice la imagen (`low`, `high`o `auto`). El objetivo de esto es que puedas ahorrar tokens si no necesitas un análisis muy detallado.
- Multi turno, lo que significa que puedes pedirle una imagen y luego pedirle que la mejore en siguientes turnos.
- Mostrar imagenes parciales mientras se genera la respuesta, lo que te permite ver el progreso del análisis.


Por otro lado, este endpoint nos permite generar e editar imágenes, cosa que no puedes hacer con el anterior. En el archivo [vision/responses-api/app.py](vision/responses-api/app.py) encontrarás un ejemplo de cómo hacerlo.

Sin embargo, este endpoint no está disponible en Ollama ni en GitHub Models, por lo que si quieres usarlo tendrás que usar OpenAI o algún otro servicio que lo implemente. Si intentas ejecutar el ejemplo de este endpoint con Ollama o GitHub Models, obtendrás un error indicando que el endpoint no se encuentra (404 Not Found).


## Generación de imágenes 🖼

Ahora que ya ️sabes cómo analizar imágenes, ahora vamos a ver cómo podemos generar nuevas.

Para este caso tenemos dos endpoints que podemos usar:

- `/v1/responses`: El mismo que vimos en la sección anterior, pero en este caso lo usaremos para generar imágenes a partir de un texto descriptivo. 

- `/v1/images/generations`: Este endpoint te permite generar una imagen a partir de un texto descriptivo. Es el más común y utilizado para crear imágenes nuevas basadas en prompts.


### ¿Cuál es la diferencia entre ambos?

El endpoint `/v1/responses` es más versátil, ya que también te permite analizar imágenes, generar nuevas, multi turno para ir tomando como referencia las imágenes que vas generando, etc. Por otro lado, el endpoint `/v1/images/generations` es más específico para la generación de imágenes a partir de un texto descriptivo y chin pump.

¿Y por qué no usar siempre el primero? Pues porque el segundo es más rápido y eficiente para la generación de imágenes, ya que está optimizado para ese propósito. Además, algunos modelos pueden no soportar el endpoint `/v1/responses` para generación de imágenes. Sin embargo, el primero soporta más modelos y es más versátil en cuanto a las tareas que puedes realizar con él.

En el directorio [images/generation](images/generation) encontrarás ejemplos de cómo usar ambos endpoints para generar imágenes a partir de un texto descriptivo.

### Usando `/v1/images/generations`

En el archivo [generation/images-api/app.py](generation/images-api/app.py) encontrarás un ejemplo de cómo usar este endpoint para generar imágenes a partir de un texto descriptivo. Aquí se muestra cómo enviar un prompt y recibir una imagen generada por el modelo.

En este caso el endpoint solo soporta 'gpt-image-1', 'dall-e-2', or 'dall-e-3' como modelos, por lo que si quieres usar otro modelo tendrás que usar el endpoint `/v1/responses`.

El resultado será parecido a este:

![Ejemplo de imagen generada por IA usando el endpoint /v1/images/generations](generation/images-api/example_output/image_generated_with_images-api.png)


### Usando `/v1/responses`

Por otro lado, tenemos el endpoint que vimos en la sección anterior, `/v1/responses`, que también nos permite generar imágenes a partir de un texto descriptivo. Pero te permite muchas más cosas. En primer lugar soporta otros modelos:

- gpt-4o
- gpt-4o-mini
- gpt-4.1
- gpt-4.1-mini
- gpt-4.1-nano
- o3

En el archivo [generation/responses-api/app.py](generation/responses-api/app.py) encontrarás un ejemplo de cómo usar este endpoint para generar imágenes a partir de un texto descriptivo. 

Además, como parte de ese ejemplo también estoy haciendo multi-turno, lo que significa que estoy generando una imagen y luego pidiéndole al modelo que la mejore en base a esa imagen. Esto te permite ir refinando la imagen generada hasta que obtengas el resultado deseado.

De hecho, con el primer prompt le pido lo siguiente:

```
Genera una imagen hiperrealista y detallada de un caracol de escayola azul y una rana de escayola verde, que se note claramente que son de escayola, ambos situados juntos sobre un lecho de hojas y musgo en un entorno natural iluminado suavemente. 
Asegúrate de que el caracol y la rana sean claramente visibles, con texturas realistas de escayola, y que el fondo muestre vegetación y elementos naturales como piedras o ramas. 
La composición debe transmitir tranquilidad y resaltar los colores azul y verde de los animales.
```

Y me genera algo como esto:

![Primera imagen /v1/responses](generation/responses-api/example_output/first_image.png)

Luego, tomando esa imagen como referencia, le pido que la mejore:

```
Añade una mariposa de color amarillo, con alas abiertas también de escayola, se tiene que notar claramente, 
posada suavemente sobre una hoja cerca del caracol y la rana. 
Asegúrate de que la mariposa destaque en la composición, manteniendo la iluminación suave y el entorno natural, 
y que todos los elementos conserven un aspecto hiperrealista y armonioso.
```

Y me devuelve algo como esto:

![Segunda imagen /v1/responses](generation/responses-api/example_output/second_image.png)

Y por último le pido que ahora quiero que los animales dejen de ser de escayola y sean reales: 

```
Transforma la escena para que tanto el caracol, la rana y la mariposa tengan un aspecto completamente realista, 
que dejen de ser de escayola y se conviertan en animales vivos, 
con detalles naturales en sus texturas y colores. Cambia el fondo a un bosque frondoso y realista, 
con árboles, hojas y luz filtrada entre las ramas, manteniendo la composición armoniosa y la iluminación suave. 
Asegúrate de que los animales se integren perfectamente en el entorno natural del bosque.
```

Y para esta última generación le pido que me devuelva parciales, por lo que primero me devuelve esto:

![Primer imagen parcial /v1/responses](generation/responses-api/example_output/partial_image_0.png)

Luego esto:

![Segunda imagen parcial /v1/responses](generation/responses-api/example_output/partial_image_1.png)

Y finalmente la imagen completa:

![Imagen final /v1/responses](generation/responses-api/example_output/final_frog_snail_and_butterfly.png)

¿A que mola? 😍

## Composición de imágenes 🧩

La composición de imágenes es el proceso de combinar varias imágenes para crear una nueva. Esto puede incluir superponer imágenes, recortar partes de una imagen y pegarlas en otra, o incluso fusionar varias imágenes en una sola.

Para este ejemplo he utilizado el endpoint `/v1/responses`, ya que es el más versátil y soporta la composición de imágenes de manera más eficiente. En el directorio 