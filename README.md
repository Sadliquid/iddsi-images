# Image Resize Utility

This Python script resizes images that were taken with 3x digital zoom back to their original 1x size using the Pillow library. It's ideal for reversing digital zoom effects and restoring approximate original framing.

## Aim

- Batch resize images from 3x to 1x (scale down to 33.33%)
- Preserves original image format
- Simple and fast using Pillow and Python Multiprocessing

## Creating a Virtual Environment

`python -m venv venv`

```
source venv/bin/activate # On macOS/Linux
venv\Scripts\activate # On Windows
```

`pip install -r requirements.txt`

## Running the Script

`python main.py`