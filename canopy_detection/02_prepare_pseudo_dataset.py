#!/usr/bin/env python3
"""
Convert predictions_bboxes.geojson → DeepForest CSV
(image_path,xmin,ymin,xmax,ymax,label), with normalized + clamped boxes.
"""

import argparse
import pathlib
import geopandas as gpd
import rasterio
import pandas as pd
import numpy as np


def main():
    p = argparse.ArgumentParser(
        description="GeoJSON bboxes → DeepForest annotations CSV, normalized and clamped"
    )
    p.add_argument(
        "--geojson", required=True, help="Path to predictions_bboxes.geojson"
    )
    p.add_argument(
        "--tile_dir",
        required=True,
        help="Directory containing optimized_tiles/ (.tif files)",
    )
    p.add_argument(
        "--output_csv", required=True, help="Path for output annotations CSV"
    )
    p.add_argument("--label", default="Tree", help="Label for all bounding boxes")
    args = p.parse_args()

    # 1) Load predicted polygons
    gdf = gpd.read_file(args.geojson)

    # 2) Preload each tile’s bounds, transform, and dimensions
    tiles = []
    for tif in pathlib.Path(args.tile_dir).glob("*.tif"):
        with rasterio.open(tif) as src:
            tiles.append(
                {
                    "path": str(tif),
                    "bounds": src.bounds,  # (minx, miny, maxx, maxy)
                    "transform": src.transform,  # for world→pixel
                    "width": src.width,
                    "height": src.height,
                }
            )

    records = []
    # 3) For each polygon, find its tile, compute pixel bbox, normalize, clamp
    for geom in gdf.geometry:
        cx, cy = geom.centroid.coords[0]
        # find which tile contains the centroid
        for tile in tiles:
            minx, miny, maxx, maxy = tile["bounds"]
            if minx <= cx <= maxx and miny <= cy <= maxy:
                t = tile["transform"]
                # four corners in pixel space
                corners = [
                    (~t) * (minx, miny),
                    (~t) * (minx, maxy),
                    (~t) * (maxx, miny),
                    (~t) * (maxx, maxy),
                ]
                xs = [c for c, r in corners]
                ys = [r for c, r in corners]
                xmin_px, xmax_px = min(xs), max(xs)
                ymin_px, ymax_px = min(ys), max(ys)

                # Normalize
                w, h = tile["width"], tile["height"]
                xmin_n = xmin_px / w
                ymin_n = ymin_px / h
                xmax_n = xmax_px / w
                ymax_n = ymax_px / h

                # Clamp to [0,1]
                xmin_n = float(np.clip(xmin_n, 0.0, 1.0))
                ymin_n = float(np.clip(ymin_n, 0.0, 1.0))
                xmax_n = float(np.clip(xmax_n, 0.0, 1.0))
                ymax_n = float(np.clip(ymax_n, 0.0, 1.0))

                # Skip degenerate or empty boxes
                if xmax_n <= xmin_n or ymax_n <= ymin_n:
                    break  # drop this polygon entirely

                records.append(
                    {
                        "image_path": tile["path"],
                        "xmin": xmin_n,
                        "ymin": ymin_n,
                        "xmax": xmax_n,
                        "ymax": ymax_n,
                        "label": args.label,
                    }
                )
                break
        else:
            raise ValueError(f"Polygon at ({cx:.1f}, {cy:.1f}) not in any tile!")

    # 4) Write out the DeepForest-formatted CSV
    df = pd.DataFrame(records)
    df.to_csv(args.output_csv, index=False)
    print(f"Wrote {len(df)} valid annotations → {args.output_csv}")


if __name__ == "__main__":
    main()
