#!/usr/bin/env python3
"""
Convert a QGIS-edited Shapefile of tree crowns into a DeepForest-style CSV
(image_path,xmin,ymin,xmax,ymax,label) for training.
"""

import argparse
import os
import geopandas as gpd
import pandas as pd
import rasterio


def polygon_to_bbox_pixels(geom, transform):
    """
    Given a Shapely polygon in spatial coordinates and a rasterio transform,
    return (xmin, ymin, xmax, ymax) in pixel coordinates.
    """
    # get the four corner extremes of the geometry
    minx, miny, maxx, maxy = geom.bounds
    # map each corner into pixel space
    corners = [
        (~transform * (minx, miny)),
        (~transform * (minx, maxy)),
        (~transform * (maxx, miny)),
        (~transform * (maxx, maxy)),
    ]
    cols = [c for c, r in corners]
    rows = [r for c, r in corners]
    xmin_px, xmax_px = min(cols), max(cols)
    ymin_px, ymax_px = min(rows), max(rows)
    return xmin_px, ymin_px, xmax_px, ymax_px


def main():
    p = argparse.ArgumentParser(
        description="Build DeepForest annotations CSV from a Shapefile."
    )
    p.add_argument(
        "--shapefile",
        required=True,
        help="Path to edited Shapefile (must have 'image_path' & 'keep' fields)",
    )
    p.add_argument(
        "--output_csv",
        required=True,
        help="Where to write the DeepForest-style CSV",
    )
    p.add_argument(
        "--label",
        default="Tree",
        help="What label to assign to each bbox (default: 'Tree')",
    )
    args = p.parse_args()

    # 1) Load and filter
    gdf = gpd.read_file(args.shapefile)
    if "keep" in gdf.columns and gdf["keep"].any():
        gdf = gdf[gdf["keep"] == True]
    else:
        print("[WARN] No keep==True found; exporting *all* features.")

    records = []
    # 2) For each image_path, open its raster to get the transform
    for img_path, group in gdf.groupby("image_path"):
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Cannot find image: {img_path}")
        with rasterio.open(img_path) as src:
            transform = src.transform
            for _, row in group.iterrows():
                xmin, ymin, xmax, ymax = polygon_to_bbox_pixels(row.geometry, transform)
                records.append(
                    {
                        "image_path": img_path,
                        "xmin": xmin,
                        "ymin": ymin,
                        "xmax": xmax,
                        "ymax": ymax,
                        "label": args.label,
                    }
                )

    # 3) Write CSV
    df = pd.DataFrame(records)
    df.to_csv(args.output_csv, index=False)
    print(f"Wrote {len(df)} annotations → {args.output_csv}")


if __name__ == "__main__":
    main()
