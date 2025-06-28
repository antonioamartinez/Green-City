#!/usr/bin/env python
"""
03_predict_tile_folder.py
-------------------------

Batch inference over a folder of TIFF tiles (e.g. 4096 × 4096 px at 10 cm GSD).

DeepForest ≥ 1.5.2 notes
------------------------
* The release model is loaded with `load_model("weecology/deepforest-tree")`;
  `use_release()` is deprecated.
* Per-box confidence is filtered with `model.config["retinanet"]["score_thresh"]`.
* Non-max suppression between overlapping patches is set via
  `model.config["nms_thresh"]`.
* `predict_tile()` accepts ONLY `patch_size`, `patch_overlap`,
  and `iou_threshold` (plus `return_plot`).  Do **not** pass
  `nms_thresh` or `score_thresh` as function arguments.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
import warnings
from typing import List, Optional

import geopandas as gpd
import pandas as pd
import rasterio
import torch
from shapely.geometry import box

# ---- DeepForest -------------------------------------------------------------
from deepforest import main as df  # alias to avoid name clash with CLI main()


# -----------------------------------------------------------------------------


def predict_single_tile(
    model: df.deepforest,
    tif_path: str,
    patch_size: int,
    patch_overlap: float,
    iou_threshold: float = 0.5,  # Increased for thightly packed crowns
) -> Optional[pd.DataFrame]:
    """
    Run DeepForest on one tile and return its raw prediction DataFrame
    (pixel coordinates). Returns ``None`` if no crowns are detected.
    """
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
    Convert the concatenated pixel-space DataFrame to a GeoDataFrame in map
    coordinates (same CRS as the source tiles).
    """
    records: List[dict] = []
    for tif, group in df_all.groupby("image_path"):
        with rasterio.open(tif) as src:
            tfm, crs = src.transform, src.crs
            for _, r in group.iterrows():
                minx, miny = tfm * (r.xmin, r.ymin)
                maxx, maxy = tfm * (r.xmax, r.ymax)
                records.append({**r, "geometry": box(minx, miny, maxx, maxy)})
    return gpd.GeoDataFrame(records, geometry="geometry", crs=crs)


# -----------------------------------------------------------------------------


def main() -> None:
    # ---------- CLI ----------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Run DeepForest canopy detection on a folder of tiles"
    )
    mgroup = parser.add_mutually_exclusive_group(required=True)
    mgroup.add_argument("--weights", help="Path to a fine-tuned .pth checkpoint")
    mgroup.add_argument(
        "--use_release",
        action="store_true",
        help="Use the official DeepForest release weights",
    )

    parser.add_argument("--tile_dir", required=True, help="Folder of .tif tiles")
    parser.add_argument("--out", required=True, help="Output GeoJSON file")

    parser.add_argument(
        "--patch_size", type=int, default=800
    )  # 600-800 px is a good compromise for 10 cm GSD
    parser.add_argument("--overlap", type=float, default=0.25)
    parser.add_argument(
        "--nms_thresh", type=float, default=0.25
    )  # How aggressive Non-Max Suppression is lower is more aggressive
    parser.add_argument("--score_thresh", type=float, default=0.5)
    parser.add_argument(
        "--extra_crs",
        default="4326,2229",
        help="Comma-separated EPSG codes to write in addition to the native CRS",
    )
    args = parser.parse_args()

    # ---------- Load model ---------------------------------------------------
    model = df.deepforest()

    if args.use_release:
        model.load_model("weecology/deepforest-tree")
    else:
        if not os.path.exists(args.weights):
            sys.exit(f"[ERROR] Cannot find weights: {args.weights}")
        state_dict = torch.load(args.weights, map_location="cpu")
        model.model.load_state_dict(state_dict)

    # Set run-time thresholds in the config  (not in predict_tile call!)
    model.config["nms_thresh"] = args.nms_thresh
    model.config["retinanet"]["score_thresh"] = args.score_thresh

    model.eval()
    torch.set_grad_enabled(False)

    # ---------- Iterate over tiles ------------------------------------------
    tile_paths = sorted(glob.glob(os.path.join(args.tile_dir, "*.tif")))
    if not tile_paths:
        sys.exit(f"[ERROR] No .tif files found in {args.tile_dir}")

    dfs: List[pd.DataFrame] = []
    for tif in tile_paths:
        print(f"Predicting {os.path.basename(tif)}")
        preds = predict_single_tile(
            model,
            tif,
            patch_size=args.patch_size,
            patch_overlap=args.overlap,
        )
        if preds is not None:
            dfs.append(preds)

    if not dfs:
        warnings.warn("No crowns detected in any tile.")
        return

    # ---------- Save GeoJSON -------------------------------------------------
    gdf = pixel_df_to_geo(pd.concat(dfs, ignore_index=True))
    gdf.to_file(args.out, driver="GeoJSON")
    print(f"[OK] Wrote {len(gdf)} detections → {args.out}")

    if args.extra_crs:
        codes = [int(c.strip()) for c in args.extra_crs.split(",") if c.strip()]
        stem, ext = os.path.splitext(args.out)
        for code in codes:
            out_path = f"{stem}_{code}{ext}"
            gdf.to_crs(epsg=code).to_file(out_path, driver="GeoJSON")
            print(f"[OK] Re-projected to EPSG:{code} → {out_path}")


# -----------------------------------------------------------------------------


if __name__ == "__main__":
    main()
