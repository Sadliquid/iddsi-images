import os
from PIL import Image, ImageOps
from multiprocessing import Pool, cpu_count
from rich.progress import Progress
from rich.console import Console
from datetime import datetime
from functools import partial

BASE_INPUT_DIR = "data"
RESIZE_INPUT_DIR = os.path.join(BASE_INPUT_DIR, "original")
CROP_PARENT_DIR = os.path.join(BASE_INPUT_DIR, "resized")
SKIP_FOLDERS = {"20250211", "to_draw"}

SCALE_FACTOR = 1 / 3

CROP_RATIOS = {
    "small": 0.75,
    "medium": 0.5,
    "large": 0.42
}

console = Console()

def wrapper(args_process_fn_output_dir):
    args, process_fn, output_base_dir = args_process_fn_output_dir
    return process_task(args, output_base_dir, process_fn)

def get_timestamp():
    now = datetime.now()
    return now.strftime("%-d%b%I%M%p").replace("AM", "AM").replace("PM", "PM")

def find_images(base_dir, skip_folders=None):
    tasks = []
    if skip_folders is None:
        skip_folders = set()

    for file_name in os.listdir(base_dir):
        full_path = os.path.join(base_dir, file_name)
        if os.path.isdir(full_path):
            if os.path.basename(full_path) in skip_folders:
                continue
            continue
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            tasks.append((os.path.basename(base_dir), file_name, full_path))

    return tasks

def resize_image(img):
    new_size = (int(img.width * SCALE_FACTOR), int(img.height * SCALE_FACTOR))
    return img.resize(new_size, Image.LANCZOS)

def crop_center(img, ratio):
    w, h = img.size
    crop_w, crop_h = int(w * ratio), int(h * ratio)
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

def run_processing(image_tasks, process_fn, label, output_base_dir):
    with Progress() as progress:
        task = progress.add_task(f"[cyan]{label} images...", total=len(image_tasks))

        with Pool(processes=cpu_count()) as pool:
            wrapped_args = [(args, process_fn, output_base_dir) for args in image_tasks]
            for result in pool.imap_unordered(wrapper, wrapped_args):
                if isinstance(result, str):
                    console.print(f"[red]{result}")
                progress.update(task, advance=1)

    console.print(f"\n[green]Done. Total images processed: {len(image_tasks)}")
    console.print(f"[blue]Saved to: {output_base_dir}")

if __name__ == "__main__":
    console.print("\n[bold yellow]Choose an option:")
    console.print("[1] Resize to 1/3 size (1x digital zoom)")
    console.print("[2] Center crop to remove plate edges\n")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        tasks = find_images(RESIZE_INPUT_DIR, SKIP_FOLDERS)
        output_base_dir = os.path.join(BASE_INPUT_DIR, "resized", f"1x - {get_timestamp()}")
        run_processing(tasks, resize_image, "Resizing", output_base_dir)

    elif choice == "2":
        folders = sorted([f for f in os.listdir(CROP_PARENT_DIR) if f.startswith("1x") and os.path.isdir(os.path.join(CROP_PARENT_DIR, f))])

        if not folders:
            console.print("[red]No valid resized folders available. Exiting console...")
            exit(1)

        console.print("\n[bold yellow]Available options:")
        for i, folder in enumerate(folders, 1):
            console.print(f"[{i}] {folder}")

        idx = input("\nEnter folder number to use for cropping: ").strip()

        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(folders):
            console.print("[red]Invalid selection. Exiting.")
            exit(1)

        selected_folder = folders[int(idx) - 1]
        selected_path = os.path.join(CROP_PARENT_DIR, selected_folder)

        timestamp = get_timestamp()
        final_output_dir = os.path.join(BASE_INPUT_DIR, "cropped", f"cropped - {timestamp}")

        os.makedirs(final_output_dir, exist_ok=True)

        total_images = 0

        for subfolder, ratio in CROP_RATIOS.items():
            sub_path = os.path.join(selected_path, subfolder)
            if not os.path.isdir(sub_path):
                console.print(f"[yellow]Skipping missing subfolder: {sub_path}")
                continue

            tasks = find_images(sub_path, SKIP_FOLDERS)
            if not tasks:
                continue

            crop_fn = partial(crop_center, ratio=ratio)

            run_processing(tasks, crop_fn, f"Cropping {subfolder}", final_output_dir)
            total_images += len(tasks)

        if total_images == 0:
            console.print("[red]No images to crop. Exiting console...")
        else:
            console.print(f"\n[green]Cropping completed. Output saved to: {final_output_dir}")
    else:
        console.print("[red]Invalid choice. Exiting.")