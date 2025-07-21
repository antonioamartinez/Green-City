#!/usr/bin/env python
"""
06_coverage_tuning.py

Grid-search over DeepForest hyperparameters to maximize coverage% @ radius 12 m,
sweeping score_thresh, nms_thresh, and patch overlap.
"""
import argparse, os, glob, subprocess, tempfile
import pandas as pd
import geopandas as gpd
import rasterio
from shapely.geometry import box
from sklearn.model_selection import KFold, ParameterGrid


def get_tile_bounds(tile_paths):
    boxes, crs = [], None
    for tif in tile_paths:
        with rasterio.open(tif) as src:
            minx, miny, maxx, maxy = src.bounds
            boxes.append(box(minx, miny, maxx, maxy))
            crs = src.crs
    return gpd.GeoDataFrame(geometry=boxes, crs=crs)


def filter_gt(gt_full, test_tiles):
    tb = get_tile_bounds(test_tiles)
    joined = gpd.sjoin(gt_full, tb, how="inner", predicate="intersects")
    return gt_full.loc[joined.index.unique()]


def run_fold_eval(tmp_dir, gt_path, args, weights_flag):
    # 1) Predict
    pred_cmd = [
        "python",
        "03_predict_tile_folder.py",
        "--tile_dir",
        tmp_dir,
        "--patch_size",
        str(args.patch_size),
        "--overlap",
        str(args.overlap),
        "--nms_thresh",
        str(args.nms_thresh),
        "--score_thresh",
        str(args.score_thresh),
        "--max_detections",
        str(args.max_detections),
    ] + weights_flag
    subprocess.run(pred_cmd, check=True)

    # find latest run folder
    run_dirs = sorted(glob.glob("runs/run_*"), reverse=True)
    pred_geojson = os.path.join(run_dirs[0], "predictions.geojson")

    # 2) Evaluate
    out_csv = os.path.join(tmp_dir, "metrics.csv")
    eval_cmd = [
        "python",
        "06_evaluate_distance.py",
        "--gt_geojson",
        gt_path,
        "--pred_geojson",
        pred_geojson,
        "--out_csv",
        out_csv,
        "--radius",
        args.radius,
        "--buffer",
        str(args.buffer),
    ]
    subprocess.run(eval_cmd, check=True)

    # extract coverage at the target radius
    df = pd.read_csv(out_csv)
    cov = df.loc[df["radius"] == float(args.radius), "coverage"].iloc[0]
    return cov


def kfold_coverage(args, weights_flag):
    tiles = sorted(glob.glob(os.path.join(args.tile_dir, "*.tif")))
    gt_full = gpd.read_file(args.gt_geojson)
    kf = KFold(n_splits=args.k_folds, shuffle=True, random_state=42)

    covs = []
    for _, test_idx in kf.split(tiles):
        test_tiles = [tiles[i] for i in test_idx]
        with tempfile.TemporaryDirectory() as td:
            # link tiles
            for t in test_tiles:
                os.symlink(os.path.abspath(t), os.path.join(td, os.path.basename(t)))
            # filter GT
            gt_fold = filter_gt(gt_full, test_tiles)
            gt_path = os.path.join(td, "gt_fold.geojson")
            gt_fold.to_file(gt_path, driver="GeoJSON")

            covs.append(run_fold_eval(td, gt_path, args, weights_flag))
    return sum(covs) / len(covs)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tile_dir", required=True)
    p.add_argument("--gt_geojson", required=True)
    gp = p.add_mutually_exclusive_group(required=True)
    gp.add_argument("--weights")
    gp.add_argument("--use_release", action="store_true")
    p.add_argument("--k_folds", type=int, default=5)
    p.add_argument("--radius", default="12")
    p.add_argument("--buffer", type=float, default=12)
    p.add_argument("--patch_size", type=int, default=600)
    # these three will be swept by the grid
    p.add_argument("--overlap", type=float, default=0.1)
    p.add_argument("--nms_thresh", type=float, default=0.5)
    p.add_argument("--score_thresh", type=float, default=0.2)
    p.add_argument("--max_detections", type=int, default=1000)
    args = p.parse_args()

    weights_flag = (
        ["--use_release"] if args.use_release else ["--weights", args.weights]
    )

    # **YOUR GRID**: overlap ∈ [0.05,0.10,0.15,0.20,0.25,0.30]
    #                score_thresh ∈ [0.20,0.30,0.40,0.50]
    #                nms_thresh   ∈ [0.30,0.50,0.70]
    param_grid = {
        "overlap": [0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
        "score_thresh": [0.20, 0.30, 0.40, 0.50],
        "nms_thresh": [0.30, 0.50, 0.70],
    }

    results = []
    for combo in ParameterGrid(param_grid):
        for k, v in combo.items():
            setattr(args, k, v)
        mean_cov = kfold_coverage(args, weights_flag)
        print(
            f"→ overlap={args.overlap:.2f}, score={args.score_thresh:.2f}, nms={args.nms_thresh:.2f} → mean coverage = {mean_cov:.3%}"
        )
        results.append({**combo, "mean_coverage": mean_cov})

    pd.DataFrame(results).to_csv("coverage_tuning_results.csv", index=False)
    best = max(results, key=lambda r: r["mean_coverage"])
    print("\n*** Best combo ***")
    print(
        f"overlap={best['overlap']:.2f}, score_thresh={best['score_thresh']:.2f}, nms_thresh={best['nms_thresh']:.2f} → {best['mean_coverage']:.3%}"
    )


if __name__ == "__main__":
    main()
