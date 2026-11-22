#!/usr/bin/env python3
"""
Convert predictions_bboxes.geojson → DeepForest CSV
(image_path,xmin,ymin,xmax,ymax,label), with pixel boxes clamped to each tile.
"""

import argparse
import pathlib
import geopandas as gpd
import rasterio
import pandas as pd
import numpy as np


def main():
    p = argparse.ArgumentParser(
        description="GeoJSON bboxes → DeepForest annotations CSV, in pixels and clamped"
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
    # 3) For each polygon, find its tile and convert its own bounds to pixel coords
    for geom in gdf.geometry:
        cx, cy = geom.centroid.coords[0]
        gminx, gminy, gmaxx, gmaxy = geom.bounds
        # find which tile contains the centroid
        for tile in tiles:
            minx, miny, maxx, maxy = tile["bounds"]
            if minx <= cx <= maxx and miny <= cy <= maxy:
                t = tile["transform"]
                # four corners of the polygon's bbox in pixel space
                corners = [
                    (~t) * (gminx, gminy),
                    (~t) * (gminx, gmaxy),
                    (~t) * (gmaxx, gminy),
                    (~t) * (gmaxx, gmaxy),
                ]
                xs = [c for c, r in corners]
                ys = [r for c, r in corners]

                # DeepForest expects pixel coordinates (pascal_voc), clamped to the tile
                w, h = tile["width"], tile["height"]
                xmin_px = float(np.clip(min(xs), 0, w))
                xmax_px = float(np.clip(max(xs), 0, w))
                ymin_px = float(np.clip(min(ys), 0, h))
                ymax_px = float(np.clip(max(ys), 0, h))

                # Skip degenerate or empty boxes
                if xmax_px <= xmin_px or ymax_px <= ymin_px:
                    break  # drop this polygon entirely

                records.append(
                    {
                        # relative to --tile_dir, which is passed as root_dir when training
                        "image_path": pathlib.Path(tile["path"]).name,
                        "xmin": xmin_px,
                        "ymin": ymin_px,
                        "xmax": xmax_px,
                        "ymax": ymax_px,
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
