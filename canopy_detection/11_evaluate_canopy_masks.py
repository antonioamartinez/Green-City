#!/usr/bin/env python
"""
11_evaluate_canopy_masks.py

Score predicted canopy masks (e.g. from 10_predict_canopy_unet.py) against
reference masks (e.g. from 08_lidar_canopy_labels.py) with the same file names.
Reports pixel precision, recall, F1 and IoU pooled over all tiles, and the mean
absolute error of per-tile canopy cover in percentage points.

Example:
    python 11_evaluate_canopy_masks.py --pred_dir canopy_run/masks \
        --ref_dir canopy_labels --list canopy_splits/test.txt
"""

import argparse
from pathlib import Path

import numpy as np
import rasterio


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred_dir", required=True)
    ap.add_argument("--ref_dir", required=True)
    ap.add_argument("--list", help="tile names to score, one per line; default all predicted tiles")
    args = ap.parse_args()

    names = ([l.strip() for l in open(args.list) if l.strip()] if args.list
             else sorted(p.stem for p in Path(args.pred_dir).glob("*.tif")))
    tp = fp = fn = 0
    cover_err = []
    for n in names:
        with rasterio.open(Path(args.pred_dir) / f"{n}.tif") as r:
            p = r.read(1) > 0
        with rasterio.open(Path(args.ref_dir) / f"{n}.tif") as r:
            g = r.read(1) > 0
        tp += int((p & g).sum())
        fp += int((p & ~g).sum())
        fn += int((~p & g).sum())
        cover_err.append(abs(p.mean() - g.mean()) * 100)
    P, R = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
    print(f"tiles {len(names)}  precision {P:.3f}  recall {R:.3f}  F1 {2 * P * R / max(P + R, 1e-9):.3f}  "
          f"IoU {tp / max(tp + fp + fn, 1):.3f}  canopy cover MAE {np.mean(cover_err):.1f} pp")


if __name__ == "__main__":
    main()
