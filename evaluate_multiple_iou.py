# evaluate_multiple_iou.py
# ──────────────────────────────────────────────────────────────────────
"""
Fast IoU table between two GeoDataFrames
---------------------------------------

Usage
-----
from evaluate_multiple_iou import evaluate_multiple_iou

df = evaluate_multiple_iou(gt_gdf, pred_gdf)   # defaults to 0.50…0.95
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import geopandas as gpd


def evaluate_multiple_iou(
    gt: gpd.GeoDataFrame,
    pred: gpd.GeoDataFrame,
    thresholds: np.ndarray | None = None,
) -> pd.DataFrame:
    """
    Compute TP / FP / FN plus precision-recall-F1 for multiple IoU thresholds.

    Parameters
    ----------
    gt : GeoDataFrame
        Ground-truth geometries.
    pred : GeoDataFrame
        Predicted geometries (same CRS as `gt`).
    thresholds : array-like, optional
        IoU break-points (default = np.arange(0.50, 1.00, 0.05)).

    Returns
    -------
    pd.DataFrame
        One row per threshold with columns:
        IoU, TP, FP, FN, Precision, Recall, F1
    """
    if thresholds is None:
        thresholds = np.arange(0.50, 1.00, 0.05)

    gt_index = gt.sindex
    gt_polys = gt.geometry
    rows = []

    for t in thresholds:
        tp = fp = 0
        matched_gt = set()

        for _, prow in pred.iterrows():
            # candidate GT indices whose bounding box intersects
            cand = list(gt_index.intersection(prow.geometry.bounds))
            hit = False
            for gi in cand:
                if gi in matched_gt:
                    continue
                inter = prow.geometry.intersection(gt_polys.iloc[gi]).area
                union = prow.geometry.union(gt_polys.iloc[gi]).area
                iou = inter / union if union else 0.0
                if iou >= t:
                    tp += 1
                    matched_gt.add(gi)
                    hit = True
                    break
            if not hit:
                fp += 1

        fn = len(gt) - len(matched_gt)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0

        rows.append(dict(IoU=t, TP=tp, FP=fp, FN=fn, Precision=p, Recall=r, F1=f1))

    return pd.DataFrame(rows)


# ──────────────────────────────────────────────────────────────────────
