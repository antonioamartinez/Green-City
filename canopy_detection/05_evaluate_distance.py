#!/usr/bin/env python
"""
05_evaluate_distance.py  –  bbox‐overlap + distance coverage with progress bars.

Counts a true positive whenever any ground‐truth bounding box overlaps
the predicted bounding box, regardless of IoU.

CLI example
-----------
python 05_evaluate_distance.py \
       --gt_geojson merged_gt.geojson \
       --pred_geojson pasadena_preds_2229.geojson \
       --out_csv metrics_plus_distance.csv \
       --radius 3,4 \
       --buffer 1.5
"""
from __future__ import annotations
import argparse
import geopandas as gpd
import numpy as np
import pandas as pd
from tqdm import tqdm


# ─────────────────── bbox‐overlap helper ────────────────────
def evaluate_bbox_overlap(gt: gpd.GeoDataFrame, pred: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Count a true positive whenever any ground-truth bbox overlaps
    the predicted bbox (spatial-index intersection), regardless of IoU.
    """
    # build spatial index on GT bounding boxes
    gidx = gt.sindex
    matched = set()
    tp = fp = 0

    # for each prediction, find any unmatched GT whose bbox overlaps
    for _, prow in pred.iterrows():
        cand = list(gidx.intersection(prow.geometry.bounds))
        hit = False
        for gi in cand:
            if gi in matched:
                continue
            # first unmatched candidate ⇒ true positive
            matched.add(gi)
            tp += 1
            hit = True
            break
        if not hit:
            fp += 1

    fn = len(gt) - len(matched)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    return pd.DataFrame(
        [
            {
                "TP": tp,
                "FP": fp,
                "FN": fn,
                "Precision": precision,
                "Recall": recall,
                "F1": f1,
            }
        ]
    )


# ───────────────── coverage at distance ────────────────────
def coverage_at_distance(
    gt: gpd.GeoDataFrame, pred: gpd.GeoDataFrame, radii: list[float]
) -> pd.DataFrame:
    pidx, pgeom = pred.sindex, pred.geometry
    merged_gt = gt.geometry.union_all()
    rows = []

    for r in radii:
        hit = np.zeros(len(gt), dtype=bool)
        miss_distances = []

        for i, g in enumerate(
            tqdm(gt.geometry, desc=f"GT ≤{r} m", unit="pt", leave=True)
        ):
            cand = list(pidx.intersection(g.buffer(r).bounds))
            dmin = min((g.distance(pgeom.iloc[j]) for j in cand), default=None)
            if dmin is not None and dmin <= r:
                hit[i] = True
            elif dmin is not None:
                miss_distances.append(dmin)

        fp = sum(
            pgeom.iloc[j].distance(merged_gt) > r
            for j in tqdm(range(len(pred)), desc=f"FP ≤{r} m", unit="pred", leave=True)
        )

        # compute area in km² using Web Mercator (EPSG:3857)
        xmin, ymin, xmax, ymax = gt.to_crs(3857).total_bounds
        area_km2 = ((xmax - xmin) * (ymax - ymin)) / 1e6

        rows.append(
            {
                "radius": r,
                "gt": len(gt),
                "hits": hit.sum(),
                "coverage": hit.mean(),
                "fp": fp,
                "fp_per_km2": fp / area_km2 if area_km2 else np.nan,
                "mean_miss": np.mean(miss_distances) if miss_distances else np.nan,
                "median_miss": np.median(miss_distances) if miss_distances else np.nan,
            }
        )

    return pd.DataFrame(rows)


# ────────────────────────── main ────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt_geojson", required=True, help="Ground-truth GeoJSON file")
    ap.add_argument("--pred_geojson", required=True, help="Predictions GeoJSON file")
    ap.add_argument("--out_csv", required=True, help="Output CSV for metrics")
    ap.add_argument(
        "--radius",
        default="3",
        help="Comma-separated list of radii (in CRS units, e.g. metres)",
    )
    ap.add_argument(
        "--buffer",
        type=float,
        default=4,
        help="If GT has Points, buffer radius (same units)",
    )
    args = ap.parse_args()

    # read files
    gt = gpd.read_file(args.gt_geojson)
    pred = gpd.read_file(args.pred_geojson).to_crs(gt.crs)

    # if GT are points, buffer them into small discs
    if gt.geom_type.unique().tolist() == ["Point"]:
        gt = gt.copy()
        gt["geometry"] = gt.geometry.buffer(args.buffer)

    # evaluate bbox-overlap metrics
    metrics_df = evaluate_bbox_overlap(gt, pred)

    # evaluate coverage at various distances
    radii = [float(r) for r in args.radius.split(",") if r.strip()]
    cov_df = coverage_at_distance(gt, pred, radii)

    # combine and save
    full = pd.concat([metrics_df, cov_df], axis=1)
    full.to_csv(args.out_csv, index=False)

    # print to console
    print(full.to_string(index=False))
    print()
    print(f"Precision: {metrics_df.Precision.iloc[0]:.3f}")
    print(f"Recall:    {metrics_df.Recall.iloc[0]:.3f}")
    print(f"F1 Score:  {metrics_df.F1.iloc[0]:.3f}")
    for _, row in cov_df.iterrows():
        print(f"Coverage ≤{row.radius:g} m: {row.coverage:.2%}")


if __name__ == "__main__":
    main()
