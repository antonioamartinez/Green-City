from flask import Flask, jsonify, request, abort, render_template
import json, os
import numpy as np
import geopandas as gpd
from pathlib import Path
from flask_cors import CORS
from shapely.geometry import shape
import requests

print(os.getcwd())

base_dir = os.getcwd()

app = Flask(__name__)  # "application" is needed for Elastic Beanstalk
CORS(app)

blocks = None
geojson_dir = "http://www.carolsun.top/210/srv/geojson/"
headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
}
geojsonFiles = {
    "training": {"file": "Street_ROW_Trees.geojson","treeType": "pt", "crs": "4326", "model_output": None},
    "baseline": {"file": "merged_pasadena_2048_0.6m_baseline.geojson","treeType": "pt","crs": "2229", "model_output": None},
    "deepforest": {"file": "predictions_4326_merged.geojson","treeType": "box","crs": "4326", "model_output": None}
    #"deepforest": {"file": "deep_forest_init.geojson","treeType": "box","model_output": None},
    #"deepforest10cm": {"file": "pasadena_predictions_4326_10cm.geojson","treeType": "box","model_output": None},
    #"cv60cm": {"file": "merged_pasadena_60cm_cv.geojson","treeType": "pt","model_output": None},
    #"deepforest10cmMerged": {"file": "pasadena_merged_polygons_4326.geojson","treeType": "box","model_output": None}
}

def sanitize_gdf(gdf):
    for col in gdf.columns:
        if col != gdf.geometry.name:
            # Convert any problematic types to strings
            gdf[col] = gdf[col].apply(lambda x: str(x) if isinstance(x, (dict, list, np.ndarray)) else x)
    return gdf

