# Jugando con imágenes y la Inteligencia Artificial Generativa

¡Hola developer 👋🏻! En este directorio encontrarás un montón de pruebas/demos con las que jugar para que puedas entender mejor cómo puedes usar la inteligencia artificial para entender qué hay en una imagen, crear nuevas, componer en base a otras e incluso editarlas. También te ayudará a entender los diferentes endpoints que existen.

Cuando hablamos de imágenes en IA podemos referirnos a:

- **Entender imágenes**: Analizar y comprender el contenido de una imagen, como identificar objetos, personas, texto, etc.
- **Generación de imágenes**: Crear imágenes nuevas a partir de descripciones textuales.
- **Edición de imágenes**: Modificar imágenes existentes, como cambiar colores, añadir o eliminar elementos.
- **Composición de imágenes**: Combinar varias imágenes para crear una nueva.


El primer punto, "Entender imágenes", es lo que se conoce como **Computer Vision** o simplemente "Vision". Así que vamos a empezar por eso:

## Vision

Cuando hablamos de vision en IA es la capacidad del modelo de "ver" y entender imágenes. Si hay un texto en la imagen, el modelo puede también entenderlo.
Además es capaz de identificar objetos, personas, animales, etc. en la imagen. Pero hay alguna limitaciones: https://platform.openai.com/docs/guides/images-vision?api-mode=responses#limitations

Por lo tanto se le puede dar como input imágenes en diferentes formatos:

- URL de la imagen
- Base64 de la imagen
- Archivo de imagen usando el parámetro `files` de la API