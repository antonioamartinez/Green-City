🌳 GreenCity
A Machine Learning Platform for Urban Tree Canopy Monitoring & Green Equity

✨ Overview: A Story of Data, Justice, and Leaves
In many cities, access to trees is a luxury. Wealthier neighborhoods enjoy cool, green streets—while lower-income communities endure heat, pollution, and poor health outcomes.

Manual tree inspections are expensive and rare in underserved areas. But the need for data is urgent.

That's where GreenCity steps in.

Like a digital guardian, GreenCity utilizes satellite vision and machine learning to identify where shade grows—and where it doesn't. It maps trees, analyzes canopy, and makes environmental inequity visible.

With it, city planners, local advocates, and arborist groups can finally back up their instincts with real, block-by-block data.

🌱 Project Mission
GreenCity empowers under-resourced cities and communities with:

An automated way to detect trees and estimate canopy coverage

A browser-based tool that visualizes tree presence and gaps

Metrics to support policy change, grant applications, and urban planning

We're not just counting trees—we're reclaiming green equity.

🛠️ What We've Built
🌍 Aerial Intelligence
Using satellite and aerial imagery from Google Earth Engine and ArcGIS archives, we process large-scale urban environments to detect canopy with machine learning.

🧠 Machine Learning Models
🌳 Tree Point Prediction (VGG)
Started with Pasadena's street tree dataset

Trained a VGG-based CNN for tree point detection

Achieved 70% recall, improved to 75% after image enhancement

🍃 Crown Detection (DeepForest)
Used DeepForest (RetinaNet) to detect canopy using bounding boxes

Initial attempts using 60cm imagery yielded unsatisfactory results due to resolution limitations.

Acquired 10cm aerial imagery from Los Angeles County ArcGIS archive

Achieved improved performance with hyper tuning, though overlapping trees posed challenges

Merged overlapping crown predictions using Shapely geometry tools

🗺️ The Map Interface
GreenCity's interactive browser-based application supports:

🧭 Census Block Mode
View canopy percentage, carbon absorption, and tree density per 100-acre block.

🏙️ Streetview Roaming
Navigate a street-level map with tree polygons overlaid in real-world locations.

📡 Live Metrics
See estimated CO₂ sequestration, heat island implications, and coverage statistics.

📝 Note: Downloadable reports are not yet available but are planned as a future feature.

🔍 Experiments & Evaluation
Component   Result
Tree Point Detection (VGG)  75% recall (on enhanced 60cm imagery)
Crown Detection (DeepForest)    Improved accuracy with 10cm imagery
Image Resolution Impact 10cm necessary for accurate canopy work
Streetview Usability (Survey): 92% found the interface intuitive and useful

💡 What We Learned
Tree detection is susceptible to image resolution—10cm or better is essential.

Urban environments are more challenging than forests: clustered trees and mixed species species can confuse models.

Bounding boxes alone aren't sufficient—polygon merging and shape reasoning are crucial.

Visual storytelling (not just raw data) is what moves people and policy.

🔮 Future Improvements
🌲 Tree species and health classification

🕒 Time-series tracking of canopy loss or growth

📱 Citizen-science tools for mobile validation

🔥 Integration with temperature and air quality overlays

📥 Downloadable data and report generation

🧑‍🔬 Expert-validated datasets per city for model calibration

⚙️ Tech Stack
Machine Learning: PyTorch, VGG, DeepForest (RetinaNet)

Geospatial Tools: GDAL, Rasterio, Shapely, GeoPandas

Frontend Mapping: Leaflet.js, Mapbox GL

Imagery Sources: Google Earth Engine, ArcGIS, OpenStreetMap

🤝 Who It's For
🌆 City Governments looking to prioritize equitable green infrastructure

🌳 Urban Forestry Groups Seeking Canopy Gap Visibility

🗣️ Community Advocates fighting environmental injustice

📊 Researchers in urban ecology and climate adaptation

🧭 Conclusion: The GreenCity Vision
GreenCity turns pixels into policy. It uses AI not just to map trees—but to reveal patterns of neglect, resilience, and opportunity. In a warming world, shade is survival—and data is power.

We started with Pasadena. But the future is every city that wants to grow fairly, intelligently, and green.