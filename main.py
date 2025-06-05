import os
from PIL import Image, ImageOps
from multiprocessing import Pool, cpu_count
from rich.progress import Progress
from rich.console import Console
from datetime import datetime

BASE_INPUT_DIR = "data"
RESIZE_INPUT_DIR = BASE_INPUT_DIR
CROP_INPUT_DIR = os.path.join(BASE_INPUT_DIR, "1x")
SKIP_FOLDERS = {"20250211", "to_draw"}

SCALE_FACTOR = 1 / 3
CROP_RATIO = 0.68

console = Console()

def wrapper(args_process_fn_output_dir):
    args, process_fn, output_base_dir = args_process_fn_output_dir
    return process_task(args, output_base_dir, process_fn)

def get_timestamp():
    now = datetime.now()
    return now.strftime("%-d%b%I%M%p").replace("AM", "AM").replace("PM", "PM")

def find_images(base_dir, skip_folders):
    tasks = []
    for folder_name in os.listdir(base_dir):
        if folder_name in skip_folders:
            continue
        folder_path = os.path.join(base_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                full_path = os.path.join(folder_path, file_name)
                tasks.append((folder_name, file_name, full_path))
    return tasks

def resize_image(img):
    new_size = (int(img.width * SCALE_FACTOR), int(img.height * SCALE_FACTOR))
    return img.resize(new_size, Image.LANCZOS)

def crop_center(img):
    w, h = img.size
    crop_w, crop_h = int(w * CROP_RATIO), int(h * CROP_RATIO)
    left = (w - crop_w) // 2
    top = (h - crop_h) // 2
    return img.crop((left, top, left + crop_w, top + crop_h))

def process_task(args, output_base_dir, process_fn):
    folder_name, file_name, file_path = args
    try:
        with Image.open(file_path) as img:
            img = ImageOps.exif_transpose(img)
            processed_img = process_fn(img)

            out_dir = os.path.join(output_base_dir, folder_name)
            os.makedirs(out_dir, exist_ok=True)

            out_path = os.path.join(out_dir, file_name)
            processed_img.save(out_path)

        return True
    except Exception as e:
        return f"Error processing {file_path}: {e}"

def run_processing(image_tasks, process_fn, label):
    timestamp = get_timestamp()
    folder_prefix = "1x" if process_fn == resize_image else "cropped"
    output_base_dir = os.path.join(BASE_INPUT_DIR, f"{folder_prefix} - {timestamp}")

    with Progress() as progress:
        task = progress.add_task(f"[cyan]{label} images...", total=len(image_tasks))

        with Pool(processes=cpu_count()) as pool:
            wrapped_args = [(args, process_fn, output_base_dir) for args in image_tasks]
            for result in pool.imap_unordered(wrapper, wrapped_args):
                if isinstance(result, str):
                    console.print(f"[red]{result}")
                progress.update(task, advance=1)


    console.print(f"\n[green]Done. Total images processed: {len(image_tasks)}")
    console.print(f"[blue]Saved in: {output_base_dir}")

if __name__ == "__main__":
    console.print("\n[bold yellow]Choose an option:")
    console.print("[1] Resize to 1/3 size (3x digital zoom)")
    console.print("[2] Center crop to remove plate edges\n")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        tasks = find_images(RESIZE_INPUT_DIR, SKIP_FOLDERS)
        run_processing(tasks, resize_image, "Resizing")

    elif choice == "2":
        folders = sorted([f for f in os.listdir(BASE_INPUT_DIR) if f.startswith("1x") and os.path.isdir(os.path.join(BASE_INPUT_DIR, f))])

        if not folders:
            console.print("[red]No folders starting with '1x' found. Exiting.")
            exit(1)

        console.print("\n[bold yellow]Available '1x' folders:")
        for i, folder in enumerate(folders, 1):
            console.print(f"[{i}] {folder}")

        idx = input("\nEnter folder number to crop from: ").strip()

        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(folders):
            console.print("[red]Invalid selection. Exiting.")
            exit(1)

        selected_folder = folders[int(idx) - 1]
        CROP_INPUT_DIR = os.path.join(BASE_INPUT_DIR, selected_folder)

        tasks = find_images(CROP_INPUT_DIR, {"20250211"})
        run_processing(tasks, crop_center, "Cropping")
    else:
        console.print("[red]Invalid choice. Exiting.")