def load_blocks():
    global blocks
    #url = os.path.join(geojson_dir, "2010_Census_Blocks.geojson")
    url = geojson_dir +"2010_Census_Blocks.geojson"
    print(f"Loading blocks from {url} ...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    geojson = response.json()
    geoms = [shape(feature["geometry"]) for feature in geojson["features"]]
    props = [feature["properties"] for feature in geojson["features"]]
    blocks = gpd.GeoDataFrame(props, geometry=geoms, crs="EPSG:4326")
    #blocks = gpd.read_file(path, engine="fiona")

    blocks["OBJECTID"] = blocks["OBJECTID"].astype(str).str.strip('"')
    blocks_proj = blocks.to_crs("EPSG:3857")
    blocks_proj["areaSqM"] = blocks_proj.geometry.area
    return blocks, blocks_proj

def process_model(file, model, tree_type, blocks, blocks_proj, crs):
    print(f"Processing model '{model}' from file '{file}' (treeType={tree_type}) ...")
    url = geojson_dir + file
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    geojson = response.json()
    geoms = [shape(feature["geometry"]) for feature in geojson["features"]]
    props = [feature["properties"] for feature in geojson["features"]]
    trees = gpd.GeoDataFrame(props, geometry=geoms, crs=f"EPSG:{crs}")
    #trees = gpd.read_file(os.path.join(geojson_dir, file), engine="fiona")
    if str(crs) != "4326":
        trees = trees.to_crs("EPSG:4326")
        
    trees_proj = trees.to_crs("EPSG:3857")

    if tree_type == "pt":
        joined = gpd.sjoin(trees_proj, blocks_proj, how="inner", predicate="within")
    elif tree_type == "box":
        trees_proj["center"] = trees_proj.geometry.centroid
        rect_centers = trees_proj.set_geometry("center")
        joined = gpd.sjoin(rect_centers, blocks_proj, how="inner", predicate="within")

    joined_latlon = joined.to_crs("EPSG:4326")
    tree_counts = joined.groupby("index_right").size().rename("treeCount")
    blocks_proj["treeCount"] = blocks_proj.index.map(tree_counts).fillna(0).astype(int)
    blocks_proj["density"] = (blocks_proj["treeCount"] / blocks_proj["areaSqM"]) * 10000

    print(f"Finished processing model '{model}'.")
    return {
        "density": dict(zip(blocks_proj["OBJECTID"], blocks_proj["density"])),
        "gdf": trees
    }


def load_and_cache_data():
    blocks, blocks_proj = load_blocks()
    for model, info in geojsonFiles.items():
        result = process_model(info["file"], model, info["treeType"], blocks, blocks_proj, info["crs"])
        if result:
            geojsonFiles[model]["model_output"] = result

# Initialize on startup
load_and_cache_data()


@app.route('/api/get_filtered_trees', methods=['GET', 'POST'])
def get_filtered_trees():

    global blocks, geojsonFiles

    if request.method == 'POST':
        data = request.get_json()
        if not data or "models" not in data:
            return jsonify({"error": "Missing 'models' in request"}), 400

        models = data["models"]

        if "blockID" in data:
            block_id = str(data["blockID"])
            block_row = blocks.loc[blocks['OBJECTID'] == block_id]
            if block_row.empty:
                return jsonify({"error": f"BlockID {block_id} not found"}), 404
            block_geom = block_row.iloc[0].geometry
        elif "polygon" in data:
            try:
                block_geom = shape(data["polygon"])
            except Exception as e:
                return jsonify({"error": f"Invalid polygon: {str(e)}"}), 400
        else:
            return jsonify({"error": "Missing 'blockID' or 'polygon' in request"}), 400
    else:  # GET
        block_id = request.args.get("blockID")
        models_param = request.args.get("models")
        if not block_id or not models_param:
            return jsonify({"error": "Missing 'blockID' or 'models' query parameters"}), 400
        block_id = str(block_id)
        models = models_param.split(",")
        block_row = blocks.loc[blocks['OBJECTID'] == str(block_id)]
        if block_row.empty:
            return jsonify({"error": f"BlockID {block_id} not found"}), 404
        block_geom = block_row.iloc[0].geometry

    # Area check (projected to EPSG:3857 for meters)
    #block_proj = block_row.to_crs("EPSG:3857")
    #area_sqm = block_proj.iloc[0].geometry.area
    #area_acres = area_sqm / 4046.8564224

    #if area_acres > 150:
        #return jsonify({"error": "bigArea"}), 413  # Payload Too Large


    response = {}

    for model in models:
        if model not in geojsonFiles:
            continue
        gdf = geojsonFiles[model]["model_output"]['gdf']
        if gdf is None or gdf.empty:
            response[model] = []
            continue
        
        tree_type = geojsonFiles[model]["treeType"]

        if tree_type == "pt":
            filtered_gdf = gdf[gdf.geometry.within(block_geom)]
        else:  # 'box' or other types
            filtered_gdf = gdf[gdf.geometry.intersects(block_geom)]
            '''
            centroids = gdf.geometry.centroid
            within_mask = centroids.within(block_geom)
            filtered_gdf = gdf[within_mask]
            '''
        #print(filtered_gdf)

        if not filtered_gdf.empty:
            features = filtered_gdf.__geo_interface__["features"]    
        else:
            features = []

        #response[model] = features
        #print(features)
        response[model] = {
            "type": "FeatureCollection",
            "features": json.loads(filtered_gdf.to_json())["features"]
        }
                    
    return jsonify(response)


@app.route('/api/get_density', methods=['GET', 'POST'])
def get_density():
    if request.method == 'POST':
        data = request.get_json()
        if not data or "models" not in data:
            return jsonify({"error": "Missing 'models' in POST data"}), 400
        model_names = data["models"]
    else:  # GET method
        models_param = request.args.get("models")
        if not models_param:
            return jsonify({"error": "Missing 'models' query parameter"}), 400
        model_names = models_param.split(",")

    combined_density = {}
    count_map = {}

    for model in model_names:
        model = model.strip()
        if model not in geojsonFiles:
            continue
        model_output = geojsonFiles[model].get("model_output")
        if not model_output or "density" not in model_output:
            continue

        density = model_output["density"]
        for obj_id, value in density.items():
            combined_density[obj_id] = combined_density.get(obj_id, 0) + value
            count_map[obj_id] = count_map.get(obj_id, 0) + 1

    # Average the densities
    for obj_id in combined_density:
        combined_density[obj_id] /= count_map[obj_id]

    return jsonify(combined_density)


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/client')
def client():
    return render_template('indexClient.html')

@app.route('/srv')
def srv():
    return render_template('indexServer.html')

if __name__ == "__main__":
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)