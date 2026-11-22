# ![GreenCity Banner](https://github.com/user-attachments/assets/00728c5a-488f-46a6-98c2-6c11044e4baf)

**A Machine Learning Platform for Urban Tree Canopy Monitoring & Green Equity**

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square" alt="License">
  </a>
  <a href="https://github.com/antonioamartinez/Green-City/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/antonioamartinez/Green-City?style=flat-square&color=blueviolet" alt="Contributors">
  </a>
  <a href="https://github.com/antonioamartinez/Green-City/discussions">
  <img src="https://img.shields.io/badge/chat-on%20discussions-ff69b4?style=flat-square" alt="Discussions">
</a>
<a href="https://github.com/antonioamartinez/Green-City/stargazers">
  <img src="https://img.shields.io/github/stars/antonioamartinez/Green-City?style=flat-square&color=yellow" alt="Stars">
</a>
</p>

---

> “Cities can’t fix what they can’t see.”  
> — *GreenCity team*

---

## 🚀 Overview

![Equity Map Example](https://github.com/user-attachments/assets/e59be6cb-7cda-467e-8ad0-42f4568558f7)

Urban tree canopy is not distributed equitably. In many cities, wealthier neighborhoods enjoy cool, green streets—while under-resourced communities endure heat, pollution, and greater health risks. The data gap is real: Most urban tree inventories are outdated, incomplete, or prohibitively expensive to maintain.

**GreenCity** bridges this divide using cutting-edge machine learning and high-resolution aerial imagery. Our platform makes invisible tree canopy data *visible, measurable, and actionable*—empowering cities, advocates, and researchers to drive real environmental change.

---

## 🌱 Mission

GreenCity is dedicated to:

- **Democratizing green data:** Delivering up-to-date, high-quality tree canopy information to all communities.
- **Driving environmental justice:** Making inequity visible to inform policy, planning, and funding.
- **Empowering local action:** Equipping cities, researchers, and grassroots advocates with tools to grow healthier, fairer urban forests.

---

## 🛠️ Features

### 💡 Intelligent Detection

- **Automated tree and canopy detection** with deep learning
- **Satellite & aerial imagery support** (Google Earth Engine, ArcGIS, more)
- **Multi-resolution analysis** (60cm to 10cm aerials)

### 🗺️ Interactive Mapping

- **Browser-based explorer:** Visualize tree locations, canopy gaps, and environmental metrics
- **Census block & street-level modes:** Analyze equity down to the block
- **Live metrics:** Canopy coverage, carbon sequestration, heat island data

### 📊 Reporting & Analysis

- **Compare multiple ML models** side-by-side
- **Flexible overlays:** Carbon, temperature, air quality (coming soon)
- **Future-ready:** Downloadable reports & open data export

---

## 🔬 How It Works

### Data Pipeline

1. **Acquire imagery:** Google Earth Engine, ArcGIS, and other sources.
2. **Image filtering/enhancement:** Focused on sharpness, contrast, and urban density.
3. **Tree detection (VGG-16):** Finds tree points; 81% recall, 4.47m avg. localization error.
4. **Canopy detection (DeepForest):** RetinaNet-based crown detection, optimized for city clusters.
5. **Canopy cover segmentation (U-Net):** Pixel-level canopy masks on 60 cm imagery, trained on labels made from USGS 3DEP lidar. See [canopy_detection](canopy_detection/README.md#canopy-cover-segmentation-60-cm-imagery).
6. **Postprocessing:** Merges overlapping crowns, shapes polygons, and prepares data for the web app.

### Key Results

| Component             | Best Result                     |
|-----------------------|---------------------------------|
| Tree Point Detection  | 81% recall, 4.47m error         |
| Tree Point Detection (retuned threshold) | F1 0.641 on the test split (precision 0.650, recall 0.631) |
| Crown Detection       | 88% recall (with enhancement)   |
| Canopy Cover (U-Net, 60 cm) | F1 0.67, 3.8 pp cover error vs lidar on 65 test tiles (DeepForest boxes: F1 0.12) |
| Image Resolution      | 10cm/pixel imagery = best acc.  |
| User Usability        | 92% found UI intuitive (survey) |

### Lessons Learned

- **High-res imagery is essential** (10cm+ for urban canopy)
- **City trees are harder:** Clusters, occlusions, and species mix confuse forest models
- **Visual storytelling moves policy:** Maps reveal patterns that stats alone cannot

---

## 🌍 Live Demo

[![Webpage Preview](https://i.postimg.cc/jdMk7w4G/Teaser-Preview.png)](https://postimg.cc/nCQk8L5k)

*Coming soon: Public demo deployment. Stay tuned!*

---

## 🔮 Roadmap

- 🌲 Tree species & health classification
- 🕒 Time-series tracking (canopy loss/gain)
- 📱 Citizen science validation (mobile)
- 🔥 Overlays: temperature, air quality
- 📥 Data & report downloads
- 🧑‍🔬 Expert calibration per city

---

## ⚙️ Tech Stack

- **Machine Learning:** PyTorch, VGG-16, DeepForest (RetinaNet), U-Net
- **Geospatial:** GDAL, Rasterio, Shapely, GeoPandas
- **Frontend:** Leaflet.js, Mapbox GL, Bootstrap
- **Imagery:** Google Earth Engine, ArcGIS, OpenStreetMap
- **Lidar:** USGS 3DEP point clouds (Entwine Point Tiles on AWS), laspy

---

## 📦 Installation

> **Requirements:** Python 3.10+, pip, git

Each component installs and runs on its own.

1. **Clone the repo:**
   ```bash
   git clone https://github.com/antonioamartinez/Green-City
   cd Green-City
   ```

2. **Canopy detection and canopy cover (DeepForest, U-Net):**
   ```bash
   pip install -r canopy_detection/requirements.txt
   ```
   Commands for each step are in [canopy_detection/README.md](canopy_detection/README.md).

3. **Tree point detection (VGG-16):** run it in the Docker or Apptainer image described in [tree_point_prediction/README.md](tree_point_prediction/README.md).

4. **Web app (Flask + Leaflet):**
   ```bash
   cd deployment/greencityEc2
   pip install -r requirements.txt
   python application.py
   ```
   Open `http://localhost:5000`. Set `FLASK_DEBUG=1` to turn on the debugger.

---

## 🤝 Contributing

We welcome contributions!  
Whether you’re a developer, data scientist, urban ecologist, or passionate resident—your input matters.

- Open issues or propose features
- Send a pull request with a short before/after of what it changes
- Join discussions—help us shape the future of urban green equity!

---

## 👩‍🔬 Citation & Acknowledgements

GreenCity is developed by [Fengchen Liu](#), [Antonio Martinez](#), [Richard Oldham](#), and [Ming-hwei Carol Sun](#).  
Inspired by open data from the City of Pasadena and aerial imagery from open sources.

**Cite this project:**
```
Liu, F., Martinez, A., Oldham, R., Sun, M.-C. (2024). GreenCity: Urban Tree Canopy Monitor. https://github.com/antonioamartinez/Green-City
```

---

## 📄 License

[MIT License](LICENSE)

---

## 🌟 Vision

**GreenCity turns pixels into policy.**  
Our mission: Make urban tree canopy data accessible, accurate, and equitable for every city. In a warming world, *shade is survival—and data is power.*

---

**Grow with us—[star this repo](../../stargazers), [join the community](../../discussions), and help every city become greener, healthier, and more just.**
