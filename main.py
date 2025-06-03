import os
from PIL import Image
from multiprocessing import Pool, cpu_count
from rich.progress import Progress, track
from rich.console import Console

DATA_DIR = "data"
OUTPUT_DIR = os.path.join("data", "1x")
SCALE_FACTOR = 1 / 3
SKIP_FOLDERS = {"1x", "20250211"}

console = Console()

def find_images():
    tasks = []
    for folder_name in os.listdir(DATA_DIR):
        if folder_name in SKIP_FOLDERS:
            continue
        folder_path = os.path.join(DATA_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                full_path = os.path.join(folder_path, file_name)
                tasks.append((folder_name, file_name, full_path))
    return tasks

def resize_task(args):
    folder_name, file_name, file_path = args
    try:
        with Image.open(file_path) as img:
            new_size = (int(img.width * SCALE_FACTOR), int(img.height * SCALE_FACTOR))
            resized_img = img.resize(new_size, Image.LANCZOS)

            out_dir = os.path.join(OUTPUT_DIR, folder_name)
            os.makedirs(out_dir, exist_ok=True)

            out_path = os.path.join(out_dir, file_name)
            resized_img.save(out_path)

        return True
    except Exception as e:
        return f"Error processing {file_path}: {e}"

if __name__ == "__main__":
    image_tasks = find_images()

    with Progress() as progress:
        task = progress.add_task("[cyan]Resizing images...", total=len(image_tasks))

        with Pool(processes=cpu_count()) as pool:
            for result in pool.imap_unordered(resize_task, image_tasks):
                if isinstance(result, str):
                    console.print(f"[red]{result}")
                progress.update(task, advance=1)

    console.print(f"\n[green]Done. Total images resized: {len(image_tasks)}")