from PIL import Image

# Abre la imagen sin metadata
imagen_sin_metadata = Image.open('images/examples/IMG_2377_sin_metadata.png')

# Verifica la metadata
if not imagen_sin_metadata.info:
    print("La imagen no tiene metadata.")
else:
    print("La imagen tiene metadata:", imagen_sin_metadata.info)
