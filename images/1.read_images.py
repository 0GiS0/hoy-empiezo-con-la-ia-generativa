import os
import ollama

res = ollama.chat(
	model="llama3.2-vision",
	messages=[
		{
			'role': 'user',
			'content': 'Describe this image:',
			'images': ['images/examples/IMG_2377.png']
		}
	]
)

print(res['message']['content'])