#!/usr/bin/env python
"""
Convert model-generated predictions (pseudo-labels) + optional hand labels
into a DeepForest training CSV.

DeepForest ≥1.5.x returns the column **scores** (plural), not *score*.
"""
from __future__ import annotations
import argparse, glob, os, sys, tempfile
import geopandas as gpd
import pandas as pd
import rasterio
from shapely.geometry import box


def write_csv(geojson: str, tiles_dir: str, out_csv: str, score_thresh: float) -> None:
    gdf = gpd.read_file(geojson)

    # Keep only high-confidence pseudo-labels if a scores column exists
    for col in ("scores", "score"):
        if col in gdf.columns:
            gdf = gdf[gdf[col] >= score_thresh]
            break

    tile_paths = glob.glob(os.path.join(tiles_dir, "*.tif"))
    if not tile_paths:
        sys.exit(f"No tiles found in {tiles_dir}")

    with rasterio.open(tile_paths[0]) as ref:
        tgt_crs = ref.crs

    gdf = gdf.to_crs(tgt_crs)

    rows: list[dict] = []
    for tif in tile_paths:
        with rasterio.open(tif) as src:
            tfm, bounds = src.transform, src.bounds
            tile_geom = box(*bounds)

            for geom in gdf[gdf.intersects(tile_geom)].geometry:
                geom = geom.intersection(tile_geom)
                if geom.is_empty:
                    continue
                minx, miny, maxx, maxy = geom.bounds
                xmin, ymin = ~tfm * (minx, maxy)
                xmax, ymax = ~tfm * (maxx, miny)
                rows.append(
                    dict(
                        image_path=os.path.abspath(tif),
                        xmin=xmin,
                        ymin=ymin,
                        xmax=xmax,
                        ymax=ymax,
                        label="Tree",
                    )
                )

    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"Wrote {len(rows)} boxes → {out_csv}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--pseudo_geojson",
        required=True,
        help="prediction_geojson.geojson from the previous run",
    )
    p.add_argument(
        "--tiles_dir",
        required=True,
        help="Folder with 4096-px TIFF tiles (tile_cache/)",
    )
    p.add_argument(
        "--out_csv", required=True, help="Destination CSV for DeepForest training"
    )
    p.add_argument(
        "--score_thresh",
        type=float,
        default=0.2,
        help="Drop pseudo-labels below this confidence",
    )
    p.add_argument(
        "--extra_geojson",
        action="append",
        default=[],
        help="Any hand-labeled GeoJSON files to merge in (repeatable)",
    )
    args = p.parse_args()

    # Merge pseudo-labels and any additional human labels
    merged = gpd.read_file(args.pseudo_geojson)
    for path in args.extra_geojson:
        merged = pd.concat([merged, gpd.read_file(path)], ignore_index=True)

    with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
        merged.to_file(tmp.name, driver="GeoJSON")
        write_csv(tmp.name, args.tiles_dir, args.out_csv, args.score_thresh)
    os.remove(tmp.name)


if __name__ == "__main__":
    main()
