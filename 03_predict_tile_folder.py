#!/usr/bin/env python
"""
03_predict_tile_folder_override_cap.py
--------------------------------------

Batch inference over a folder of TIFF tiles with increased detections per tile,
plus outputs for manual QGIS annotation (GeoJSON, Shapefile, GeoPackage, CSV + WKT),
all written into ./runs/run_<timestamp>/…
"""

from __future__ import annotations
import argparse
import glob
import os
import sys
import warnings
import json
import datetime
from typing import List, Optional

import geopandas as gpd
import pandas as pd
import rasterio
import torch
from shapely.geometry import box

from deepforest import main as df  # alias to avoid name clash with CLI main()


def predict_single_tile(
    model: df.deepforest,
    tif_path: str,
    patch_size: int,
    patch_overlap: float,
    iou_threshold: float = 0.5,
) -> Optional[pd.DataFrame]:
    df_pred = model.predict_tile(
        tif_path,
        patch_size=patch_size,
        patch_overlap=patch_overlap,
        iou_threshold=iou_threshold,
        return_plot=False,
    )
    if df_pred is not None and not df_pred.empty:
        df_pred["image_path"] = tif_path
        return df_pred
    return None


def pixel_df_to_geo(df_all: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Convert a DataFrame of pixel-space boxes (xmin, ymin, xmax, ymax)
    into a GeoDataFrame of Polygons in the raster's native CRS.
    """
    records: List[dict] = []
    crs = None
    for tif, group in df_all.groupby("image_path"):
        with rasterio.open(tif) as src:
            tfm, crs = src.transform, src.crs
            for _, r in group.iterrows():
                minx, miny = tfm * (r.xmin, r.ymin)
                maxx, maxy = tfm * (r.xmax, r.ymax)
                records.append(
                    {
                        "image_path": r.image_path,
                        "xmin": r.xmin,
                        "ymin": r.ymin,
                        "xmax": r.xmax,
                        "ymax": r.ymax,
                        "score": r.score,
                        "geometry": box(minx, miny, maxx, maxy),
                    }
                )
    return gpd.GeoDataFrame(records, geometry="geometry", crs=crs)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run DeepForest canopy detection on a folder of tiles "
        "and produce QGIS-annotatable outputs in ./runs/run_<timestamp>/"
    )
    mgroup = parser.add_mutually_exclusive_group(required=True)
    mgroup.add_argument("--weights", help="Path to fine-tuned .pth checkpoint")
    mgroup.add_argument(
        "--use_release",
        action="store_true",
        help="Use the official DeepForest release weights",
    )
    parser.add_argument("--tile_dir", required=True, help="Folder of .tif tiles")
    parser.add_argument(
        "--patch_size",
        type=int,
        default=600,
        help="Size of square patches for tiled inference",
    )
    parser.add_argument(
        "--overlap", type=float, default=0.5, help="Fractional overlap between patches"
    )
    parser.add_argument(
        "--nms_thresh",
        type=float,
        default=0.5,
        help="IoU threshold for Non-Maximum Suppression",
    )
    parser.add_argument(
        "--score_thresh",
        type=float,
        default=0.2,
        help="Confidence score threshold for RetinaNet",
    )
    parser.add_argument(
        "--max_detections",
        type=int,
        default=1000,
        help="Max detections per tile (override default 300)",
    )
    parser.add_argument(
        "--extra_crs",
        default="4326",
        help="Extra CRS code(s), comma-separated, to reproject output",
    )
    args = parser.parse_args()

    # 1) Ensure top-level "runs" folder exists
    base_runs = "runs"
    os.makedirs(base_runs, exist_ok=True)

    # 2) Create a unique run folder with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder = os.path.join(base_runs, f"run_{timestamp}")
    os.makedirs(run_folder)
    print(f"[INFO] Run folder → {run_folder}")

    # 3) Save hyperparameters for this run
    params = {
        "weights": args.weights or None,
        "use_release": args.use_release,
        "tile_dir": args.tile_dir,
        "patch_size": args.patch_size,
        "patch_overlap": args.overlap,
        "nms_thresh": args.nms_thresh,
        "score_thresh": args.score_thresh,
        "max_detections": args.max_detections,
        "extra_crs": args.extra_crs,
        "run_timestamp": timestamp,
    }
    with open(os.path.join(run_folder, "params.json"), "w") as f:
        json.dump(params, f, indent=2)
    print(f"[OK] Hyperparameters → params.json")

    # Load DeepForest model
    model = df.deepforest()
    if args.use_release:
        model.load_model("weecology/deepforest-tree")
    else:
        if not os.path.exists(args.weights):
            sys.exit(f"[ERROR] Weights not found: {args.weights}")
        state = torch.load(args.weights, map_location="cpu")
        model.model.load_state_dict(state)

    # Override thresholds and detection cap
    model.config["nms_thresh"] = args.nms_thresh
    model.config["retinanet"]["score_thresh"] = args.score_thresh
    model.model.detections_per_img = args.max_detections

    model.eval()
    torch.set_grad_enabled(False)

    # Gather tiles
    tiles = sorted(glob.glob(os.path.join(args.tile_dir, "*.tif")))
    if not tiles:
        sys.exit(f"[ERROR] No TIFFs found in {args.tile_dir}")

    # Run predictions
    dfs: List[pd.DataFrame] = []
    for tif in tiles:
        print(f"Predicting {os.path.basename(tif)} …")
        preds = predict_single_tile(
            model,
            tif,
            patch_size=args.patch_size,
            patch_overlap=args.overlap,
            iou_threshold=args.nms_thresh,
        )
        if preds is not None:
            dfs.append(preds)

    if not dfs:
        warnings.warn("No detections returned.")
        return

    # Merge and convert to GeoDataFrame
    gdf = pixel_df_to_geo(pd.concat(dfs, ignore_index=True))

    # Add fields for manual review
    gdf["reviewed"] = False
    gdf["keep"] = None

    # Write outputs inside run_folder
    geojson_p = os.path.join(run_folder, "predictions.geojson")
    shp_p = os.path.join(run_folder, "predictions.shp")
    gpkg_p = os.path.join(run_folder, "predictions.gpkg")
    csv_p = os.path.join(run_folder, "predictions.csv")

    gdf.to_file(geojson_p, driver="GeoJSON")
    print(f"[OK] GeoJSON → {geojson_p}")

    gdf.to_file(shp_p, driver="ESRI Shapefile")
    print(f"[OK] Shapefile → {shp_p}")

    layer = os.path.splitext(os.path.basename(gpkg_p))[0]
    gdf.to_file(gpkg_p, driver="GPKG", layer=layer)
    print(f"[OK] GeoPackage → {gpkg_p}")

    df_csv = gdf.drop(columns="geometry").copy()
    df_csv["wkt"] = gdf.geometry.apply(lambda g: g.wkt)
    df_csv.to_csv(csv_p, index=False)
    print(f"[OK] CSV → {csv_p}")

    # Optional reprojections
    for code in args.extra_crs.split(","):
        try:
            epsg = int(code)
        except ValueError:
            continue
        outp = os.path.join(run_folder, f"predictions_{epsg}.geojson")
        gdf.to_crs(epsg=epsg).to_file(outp, driver="GeoJSON")
        print(f"[OK] Reprojected → {outp}")


if __name__ == "__main__":
    main()
