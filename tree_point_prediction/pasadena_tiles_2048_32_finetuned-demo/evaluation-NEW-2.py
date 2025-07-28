import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
from shapely.geometry import LineString  # Imported here
import os
import pandas as pd

# Load the GeoJSON files
gdf_groundtruth = gpd.read_file("merged_pasadena_groundtruth.json")
gdf_predictions = gpd.read_file("merged_pasadena.json")

# Reproject to UTM zone 11N (meters) for distance calculations
gdf_groundtruth = gdf_groundtruth.to_crs("EPSG:32611")
gdf_predictions = gdf_predictions.to_crs("EPSG:32611")

# Extract coordinates as numpy arrays
gt_coords = np.array(list(zip(gdf_groundtruth.geometry.x, gdf_groundtruth.geometry.y)))
pred_coords = np.array(list(zip(gdf_predictions.geometry.x, gdf_predictions.geometry.y)))

# Set distance threshold in meters
threshold = 12.0

# Build KDTree for predicted points
tree = cKDTree(pred_coords)

# Initialize a set for matched predicted indices and a list for match distances
matched_pred = set()
match_distances = []

# Greedy matching: Match each ground truth tree to the closest available predicted tree
for gt_point in gt_coords:
    # Find indices of predicted points within the threshold
    indices = tree.query_ball_point(gt_point, threshold)
    available_indices = [i for i in indices if i not in matched_pred]
    if available_indices:
        # Find the closest available predicted point
        distances = [np.linalg.norm(gt_point - pred_coords[i]) for i in available_indices]
        min_idx = available_indices[np.argmin(distances)]
        matched_pred.add(min_idx)
        match_distances.append(min(distances))

# Calculate evaluation metrics for the 12m threshold
tp = len(matched_pred)
fn = len(gdf_groundtruth) - tp
fp = len(gdf_predictions) - tp
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
avg_distance_matches = np.mean(match_distances) if match_distances else 0

# Compute average distance to the closest predicted tree for all ground truth trees
distances, pred_indices = tree.query(gt_coords, k=1)
avg_distance_closest = np.mean(distances)

# Generate histogram of distances to closest predicted trees
plt.figure(figsize=(10, 6))
plt.hist(distances, bins=1000, color='skyblue', edgecolor='black')
plt.title('Histogram of Distance to Closest Predicted Tree')
plt.xlabel('Distance (meters)')
plt.xlim(0, 25)
plt.ylabel('Frequency')
plt.grid(True)
plt.axvline(x=avg_distance_closest, color='red', linestyle='--', label=f'Average Distance: {avg_distance_closest:.2f}m')
plt.legend()
plt.savefig('distance_histogram.png')
plt.close()

# Generate histogram of recall across thresholds (6 to 20 meters)
thresholds = np.arange(6, 21, 1)
recalls = []
for t in thresholds:
    matched_pred = set()
    for gt_point in gt_coords:
        indices = tree.query_ball_point(gt_point, t)
        available_indices = [i for i in indices if i not in matched_pred]
        if available_indices:
            min_idx = available_indices[np.argmin([np.linalg.norm(gt_point - pred_coords[i]) for i in available_indices])]
            matched_pred.add(min_idx)
    recalls.append(len(matched_pred) / len(gt_coords))

plt.figure(figsize=(10, 6))
plt.plot(thresholds, recalls, marker='o', color='green', label='Recall')
plt.axvline(x=12, color='red', linestyle='--', label='12m Threshold (81%)')
plt.title('Recall vs. Threshold Distance')
plt.xlabel('Threshold Distance (meters)')
plt.ylabel('Recall')
plt.legend()
plt.grid(True)
plt.savefig('recall_threshold_plot.png')
plt.close()

# Save recall_threshold data to CSV
recall_df = pd.DataFrame({'threshold': thresholds, 'recall': recalls})
recall_df.to_csv('recall_threshold_data.csv', index=False)

# Generate GeoJSON with lines connecting ground truth to closest predicted trees
lines = []
for i, gt_point in enumerate(gt_coords):
    pred_point = pred_coords[pred_indices[i]]
    line = LineString([gt_point, pred_point])  # Create LineString directly
    lines.append(line)

gdf_lines = gpd.GeoDataFrame(geometry=lines, crs="EPSG:32611")
gdf_lines.to_file("tree_matches.geojson", driver='GeoJSON')

# Define the file name for saving metrics
metrics_file = "evaluation_metrics.csv"

# Create metrics dictionary
metrics = {
    'Metric': ['True Positives (TP)', 'False Negatives (FN)', 'False Positives (FP)', 'Precision', 'Recall', 'F1 Score', 'Average Distance for Matches', 'Average Distance to Closest Predicted Tree'],
    'Value': [tp, fn, fp, f"{precision:.4f}", f"{recall:.4f}", f"{f1:.4f}", f"{avg_distance_matches:.2f} meters", f"{avg_distance_closest:.2f} meters"]
}

# Convert to DataFrame and save as CSV
metrics_df = pd.DataFrame(metrics)
metrics_df.to_csv(metrics_file, index=False)

print(metrics_df)

# Confirmation messages
print(f"Metrics have been saved to {metrics_file}")
print("Distance histogram saved to 'distance_histogram.png'")
print("Recall vs. Threshold plot saved to 'recall_threshold_plot.png'")
print("Recall vs. Threshold data saved to 'recall_threshold_data.csv'")
print("Matching lines saved to 'tree_matches.geojson'")