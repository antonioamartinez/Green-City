#!/usr/bin/env python
"""
Tile a large GeoTIFF (e.g. Pasadena_Whole_Map.tif, 95 GB) into
manageable 4096 px squares without loading the whole raster into RAM.

Usage
-----
python 00_tile_mosaic.py \
       --mosaic Pasadena_Whole_Map.tif \
       --out_dir tile_cache \
       --tile_size 4096
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path

import rasterio
from rasterio.windows import Window
from tqdm import tqdm


def tile_raster(mosaic_path: str, out_dir: str, tile_size: int) -> None:
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    with rasterio.open(mosaic_path) as src:
        meta_template = src.meta.copy()

        # Iterate over the mosaic by window
        for i in tqdm(range(0, src.width, tile_size), desc="Columns"):
            for j in range(0, src.height, tile_size):
                w = min(tile_size, src.width - i)
                h = min(tile_size, src.height - j)

                window = Window(i, j, w, h)
                transform = src.window_transform(window)
                tile_data = src.read(window=window)

                meta = meta_template.copy()
                meta.update({"height": h, "width": w, "transform": transform})

                out_name = f"tile_{i}_{j}.tif"
                out_path = Path(out_dir) / out_name
                with rasterio.open(out_path, "w", **meta) as dst:
                    dst.write(tile_data)

    print(f"[OK] Tiles saved in {out_dir}")


def main() -> None:
    p = argparse.ArgumentParser(description="Tile a large GeoTIFF into squares")
    p.add_argument("--mosaic", required=True, help="Path to Pasadena_Whole_Map.tif")
    p.add_argument("--out_dir", required=True, help="Destination folder for tiles")
    p.add_argument("--tile_size", type=int, default=4096, help="Tile edge in pixels")
    args = p.parse_args()

    tile_raster(args.mosaic, args.out_dir, args.tile_size)


if __name__ == "__main__":
    main()
