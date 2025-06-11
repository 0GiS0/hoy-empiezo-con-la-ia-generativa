import os
from PIL import Image
from rich.pretty import Pretty
from rich.console import Console

def show_and_remove_metadata_from_pngs(directory):
    console = Console()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        metadata = img.info
                        if metadata:
                            console.print(f"[bold yellow]Metadata de {file_path}:[/bold yellow]")
                            console.print(Pretty(metadata))
                            # Limpiar metadata solo si existe
                            data = list(img.getdata())
                            img_no_metadata = Image.new(img.mode, img.size)
                            img_no_metadata.putdata(data)
                            img_no_metadata.save(file_path)
                            console.print(f"[cyan]Metadata eliminada: {file_path}[/cyan]")
                        else:
                            console.print(f"[green]No hay metadata en {file_path}[/green]")
                except Exception as e:
                    console.print(f"[red]Error procesando {file_path}: {e}[/red]")

if __name__ == "__main__":
    images_dir = "/workspaces/hoy-empiezo-con-ia-generativa/images"
    show_and_remove_metadata_from_pngs(images_dir)
