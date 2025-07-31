# 🌳 GreenCity CV Pipeline

Coordinate CSV  
    │    
    ▼  
[INGEST] → raw image chips  
    │  
    ▼  
[ANALYZE] → quality metrics + fail tags    
    │  
    ▼  
[ENHANCE] → improved chips + new metrics    

## 🛰️ GreenCity_DATA1_INGEST.ipynb
**Purpose**: Load Google Earth Engine image chips and validate structure.

**Key Actions**:
- Reads coordinates from the input DataFrame  
- Pulls per-point NAIP image chips from GEE  
- Saves chips locally as `.jpg` files  

---

## 🧪 GreenCity_DATA2_ANALYSE.ipynb
- **Purpose**: Loads Google Earth Engine image chips and validates their structure.  

**Key Actions**:
  - Computes five metrics: **contrast**, **sharpness**, **brightness**, **edge density**, and **centroid offset**
  - Generates statistical and visual outputs to aid analysis 
  - Qualifies each image as "pass" or "fail" with reason for failure
- **Output**: A filtered DataFrame identifying high-quality images for use and targets for image enhancement.

---

## 🛠️ GreenCity_DATA3_ENHANCE.ipynb
**Purpose**: Improve model-readiness of failed images.

**Key Capabilities**:
  - Can apply tunable combinations of contrast stretching, sharpening, and brightness normalization, and centering
  - Saves enhanced chips to a new output directory
  - Verifies metric improvement visually and numerically 

---

## 🧠 Why This Matters
Low-quality imagery can reduce model performance and generalizability. This pipeline expands usable training data by rescuing failed image chips.

---

## 🔧 Requirements
python 3.9<br> 
ee, geopandas, rasterio, shapely, cv2, numpy, matplotlib, seaborn, tensorflow


##  🚀 How to Run
Run GreenCity_DATA1_INGEST.ipynb to retrieve images from Earth Engine

Run GreenCity_DATA2_ANALYSE.ipynb to compute quality scores

Run GreenCity_DATA3_ENHANCE.ipynb to enhance failed images

No special setup needed beyond Earth Engine authentication, and pathing in the CONFIG sections of each notebook.

## 🧠 Summary

The GreenCity CV pipeline supports image ingestion, quality analysis, and enhancement across 57,000+ NAIP image chips. Each step builds toward one goal: maximizing usable training data by identifying and correcting poor-quality inputs — fast, transparently, and at scale.

- **Ingestion** extracts raw chips from Google Earth Engine per point in our dataset.
- **Analysis** scores each image using interpretable metrics: contrast, brightness, sharpness, edge density, and canopy alignment.
- **Enhancement** applies a tunable OpenCV pipeline to correct failures without introducing artifacts or synthetic textures.

The result: a high-quality, filtered dataset primed for tree detection and canopy segmentation tasks, with traceable improvements and minimal preprocessing burden.




