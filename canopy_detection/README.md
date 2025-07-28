# GreenCity Urban Tree Canopy Detection

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Docker Build](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

A fully automated, deep learning-based pipeline for **urban tree canopy detection** from high-resolution aerial imagery.  
Optimized for research, city planning, and environmental monitoring.  
**Powered by [DeepForest](https://deepforest.readthedocs.io/en/latest/)** and designed for reproducible, high-throughput urban forest analysis.

---

## 🚀 Features

- **Scalable Tiling:** Efficiently splits giant aerial GeoTIFFs into RAM-manageable tiles.
- **Image Optimization:** Batch enhances tiles (white balance, CLAHE) for optimal deep learning performance.
- **Annotation Preparation:** Converts polygons/boxes to DeepForest-ready CSV with normalization and clamping.
- **Custom Fine-Tuning:** Full control over RetinaNet, advanced loss logging, and backbone unfreezing.
- **Batch Inference:** Predicts all tiles in a folder, outputs ready for QGIS (GeoJSON, Shapefile, GeoPackage, CSV).
- **Coverage-Oriented Evaluation:** Precision, recall, F1, and coverage at arbitrary radii.
- **Automated Hyperparameter Grid Search:** Finds the best detection settings for maximum canopy coverage.
- **Advanced Postprocessing:** Merges overlapping predicted boxes into precise canopy polygons for further GIS analysis.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Pipeline Workflow](#pipeline-workflow)
- [Script Details](#script-details)
- [Example Data](#example-data)
- [Docker Usage](#docker-usage)
- [License](#license)
- [Citation](#citation)
- [Contact](#contact)

---

## Installation

### **Requirements**

- **Python 3.8+**
- **CUDA-enabled GPU** (recommended for training/inference)
- See the [Dockerfile](Dockerfile) for a fully reproducible environment with all dependencies (DeepForest, Rasterio, Shapely, OpenCV, etc.)

### **Local Setup**

```bash
git clone https://github.com/antonioamartinez/Green-City
cd canopy-detection
pip install -r requirements.txt
```

---

## Quick Start

1. **Tile and Enhance Your Aerial Imagery**
2. **Prepare Training Annotations (CSV from GeoJSON)**
3. **Fine-Tune DeepForest**
4. **Batch Predict and Output GIS Files**
5. **Evaluate Results and Tune Parameters**
6. **Merge Predicted Boxes to Generate Final Canopy Polygons**

---

## Pipeline Workflow

### 1. **Tiling Large GeoTIFFs**

Split huge orthomosaics into tiles for efficient processing:

```bash
python 00_tile_mosaic.py   --mosaic Pasadena_Whole_Map.tif   --out_dir tile_cache   --tile_size 4096
```

### 2. **Image Enhancement for ML**

Enhance tile contrast and color for robust model predictions:

```bash
python 01_optimize_tiles.py
# Input/output folders are set in the script.
```

### 3. **Prepare DeepForest CSV Annotations**

Convert polygons/boxes from GeoJSON to normalized CSV for DeepForest:

```bash
python 02_prepare_pseudo_dataset.py   --geojson predictions_bboxes.geojson   --tile_dir optimized_pasadena_tiles_800   --output_csv annotations.csv
```

### 4. **Fine-Tune DeepForest Model**

Custom training with adjustable anchors, thresholds, and epochs:

```bash
python 03_finetune_deepforest.py   -a annotations.csv   -r optimized_pasadena_tiles_800   -o df_weights.pth   -e 30   -v 0.1
```

### 5. **Batch Prediction Over All Tiles**

Outputs GIS-ready predictions in multiple formats:

```bash
python 04_predict_tile_folder.py   --weights df_weights.pth   --tile_dir optimized_pasadena_tiles_800   --patch_size 600   --overlap 0.5   --nms_thresh 0.5   --score_thresh 0.2   --max_detections 1000   --extra_crs 4326
```

### 6. **Evaluation: Coverage and Accuracy**

Evaluate predictions using overlap and distance metrics:

```bash
python 05_evaluate_distance.py   --gt_geojson merged_gt.geojson   --pred_geojson runs/run_<timestamp>/predictions.geojson   --out_csv metrics_plus_distance.csv   --radius 12   --buffer 12
```

### 7. **Hyperparameter Tuning (Grid Search)**

Find the best model settings for maximum coverage:

```bash
python 06_coverage_tuning.py   --tile_dir optimized_pasadena_tiles_800   --gt_geojson merged_gt.geojson   --weights df_weights.pth   --k_folds 5   --radius 12   --buffer 12
```

### 8. **Merge Overlapping Boxes into Canopy Polygons**

Get the final set of canopy polygons for analysis:

```bash
python 07_merge_polygons.py   runs/run_<timestamp>/predictions.geojson   merged_canopy.geojson
```

---

## Script Details

| Script | Purpose |
|---|---|
| `00_tile_mosaic.py` | Tile large aerial GeoTIFFs for memory-efficient processing |
| `01_optimize_tiles.py` | Batch enhance tile imagery for ML (white balance, CLAHE) |
| `02_prepare_pseudo_dataset.py` | Convert GeoJSON boxes to DeepForest-ready CSV |
| `03_finetune_deepforest.py` | Fine-tune DeepForest on your urban data |
| `04_predict_tile_folder.py` | Predict on all tiles, output for GIS review |
| `05_evaluate_distance.py` | Evaluate model coverage and accuracy (distance/overlap) |
| `06_coverage_tuning.py` | Automated grid search for best model hyperparameters |
| `07_merge_polygons.py` | Merge overlapping detection boxes to polygons |

---

## Example Data

- **Input Imagery:** e.g., `Pasadena_Whole_Map.tif` or any high-res aerial tile
- **Ground Truth:** Polygon or point GeoJSON
- **Outputs:** GeoJSON, Shapefile, GeoPackage, CSV with WKT; merged canopy polygons

---

## Docker Usage

For **maximum reproducibility and ease**, use the included Dockerfile.

### **Build the Image**

```bash
docker build -t martianucb/greencity .
```

### **Run the Container**

```bash
docker run --gpus all -v $(pwd):/workspace -it martianucb/greencity bash
```
*Replace `--gpus all` if not using a GPU.*

---

## License

[MIT License](LICENSE)

---

## Citation

If you use this pipeline in your research or project, please cite:

- [DeepForest: A Python package for RGB deep learning tree crown delineation](https://deepforest.readthedocs.io/en/latest/)
- GreenCity.

---

## Contact

- Maintainer: [Antonio Martinez]  
- Email: [martian@berkeley.edu]  
- Issues and PRs welcome!

---

**Built for accurate, scalable urban tree mapping.  
Tested on real city-scale data. Fork, adapt, and deploy!**
