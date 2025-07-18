import geopandas as gpd
from shapely.geometry import box

# 1. Read your points GeoJSON
gdf = gpd.read_file("merged_pasadena (4).geojson")

# 2. (Optional but highly recommended) Project to a CRS with metric units
#    so that your “size” is in meters rather than degrees.
#    Here we use Web Mercator (epsg:3857); pick whatever’s appropriate.
gdf = gdf.to_crs(epsg=2229)

# 3. Choose half the side-length of your bounding box (in the same units as your CRS)
half_side = 12  # e.g. 6 meters → 12 m × 12 m squares

# 4. Replace each point geometry with a square polygon around it
gdf["geometry"] = gdf.geometry.apply(
    lambda pt: box(
        pt.x - half_side, pt.y - half_side, pt.x + half_side, pt.y + half_side
    )
)

# 5. (Optional) If you want to go back to WGS84 lon/lat for web-mapping:
gdf = gdf.to_crs(epsg=2229)

# 6. Write out as a new GeoJSON
gdf.to_file("predictions_bboxes.geojson", driver="GeoJSON")
