#!/usr/bin/env python
"""
06_evaluate_distance.py
──────────────────────────────────────────────────────────────
Extended evaluation for tree-crown detection:

• classic IoU table (0.50 → 0.95)  – same as earlier pipeline
• coverage within one or many radii (metres or feet, CRS-units)
• mean / median miss-distance
• false-positive density (per km²)
• progress bars via tqdm

Usage
-----
python 06_evaluate_distance.py \
       --gt_geojson merged_gt.geojson \
       --pred_geojson pasadena_preds.geojson \
       --out_csv metrics_plus_distance.csv \
       --radius 3,4              # radii in CRS units
"""

from __future__ import annotations
import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from tqdm import tqdm


# ────────────────────────────────────────────────────────────
#  Stand-alone IoU helper (no external import needed)
def evaluate_multiple_iou(
    gt: gpd.GeoDataFrame,
    pred: gpd.GeoDataFrame,
    thresholds: np.ndarray | None = None,
) -> pd.DataFrame:
    if thresholds is None:
        thresholds = np.arange(0.50, 1.00, 0.05)

    gidx = gt.sindex
    gpolys = gt.geometry
    rows = []

    for thr in thresholds:
        tp = fp = 0
        matched = set()

        for _, prow in pred.iterrows():
            cand = list(gidx.intersection(prow.geometry.bounds))
            hit = False
            for gi in cand:
                if gi in matched:
                    continue
                inter = prow.geometry.intersection(gpolys.iloc[gi]).area
                union = prow.geometry.union(gpolys.iloc[gi]).area
                iou = inter / union if union else 0.0
                if iou >= thr:
                    tp += 1
                    matched.add(gi)
                    hit = True
                    break
            if not hit:
                fp += 1

        fn = len(gt) - len(matched)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0

        rows.append(
            dict(IoU=thr, TP=tp, FP=fp, FN=fn, Precision=prec, Recall=rec, F1=f1)
        )

    return pd.DataFrame(rows)


# ────────────────────────────────────────────────────────────


def coverage_at_distance(
    gt: gpd.GeoDataFrame,
    pred: gpd.GeoDataFrame,
    radii: list[float],
) -> pd.DataFrame:
    """Return coverage / FP density for every radius in `radii`."""
    pidx = pred.sindex
    pgeom = pred.geometry
    merged_gt = gt.geometry.union_all()  # efficient + no deprecation

    results = []

    for r in radii:
        hit_mask = np.zeros(len(gt), dtype=bool)
        miss_dist = []

        for geom in tqdm(
            gt.geometry, desc=f"Radius {r}", unit="pt", leave=True, dynamic_ncols=True
        ):
            cand = list(pidx.intersection(geom.buffer(r).bounds))
            min_d = None
            for j in cand:
                d = geom.distance(pgeom.iloc[j])
                if min_d is None or d < min_d:
                    min_d = d
                if d <= r:
                    hit_mask[len(miss_dist)] = True  # index by loop counter
                    break
            if not hit_mask[len(miss_dist)] and min_d is not None:
                miss_dist.append(min_d)

        hits = hit_mask.sum()
        fp = sum(pgeom.iloc[j].distance(merged_gt) > r for j in range(len(pred)))
        area = gt.to_crs(3857).total_bounds
        area_km2 = ((area[2] - area[0]) * (area[3] - area[1])) / 1e6

        results.append(
            dict(
                radius=r,
                gt=len(gt),
                hits=hits,
                coverage=hits / len(gt) if len(gt) else 0,
                fp=fp,
                fp_per_km2=fp / area_km2 if area_km2 else np.nan,
                mean_miss=np.mean(miss_dist) if miss_dist else np.nan,
                median_miss=np.median(miss_dist) if miss_dist else np.nan,
            )
        )
    return pd.DataFrame(results)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt_geojson", required=True)
    ap.add_argument("--pred_geojson", required=True)
    ap.add_argument("--out_csv", required=True)
    ap.add_argument(
        "--radius", default="3", help="comma-separated radii in CRS units (default 3)"
    )
    args = ap.parse_args()

    gt = gpd.read_file(args.gt_geojson)
    pred = gpd.read_file(args.pred_geojson).to_crs(gt.crs)

    iou_df = evaluate_multiple_iou(gt, pred)
    radii = [float(r.strip()) for r in args.radius.split(",") if r.strip()]
    cov_df = coverage_at_distance(gt, pred, radii)

    full = pd.concat([iou_df, cov_df], axis=1)
    full.to_csv(args.out_csv, index=False)

    print(full.to_string(index=False))
    print(f"\nmAP: {iou_df.Precision.mean():.3f}")
    for _, row in cov_df.iterrows():
        print(f"Coverage ≤{row.radius:g} m: {row.coverage:.2%}")


if __name__ == "__main__":
    main()
