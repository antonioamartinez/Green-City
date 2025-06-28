#!/usr/bin/env python
"""
merge_polygons.py

Read a GeoJSON of DeepForest bounding-box predictions,
merge overlapping boxes into exact union polygons using Shapely,
and write out the final polygons back to GeoJSON.
"""

import argparse
import geopandas as gpd  # GeoDataFrame I/O :contentReference[oaicite:11]{index=11}
from shapely.ops import (
    unary_union,
)  # Union of many geometries :contentReference[oaicite:12]{index=12}


def merge_polygons(input_geojson: str, output_geojson: str):
    # 1. Load predictions (with existing 'geometry' column of polygons)
    gdf = gpd.read_file(
        input_geojson
    )  # reads CRS and geometry automatically :contentReference[oaicite:13]{index=13}
    src_crs = gdf.crs  # remember input CRS

    # 2. Compute the union of all geometries in one shot
    merged = unary_union(
        gdf.geometry
    )  # returns Polygon or MultiPolygon :contentReference[oaicite:14]{index=14}

    # 3. Split MultiPolygon into individual Polygons
    if merged.geom_type == "Polygon":
        polygons = [merged]
    else:  # MultiPolygon
        polygons = list(
            merged.geoms
        )  # iterate over each part :contentReference[oaicite:15]{index=15}

    # 4. Build a new GeoDataFrame and preserve CRS
    merged_gdf = gpd.GeoDataFrame(geometry=polygons, crs=src_crs)

    # 5. Write to GeoJSON
    merged_gdf.to_file(
        output_geojson, driver="GeoJSON"
    )  # writes lon/lat or projected coords per src_crs :contentReference[oaicite:16]{index=16}
    print(f"Wrote {len(merged_gdf)} merged polygons to {output_geojson}")


def main():
    parser = argparse.ArgumentParser(
        description="Merge overlapping bounding boxes into exact polygons"
    )
    parser.add_argument(
        "input_geojson", help="Path to input GeoJSON of box predictions"
    )
    parser.add_argument("output_geojson", help="Path to write merged polygons GeoJSON")
    args = parser.parse_args()
    merge_polygons(args.input_geojson, args.output_geojson)


if __name__ == "__main__":
    main()
