#!/usr/bin/env python
"""
Compute precision/recall/F1 across multiple IoU thresholds.

Uses the memory-efficient routine from your earlier pipeline.
"""
from __future__ import annotations
import argparse
import geopandas as gpd
import pandas as pd
from evaluate_multiple_iou import evaluate_multiple_iou  # keep your original function


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--gt_geojson", required=True, help="Human-verified crowns")
    p.add_argument("--pred_geojson", required=True, help="Predictions from step 03")
    p.add_argument("--out_csv", required=True)
    args = p.parse_args()

    gt = gpd.read_file(args.gt_geojson)
    pred = gpd.read_file(args.pred_geojson).to_crs(gt.crs)

    df_metrics = evaluate_multiple_iou(gt, pred)
    df_metrics.to_csv(args.out_csv, index=False)

    print(df_metrics.to_string(index=False))
    print(f"mAP: {df_metrics.Precision.mean():.3f}")


if __name__ == "__main__":
    main()
