# 🖼️ Image Processing Utility

A fast, parallelized image processing script for batch **resizing** and **center-cropping** images using Pillow and Python's multiprocessing. Includes a simple CLI to choose tasks and auto-organizes output folders with timestamps.

## ✅ Features

- Resize images to **1/3 original size** (simulate 1x digital zoom)
- Center-crop images with customizable ratios (`small`, `medium`, `large`)
- Automatically detects image folders and skips specified ones
- Uses **multiprocessing** for performance
- Displays progress with **Rich**
- Output saved in timestamped directories for traceability

## 📁 Folder Structure

- `data/original/` → Input folder for original images to resize
- `data/resized/1x - TIMESTAMP/` → Output of resized images
- `data/cropped/cropped - TIMESTAMP/` → Output of cropped images

> Subfolders named `small`, `medium`, or `large` in the resized folder are used for cropping based on defined ratios.

## 🛠️ Setup

### 1. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 2. Install Dependancies

`pip install -r requirements.txt`

## ▶️ Running the Script

`python main.py`

## ⚙️ Customization

- Modify `SCALE_FACTOR` to change resize scale
- Edit `CROP_RATIOS` to define new crop sizes
- Add folder names to `SKIP_FOLDERS` to exclude from processing

## 🧠 Notes

- Automatically handles EXIF rotation
- Supported formats: `.png, .jpg, .jpeg, .bmp, .tiff`
- Progress is shown in real-time using the Rich CLI

---

**Documentation last updated at: `Sat 7 Jun 11:25 PM`**
