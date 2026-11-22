#!/usr/bin/env python
"""
10_predict_canopy_unet.py

Map tree canopy over a folder of GeoTIFF tiles with the canopy U-Net.
For each tile it writes a canopy mask GeoTIFF (1 = canopy), and for the folder
a canopy_polygons.geojson and a canopy_cover.csv with the canopy share of each
tile's imaged (non-nodata, non-black) area. Tiles not at ~0.6 m are resampled
to 0.6 m for the model and the mask is written back on the tile's own grid.

Example:
    python 10_predict_canopy_unet.py --weights canopy_unet.pt \
        --tile_dir tiles --out_dir canopy_run
"""

import argparse
import csv
import os
from pathlib import Path

import cv2
import geopandas as gpd
import numpy as np
import rasterio
import torch
from rasterio.features import shapes
from shapely.geometry import shape

from canopy_unet import MODEL_RES_M, load_model, predict_prob


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--weights", default="canopy_unet.pt")
    ap.add_argument("--tile_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--threshold", type=float, help="override the threshold tuned at training")
    ap.add_argument("--min_area_m2", type=float, default=4.0, help="drop canopy polygons smaller than this")
    ap.add_argument("--no_tta", action="store_true", help="skip the 4-rotation averaging (4x faster)")
    args = ap.parse_args()

    torch.set_num_threads(os.cpu_count() or 1)
    model, threshold = load_model(args.weights)
    if args.threshold is not None:
        threshold = args.threshold
    out = Path(args.out_dir)
    (out / "masks").mkdir(parents=True, exist_ok=True)

    polys, rows, crs = [], [], None
    for tif in sorted(Path(args.tile_dir).glob("*.tif")):
        with rasterio.open(tif) as r:
            rgb = r.read([1, 2, 3]).transpose(1, 2, 0)
            # pixels outside the imagery (nodata, or black mosaic padding) are not counted
            valid = (r.dataset_mask() > 0) & (rgb.max(-1) > 0)
            prof, tr, crs = r.profile, r.transform, r.crs
            if crs is None or not crs.is_projected:
                raise SystemExit(f"{tif.name}: needs a projected CRS in metres or feet; reproject it first")
            res_m = abs(tr.a) * crs.linear_units_factor[1]
        H, W = rgb.shape[:2]
        scale = res_m / MODEL_RES_M
        if abs(scale - 1) > 0.05:
            small = cv2.resize(rgb, (max(1, round(W * scale)), max(1, round(H * scale))), interpolation=cv2.INTER_AREA)
            prob = cv2.resize(predict_prob(model, small, tta=not args.no_tta), (W, H), interpolation=cv2.INTER_LINEAR)
        else:
            prob = predict_prob(model, rgb, tta=not args.no_tta)
        mask = ((prob > threshold) & valid).astype(np.uint8)
        cover = 100 * mask.sum() / valid.sum() if valid.any() else float("nan")

        prof.update(count=1, dtype="uint8", nodata=None, compress="deflate")
        with rasterio.open(out / "masks" / tif.name, "w", **prof) as dst:
            dst.write(mask, 1)
        for geom, _ in shapes(mask, mask=mask.astype(bool), transform=tr):
            polys.append({"tile": tif.stem, "geometry": shape(geom)})
        rows.append({"tile": tif.stem, "canopy_cover_pct": round(cover, 2)})
        print(f"{tif.name}: canopy {cover:.1f}% of imaged area", flush=True)

    gdf = gpd.GeoDataFrame({"tile": [p["tile"] for p in polys]},
                           geometry=[p["geometry"] for p in polys], crs=crs)
    if len(gdf) and crs is not None and crs.is_projected:
        area_m2 = gdf.geometry.area * crs.linear_units_factor[1] ** 2
        gdf = gdf[area_m2 >= args.min_area_m2]
    gdf.to_file(out / "canopy_polygons.geojson", driver="GeoJSON")
    with open(out / "canopy_cover.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["tile", "canopy_cover_pct"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} masks, {len(gdf)} polygons to {out}")


if __name__ == "__main__":
    main()
