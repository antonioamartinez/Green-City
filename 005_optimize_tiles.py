import os
import numpy as np
import cv2
import rasterio
from rasterio.enums import Resampling
from rasterio.shutil import copy as rio_copy
from rasterio.io import MemoryFile

# ---------- CONFIGURATION ----------
input_folder = "tile_cache"
output_folder = "optimized_tile_cache"
os.makedirs(output_folder, exist_ok=True)


# ---------- WHITE BALANCE ----------
def white_balance(img):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    avg_a = np.average(lab[:, :, 1])
    avg_b = np.average(lab[:, :, 2])
    lab[:, :, 1] = lab[:, :, 1] - ((avg_a - 128) * (lab[:, :, 0] / 255.0) * 1.1)
    lab[:, :, 2] = lab[:, :, 2] - ((avg_b - 128) * (lab[:, :, 0] / 255.0) * 1.1)
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)


# ---------- CLAHE ENHANCEMENT ----------
def apply_clahe(img):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)


# ---------- PROCESS A TIF WITH METADATA ----------
def process_geotiff(image_path, output_path):
    with rasterio.open(image_path) as src:
        meta = src.meta.copy()
        img = src.read([1, 2, 3], out_dtype=np.uint8)  # Read RGB
        img = np.transpose(img, (1, 2, 0))  # To H x W x C format

        # Apply enhancements
        img_wb = white_balance(img)
        img_clahe = apply_clahe(img_wb)

        # Transpose back to C x H x W for rasterio
        optimized = np.transpose(img_clahe, (2, 0, 1))

        # Update meta to match processed data
        meta.update({"count": 3, "dtype": "uint8"})

        # Write GeoTIFF with preserved metadata
        output_file = os.path.join(output_path, os.path.basename(image_path))
        with rasterio.open(output_file, "w", **meta) as dst:
            dst.write(optimized)


# ---------- MAIN LOOP ----------
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".tif") or filename.lower().endswith(".tiff"):
        input_path = os.path.join(input_folder, filename)
        process_geotiff(input_path, output_folder)

print("✅ DeepForest-compatible optimized GeoTIFFs saved to:", output_folder)
