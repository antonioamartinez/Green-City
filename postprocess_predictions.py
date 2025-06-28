#!/usr/bin/env python
"""
postprocess_predictions.py

Read a GeoJSON of DeepForest bounding-box predictions,
apply Soft-NMS or Weighted Boxes Fusion to remove overlaps,
and write out a cleaned GeoJSON in the same CRS as the input.
"""

import argparse  # CLI parsing :contentReference[oaicite:6]{index=6}
import rasterio  # Raster I/O & transforms :contentReference[oaicite:7]{index=7}
import geopandas as gpd  # Vector I/O & GeoDataFrame :contentReference[oaicite:8]{index=8}
import pandas as pd
from shapely.geometry import (
    box,
)  # Build rectangular polygons :contentReference[oaicite:9]{index=9}
from ensemble_boxes import (
    soft_nms,
    weighted_boxes_fusion,
)  # Soft-NMS & WBF :contentReference[oaicite:10]{index=10}


def process_tile(
    df_tile: pd.DataFrame,
    method: str,
    iou_thr: float,
    score_thr: float,
    wbf_iou_thr: float,
    wbf_skip_thr: float,
) -> gpd.GeoDataFrame:
    """Process one tile: apply Soft-NMS or WBF, return GeoDataFrame in tile CRS."""
    src = rasterio.open(df_tile.image_path.iloc[0])
    tile_crs = src.crs
    width, height = src.width, src.height
    transform = src.transform

    # Extract pixel boxes & scores
    boxes = df_tile[["xmin", "ymin", "xmax", "ymax"]].values.tolist()
    scores = df_tile["score"].tolist()
    labels = [0] * len(boxes)  # single-class

    # Normalize to [0,1] as ensemble-boxes expects
    boxes_norm = [
        [x1 / width, y1 / height, x2 / width, y2 / height] for x1, y1, x2, y2 in boxes
    ]

    # Apply ensemble method
    if method == "soft_nms":
        boxes_out, scores_out, _ = soft_nms(
            [boxes_norm], [scores], [labels], iou_thr=iou_thr, thresh=score_thr
        )
    else:  # Weighted Boxes Fusion
        boxes_out, scores_out, _ = weighted_boxes_fusion(
            [boxes_norm],
            [scores],
            [labels],
            iou_thr=wbf_iou_thr,
            skip_box_thr=wbf_skip_thr,
        )

    # Denormalize back to pixel coords
    boxes_denorm = [
        [b[0] * width, b[1] * height, b[2] * width, b[3] * height] for b in boxes_out
    ]

    src.close()

    # Build output records
    records = []
    for (x1, y1, x2, y2), sc in zip(boxes_denorm, scores_out):
        minx, miny = transform * (x1, y1)
        maxx, maxy = transform * (x2, y2)
        geom = box(minx, miny, maxx, maxy)
        records.append(
            {
                "xmin": x1,
                "ymin": y1,
                "xmax": x2,
                "ymax": y2,
                "label": "Tree",
                "score": sc,
                "image_path": df_tile.image_path.iloc[0],
                "geometry": geom,
            }
        )

    # Handle empty-case: ensure 'geometry' column exists :contentReference[oaicite:11]{index=11}
    if not records:
        cols = [
            "xmin",
            "ymin",
            "xmax",
            "ymax",
            "label",
            "score",
            "image_path",
            "geometry",
        ]
        empty = pd.DataFrame([], columns=cols)
        return gpd.GeoDataFrame(empty, geometry="geometry", crs=tile_crs)

    return gpd.GeoDataFrame(records, geometry="geometry", crs=tile_crs)


def main():
    parser = argparse.ArgumentParser(
        description="Post-process DeepForest GeoJSON with Soft-NMS or WBF"
    )
    parser.add_argument("predictions", help="Input GeoJSON")
    parser.add_argument("output", help="Output GeoJSON")
    parser.add_argument(
        "--method",
        choices=["soft_nms", "wbf"],
        default="soft_nms",
        help="Ensembling method",
    )
    parser.add_argument("--iou_thr", type=float, default=0.5)
    parser.add_argument("--score_thr", type=float, default=0.1)
    parser.add_argument("--wbf_iou_thr", type=float, default=0.5)
    parser.add_argument("--wbf_skip_thr", type=float, default=0.0)
    args = parser.parse_args()

    # Read input and capture its CRS :contentReference[oaicite:12]{index=12}
    gdf = gpd.read_file(args.predictions)
    output_crs = gdf.crs

    # Process tiles and collect results
    processed = []
    for _, group in gdf.groupby("image_path"):
        df_tile = pd.DataFrame(group.drop(columns="geometry"))
        fused = process_tile(
            df_tile,
            args.method,
            args.iou_thr,
            args.score_thr,
            args.wbf_iou_thr,
            args.wbf_skip_thr,
        )
        processed.append(fused)

    if not processed:
        print("No detections to process.")
        return

    # Concatenate, reproject to input CRS, and write GeoJSON :contentReference[oaicite:13]{index=13}
    result = gpd.GeoDataFrame(
        pd.concat(processed, ignore_index=True), crs=processed[0].crs
    ).to_crs(output_crs)

    result.to_file(args.output, driver="GeoJSON")
    print(f"Wrote {len(result)} fused detections → {args.output}")


if __name__ == "__main__":
    main()
