# 🚀✨ Hoy empiezo con IA Generativa 🌟🤖

¡Hola developer 👋🏻! Este repo contiene todo lo que necesitas para empezar a trabajar con IA generativa. Desde qué puedes usar para empezar gratis en tu máquina local, o en la nube, hasta ejemplos de los diferentes conceptos que necesitas aprender para poder usar IA generativa en tus proyectos. Pero todo ello desde el punto de vista del desarrollador, para que puedas ver cómo realmente puedes integrar esto dentro de una aplicación que tú estés desarrollando, dejando a un lado las aplicaciones de terceros que circulan por la red. Este repo forma parte de mi serie sobre IA Generativa en mi canal de YouTube.

## 📚 Índice

- [💡 Capítulo 1: Todo lo que necesitas para empezar a desarrollar apps con IA Generativa GRATIS 🧠✨](#-capítulo-1-todo-lo-que-necesitas-para-empezar-a-desarrollar-apps-con-ia-generativa-gratis-)
- [📝 Capítulo 2: Introducción a la generación de texto con IA Generativa 📝🤖🪄✨ ](../text-generation/README.md)
- [👩🏼‍🏫 Capítulo 3: Prompt Engineering 🤖💬 ](../prompt-engineering/README.md)
- [💬 Capítulo 4: Crea un chat con IA Generativa 🤖💬 ](../chat/README.md)
- [🔍 Capítulo 5: IA Generativa con RAG 🔍📥 ](../rag/README.md)
- [🖼️ Capítulo 6: Imágenes y la IA Generativa](../images/README.md)
- [🔊 Capítulo 7: Audio y la IA Generativa (Parte 1) 🎵🤖](../audio/README.md)
- [🔊 Capítulo 8: Audio y la IA Generativa (Parte 2 · Vídeo 2) 🎵🤖](../audio/avanzado/README.md)


## 💡 Capítulo 1: Todo lo que necesitas para empezar a desarrollar apps con IA Generativa GRATIS  🧠✨

Este README contiene todo lo explicado en mi primer vídeo de esta serie, al que puedes acceder desde aquí:

[![Herramientas GRATIS para empezar a desarrollar con IA Generativa](https://github.com/user-attachments/assets/b1748e33-0c8b-4db5-adba-32887bd54ffc)](https://youtu.be/n28h_yXPeMg)

## ¿Qué es IA generativa?

La IA generativa es un tipo de inteligencia artificial que puede crear contenido nuevo y original, como texto, imágenes, música y más. Utiliza algoritmos avanzados y modelos de aprendizaje profundo para generar resultados creativos y únicos.

## ¿Qué puedes hacer con IA generativa?

- ✏️ Generar texto: Puedes crear artículos, historias, poemas y más.
- 🌅 Crear imágenes: Puedes generar imágenes, modificarlas, etcétera.
- 🎶 Componer música: Puedes crear melodías y composiciones musicales utilizando IA generativa.
- 📋 Automatizar tareas: Puedes utilizar IA generativa para automatizar tareas repetitivas y mejorar la eficiencia en el trabajo.
- 🤖 Crear chatbots: Puedes desarrollar chatbots inteligentes que interactúan con los usuarios de manera natural.
- 👩🏼‍💻 Generar código: Puedes utilizar IA generativa para escribir y depurar código, lo que puede acelerar el proceso de desarrollo.
- 💡 Mejorar la creatividad: Puedes utilizar IA generativa como una herramienta para inspirarte y mejorar tu creatividad en diferentes campos.

Y estos son solo algunos ejemplos. Pero lo importante aquí es que entiendas que la IA Generativa tiene como principal objetivo crear.

Vale, ¿y cómo empiezo con todo esto? La IA Generativa utiliza lo que se conocen modelos que están entrenados, mejor o peor, para saber crear todo esto. Hay de diferentes tipos, tamaños y proveedores. Así que vamos a empezar por ver cómo puedo montarme un entorno donde pueda probar estos modelos para en posteriores vídeos elegir unos u otros dependiendo de lo que necesite.

## ¿Qué necesitas para empezar?

Lo primero que necesitas es un entorno de desarrollo y lo más importante de todo es que necesitas "algo" que pueda ejecutar los modelos de IA Generativa. Aquí 👇🏻 te dejo algunas opciones:

- Ollama: Ollama es una herramienta de código abierto que te permite ejecutar modelos de IA generativa en tu máquina local. Puedes instalarla fácilmente y empezar a usarla con solo unos pocos comandos. [Ollama](https://ollama.com/)
- Docker Model Runner: Relativamente nuevo y no está soportado todavía en todos los sistemas operativos o arquitecturas pero si eres un desarrollador que trabaja con contenedores, puede ser una opción interesante para explorar. [Docker Model Runner](https://www.docker.com/)
- GitHub Models: esta última opción, también gratuita, te permite poder acceder a una variedad de modelos de IA generativa que puedes utilizar directamente en tus proyectos en fase de desarrollo y no necesitas instalar nada adicional. [GitHub Models](https://github.com/)

### Ollama

Puedes instalarlo localmente, por ejemplo en tu Mac a través de Homebrew:

```bash
brew install ollama
```

O descargandote los ejecutables directamente desde su [página de descargas](https://ollama.com/download).

También puedes ejecutarlo dentro de un Dev Container, lo cual te evita tener que instalarlo directamente en tu máquina local. Sin embargo, debes tener en cuenta de que para la mayoría de modelos que es humanamente posible ejecutarlos en una máquina local, vas a necesitar reservar unos 16gb, como poco, de memoria RAM para que pueda ejecutar los modelos. Si quieres probarlo, este repositorio tiene todo lo que necesitas para tenerlo funcionando si abres el mismo dentro de un contenedor.

Si estás en local, una vez que ya lo tengas instalado, necesitas primeramente arrancar ollama:

```bash
ollama serve
```

Si estás dentro de un dev container, no es necesario que lo hagas, ya que el contenedor ya lo tiene arrancado.

Con esto tienes arrancada la herramienta que va a permitirte ejecutar los modelos de IA generativa en tu máquina local. Pero por ahora no tienes ningún modelo descargado que poder ejecutar. Para ello, muy al estilo Docker, puedes descargar modelos usando `ollama pull` y ejecutarlos con `ollama run`. Ok, pero qué modelos puedo descargar? Puedes ver una lista de los modelos disponibles ejecutando el siguiente comando:

```bash
ollama list
```

y descargar alguno de los modelos, por ejemplo el de Mistral (no te preocupes, ya veremos más adelante qué modelos son los que vas a ir necesitando)

```bash
ollama pull mistral-nemo
```

Para ver cuántos modelos tienes descargados, puedes ejecutar el siguiente comando:

```bash
ollama list
```

Ok, ¿y ahora qué hago con esto? Puedes ejecutar este modelo en concreto:

```bash
ollama run mistral-nemo "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

O incluso lo puedes ejecutar para que puedas llamarlo de forma programática, a través de un API REST:

```bash
ollama run mistral-nemo
```

Para saber qué modelos tienes ejecutandose, puedes lanzar el siguiente comando:

```bash
ollama ps
```

Y a partir de este momento también puedes hacer peticiones a través de un cliente HTTP, como Postman o Insomnia, o incluso desde tu propio código. 

```bash
curl http://localhost:11434/api/generate \
-d '{ "model": "mistral-nemo", "stream": false, "prompt":"Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"}' \
| jq .response
```

La lista de modelos disponibles para Ollama la puedes encontrar aquí: https://ollama.com/library

Si quieres probar otros la forma es la misma:

```bash
ollama run gemma3 "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

O incluso Deepseek-r1 que está ahora muy de moda:

```bash
ollama run deepseek-r1 "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

O includo de la gama Phi:

```bash
ollama run phi4-mini "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

Al igual que en Docker, no hace falta hacer primeramente un `pull` del modelo, sino que puedes ejecutarlo directamente y si no tienes el modelo en local se encargará de descargarlo.

Y también puedes eliminar cualquiera de los modelos descargados usando el mismo estilo:

```bash
ollama rm mistral
```

#### Ollama en local y el entorno de desarrollo dentro del Dev Container

```bash
curl http://localhost:11434/api/generate \
-d '{ "model": "mistral-nemo", "stream": false, "prompt":"Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"}' \
| jq .response
```

Ollama escucha por defecto por el puerto 11434. Si quieres llamar a Ollama que está fuera de tu Dev Container deberías de usar `http://host.docker.internal:11434/api/generate`Hará que hablemos con el Ollama que tenemos en nuestro host.

```bash
curl http://host.docker.internal:11434/api/generate \
-d '{ "model": "mistral-nemo", "stream": false, "prompt":"Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"}' \
| jq .response
```

También puedo cambiar el host del CLI de Ollama de la siguiente forma:

```bash
export OLLAMA_HOST=http://host.docker.internal:11434
```

y ahora desde dentro del Dev Container llamar al Ollama de fuera. Voy a borrar el modelo que descargué dentro del Dev Container, para que no haya dudas:

```bash
ollama rm mistral-nemo
```

y ahora intento ejecutar este modelo que tengo el host:

```bash
OLLAMA_HOST=http://host.docker.internal:11434 ollama run mistral-nemo "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

O cualquier otro:

```bash
OLLAMA_HOST=http://host.docker.internal:11434 ollama run phi4-mini "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

### Docker Model Runner

Hace apenas unos días, Docker anunció [Docker Model Runner](https://docs.docker.com/desktop/features/model-runner/). Esta otra opción está todavía en fase beta y no está soportada en todos los sistemas operativos o arquitecturas. Pero lo único que debes hacer en este caso, si tienes instalado Docker Desktop es tenerlo actualizado, al menos a la versión 4.40 o superior.

Este funciona de una forma similar a Ollama. Primero debes verificar que este lo tienes funcionando con tu instalación de Docker Desktop:

```bash
docker model status
```
y debería de devolverte: `Docker Model Runner is running`, y puedes hacer lo mismo que hemos visto hasta ahora:

Descargarte modelos (para ello puedes ver [los modelos disponibles a día de hoy en Docker Hub](https://hub.docker.com/u/ai)):

```bash
docker model pull ai/mistral-nemo
```

Ejecutarlos:

```bash
docker model run ai/mistral-nemo "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

u otros:

```bash
docker model run ai/phi4 "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

Y dentro del Dev Container podemos invocarlo usando cURL:

```bash
curl http://model-runner.docker.internal/engines/llama.cpp/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "ai/mistral-nemo",
        "prompt": "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa",
        "temperature": 0.7
    }' \
    | jq .choices[0].text
```

El "problema" de estos dos primeros es que necesitas hardware, o arquitecturas, suficiente para poder ejecutar los modelos en tu local y que esto no sea un sufrimiento. Por ejemplo, en el repo de GitHub de ollama se indica lo siguiente:

> [Note]
>You should have at least 8 GB of RAM available to run the 7B models, 16 GB to run the 13B models, and 32 GB to run the 33B models.

Y como te puedes imaginar, no todo el mundo tiene maquinones para poder ejecutar esto.

### GitHub Models

La tercera opción que puedes utilizar, si las anteriores no son posibles para ti es Github Models. El cual es un marketplace de modelos de IA que puedes utilizar en fase de desarrollo de forma gratuita. Para poder utilizarlo solo necesitas tener una cuenta de GitHub y generar un Personal Access Token que nisiquiera necesita tener ningún scope.

```bash
GITHUB_TOKEN=github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

y ya solo con esto puedes hacer llamadas a los diferentes modelos que hay en el catalogo de GitHub Models:

```bash
curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -d '{
        "messages": [           
            {
                "role": "user",
                "content": "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
            }
        ],       
        "model": "Mistral-Nemo"
    }' \
    | jq -r .choices[0].message.content
```

Y si queremos otro modelo la llamada es la misma, solo cambia el valor de `model`:

```bash
curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -d '{
        "messages": [           
            {
                "role": "user",
                "content": "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
            }
        ],        
        "model": "DeepSeek-R1"
    }' \
    | jq -r .choices[0].message.content
```

```bash
curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -d '{
        "messages": [           
            {
                "role": "user",
                "content": "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
            }
        ],        
        "model": "Phi-4"
    }' \
    | jq -r .choices[0].message.content
```

### AI Toolkit for Visual Studio

Y ya para terminar, si vas a utilizar Visual Studio Code como parte de tu entorno de desarrollo tienes una extensión disponible muy interesante que se llama AI Toolkit for Visual Studio, la cual te va a permitir interactuar de una forma bastante sencilla con los modelos tanto de Ollama como de Github Models (además de otras opciones que no hemos visto aquí). Esta extensión forma parte de este DevContainer.

# Cap.1 · Intro y setup: empieza GRATIS con IA Generativa

Guía mínima del vídeo 1: tres caminos rápidos para probar modelos de IA Generativa sin gastar dinero ni complicarte. Elige el que mejor te encaje y pasa al siguiente capítulo cuando lo tengas listo.

[![Herramientas GRATIS para empezar a desarrollar con IA Generativa](https://github.com/user-attachments/assets/b1748e33-0c8b-4db5-adba-32887bd54ffc)](https://youtu.be/n28h_yXPeMg)

## Qué vas a conseguir

- Probar modelos en local (Ollama) o vía Docker Model Runner.
- Alternativa sin instalación: GitHub Models vía API con un token gratuito.
- Un comando de ejemplo para validar que todo responde.

## Requisitos rápidos

- macOS/Windows/Linux y terminal.
- VS Code recomendado (Dev Containers opcional).
- Si ejecutas modelos en local: 8–16 GB RAM según el modelo.

---

## Opción A: Ollama (local)

1) Instala y arranca Ollama

```bash
brew install ollama
ollama serve
```

2) Descarga y ejecuta un modelo

```bash
ollama pull mistral-nemo
ollama run mistral-nemo "Mejora este título para un vídeo de YouTube con emojis: Hoy empiezo con IA Generativa"
```

3) Llama por HTTP (opcional)

```bash
curl http://localhost:11434/api/generate \
    -d '{"model":"mistral-nemo","stream":false,"prompt":"Hola IA 👋🏻"}' \
    | jq .response
```

Sugerencia Dev Container: si Ollama corre fuera del contenedor, usa `OLLAMA_HOST=http://host.docker.internal:11434`.

---

## Opción B: Docker Model Runner

1) Requisitos: Docker Desktop >= 4.40

```bash
docker model status
```

2) Pull y run de un modelo

```bash
docker model pull ai/mistral-nemo
docker model run ai/mistral-nemo "Hola IA 👋🏻"
```

3) Endpoint HTTP (opcional)

```bash
curl http://model-runner.docker.internal/engines/llama.cpp/v1/completions \
    -H "Content-Type: application/json" \
    -d '{"model":"ai/mistral-nemo","prompt":"Hola IA 👋🏻"}' \
    | jq .choices[0].text
```

---

## Opción C: GitHub Models (nube, gratis en dev)

1) Genera un GitHub Personal Access Token (sin scopes) y expórtalo como variable

```bash
export GITHUB_TOKEN=github_pat_xxx
```

2) Llama al endpoint de chat completions

```bash
curl -X POST "https://models.inference.ai.azure.com/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -d '{
        "messages": [{"role":"user","content":"Hola IA 👋🏻"}],
        "model": "Mistral-Nemo"
    }' | jq -r .choices[0].message.content
```

Importante: no compartas tu token ni lo subas al repositorio.

---

## ¿Y ahora qué?

- Si ya te responde algún modelo, continúa con los capítulos del repo:
    - [Cap.2 · Generación de texto](../text-generation/README.md)
    - [Cap.3 · Prompt Engineering](../prompt-engineering/README.md)
    - [Cap.4 · Chat con IA](../chat/README.md)
    - [Cap.5 · RAG](../rag/README.md)
    - [Cap.6 · Imágenes](../images/README.md)
    - [Cap.7 · Audio (básico)](../audio/README.md)
    - [Cap.8 · Audio (avanzado)](../audio/avanzado/README.md)

Si algo falla, abre un issue con el error exacto y tu sistema operativo; así puedo ayudarte más rápido.
