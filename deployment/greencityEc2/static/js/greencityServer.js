//const serverName = "http://localhost:5000/"
const serverName = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/`;
const infoDict = {
    "co2": `A healthy tree absorbs approx. <strong>10 kg</strong> (22 lbs) of CO₂ per year<sup>[1]</sup>.<br>
  <small><a href="https://onetreeplanted.org/blogs/stories/how-much-co2-does-tree-absorb?utm_source=chatgpt.com" target="_blank" rel="noopener noreferrer">
    [One Tree Planted - How Much CO₂ Does a Tree Absorb?]
  </a></small>`,
    "pm2": `An average urban tree removes ~<strong>0.015 kg</strong> of PM₂.₅/year.  
  One hectare of canopy removes ~<strong>67 kg</strong>/year.<br>
  <a href="https://www.itreetools.org/documents/560/i-Tree_Canopy_Air_Pollutant_Removal_and_Monetary_Value_Model_Descriptions.pdf" target="_blank" rel="noopener noreferrer">
    [i-Tree Canopy Model Description (2022)]
  </a>`, 
    "kgHa": `1 hectare of healthy canopy removes ~<strong>4.7 kg</strong> of PM₂.₅/year  
  (~<strong>12.9 g/m²/year</strong>).<br>
  <a href="https://www.itreetools.org/documents/389/Reporte_Intec.pdf" target="_blank" rel="noopener noreferrer">
    [i-Tree Eco, USFS]
  </a>`,
    "largeArea": `The area is too big, please use either 100 Acre box or street view selection.`
}
function getToolTip(text){
    return `<span class="tooltip-wrapper">
        <span class="tooltip-icon" onclick="toggleTooltip(this)">i</span>
        <div class="tooltip-bubble" style="display: none;">
            ${text}
        </div>
    </span>`;
}

const infoBoxDefaultHTML = `
  <div class="sidebarmenu">Tree Benefits</div>
  <div class="infoText"><b>How Much CO2 Does A Tree Absorb?</b></div>
  <div class="infoText">On average, each tree absorbs 10 kilograms/22 pounds of CO2 per year</div>
    ${getToolTip(infoDict['co2'])}
  <hr>
  <div class="infoText"><b>How much pollutant (PM₂.₅) can a tree remove?</b></div>
  <div class="infoText">An urban tree removes 0.015 kg (15 g) PM₂.₅ pollutant per year</div>
  ${getToolTip(infoDict['pm2'])}
  <div class="infoText">1 hectare of healthy tree canopy can remove ≈ 4.7 kg of PM2.5 per year</div>
    ${getToolTip(infoDict['kgHa'])}
  `;


function updateInfoBox(feature, selectedPoints, numModel) {
    const areaSqMeters = turf.area(feature);
    const areaAcres = areaSqMeters / 4046.8564224;
    const hectare = areaAcres / 2.47105;

    let avgDensity, avgTreeCount;

    const pointCount = selectedPoints.features.length / numModel;
    avgTreeCount = pointCount;
    avgDensity = pointCount / hectare;

    // Build output
    let htmlOut = `<div class="sidebarmenu">Selected Area</div>`;
    htmlOut += `<div class="infoText">Area: ${areaAcres.toFixed(0)} Acre<br>`;
    htmlOut += `Model Selected: ${numModel}<br>`;
    htmlOut += `Avg Tree Count: ${avgTreeCount.toFixed(0)}<br>`;
    htmlOut += `Density: ${avgDensity.toFixed(2)} (count/hectare)<br>`;
    htmlOut += `</div><hr>`;

    // CO₂ (kg and tonnes)
    const totalCO2_kg = avgTreeCount * 10;
    const totalCO2_tonnes = totalCO2_kg / 1000;
    htmlOut += `<div class="infoText">The selected area absorbed a total of ${totalCO2_kg.toFixed(2)} kg (${totalCO2_tonnes.toFixed(2)} tonnes) CO₂ per year`;
    htmlOut += `<br>${getToolTip(infoDict['co2'])}</div>`;

    const polygonFeatures = selectedPoints.features.filter(f => f.geometry.type !== "Point");

    if (polygonFeatures.length > 0) {
        // Track how many models contributed polygons
        const modelSet = new Set();
        polygonFeatures.forEach(f => {
            if (f.properties?.model) {
                modelSet.add(f.properties.model);
            }
        });

        const numPolygonModels = modelSet.size || 1; // avoid divide-by-zero

        const polygonCollection = {
            type: "FeatureCollection",
            features: polygonFeatures
        };

        const totalSqMeters = turf.area(polygonCollection);
        const avgSqMeters = totalSqMeters / numPolygonModels;
        const totalHectares = avgSqMeters / 10000;

        const canopy_pm25_kg = totalHectares * 4.7;
        const canopy_pm25_tonnes = canopy_pm25_kg / 1000;
        htmlOut += `<hr>
        <div class="infoText">An estimated ${totalHectares.toFixed(2)}ha canopy area are detected in the selection.<br> 
        <br>The canopy removed approximately ${canopy_pm25_kg.toFixed(2)} kg (${canopy_pm25_tonnes.toFixed(4)} tonnes) pollution (PM₂.₅) per year
        <br>${getToolTip(infoDict['kgHa'])}</div>`;
    }
    else{
    // PM2.5 (kg and tonnes)
        const PM25_per_tree_kg = 0.015;
        const total_pm25_kg = avgTreeCount * PM25_per_tree_kg;
        const total_pm25_tonnes = total_pm25_kg / 1000;
        htmlOut += `<hr>
        <div class="infoText">The selected area removed approximately ${total_pm25_kg.toFixed(2)} kg (${total_pm25_tonnes.toFixed(4)} tonnes)  pollution (PM₂.₅) per year
        <br>${getToolTip(infoDict['pm2'])}</div`;
    }
    
    infoBox.innerHTML = htmlOut;


//How Much CO2 Does A Tree Absorb?
        //average value of 10 kilograms/22 pounds per tree per year
    //https://onetreeplanted.org/blogs/stories/how-much-co2-does-tree-absorb?utm_source=chatgpt.com

    /*
    Tree Density
    City trees per hectare
    https://wfpquantum.s3.amazonaws.com/pdf/2021/63937_State%20of%20the%20Urban%20Forest%20April%202021.pdf?utm_source=chatgpt.com
    
    City trees per hectare
    < 25; 26–50; 51-75; 76-100; >100
    */
    
    /*
    Air Quality
    AQI
    https://en.wikipedia.org/wiki/Air_quality_index?utm_source=chatgpt.com
    i‑Tree Eco estimates pollutant removal (PM₂.₅, NO₂, O₃, SO₂, CO), expressed in grams per m² of canopy or kg per hectare per year, using local weather and air data
    
    1 urban tree removes on average:
    0.015 kg (15 g) PM₂.₅ per year
    One hectare of U.S.
    urban tree cover averages about 67 kg of pollution removal per year (Nowak
    et al. 2014)
https://www.itreetools.org/documents/560/i-Tree_Canopy_Air_Pollutant_Removal_and_Monetary_Value_Model_Descriptions.pdf

    1 hectare of healthy tree canopy can remove ≈ 4.7 kg of PM2.5 per year
    (source: i-Tree Eco model, US Forest Service)
    https://www.itreetools.org/documents/389/Reporte_Intec.pdf?utm_source=chatgpt.com
    https://www.nps.gov/articles/000/uerla-trees-air-pollution.htm?utm_source=chatgpt.com

    That’s about:
    ~12.9 g/m²/year
    */
}


// Get map view and map view selection
const baseLayers = {
  satellite: L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
      attribution: 'Tiles © Esri',
      maxZoom: 19 
    }
  ),
  streets: L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19 
    }
  ),
  terrain: L.tileLayer(
    "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
      attribution: '© OpenTopoMap contributors',
      maxZoom: 17 // 👈 prevent requests to non-existent zoom 18+
    }
  )
};


const map = L.map("map", {
        center: [34.156113, -118.131943],
        zoom: 13,
        zoomControl: true, 
        editable: true, // Required for Leaflet.Editable
    });

let toolon = "blocks"; // default
let polygonLayer = null;
let selectedLayer = null; // Track clicked layer
let selectedBlockFeature = null;
let isPointerOnSidebar = false;
let selectionRect = null;    
let boxInfo = {}; 
const sidebar = document.getElementById('sidebar');
const infoBox = document.getElementById('infoBox');
const legend = document.getElementById('legend');
const modelMenu = document.getElementById("modelMenu");

const activeModels = new Set();

const modelData = {
    "baseline": {
        densityMap: null,
        trees: null,
        type: "pt",
        color: "#fa1d6eff",
        size: 3,
        layer: null,
        label: "Detected Tree Points",
        tooltip: "Model iniciated with VGG16 Fully Convolutional Network. Foundational for detecting tree locations to support further canopy analysis. "
    },

    
    "training": {
        densityMap: null,
        trees: null,
        type: "pt",
        size: 3,
        color: "#4842f5",
        layer: null,
        label: "Public Tree Inventory",
        tooltip: "Training dataset with labeled street trees provided by the city of Pasadena. This data is the limited, public-facing data set of the City's public tree inventory"

    },

    "deepforest":{
        densityMap: null,
        trees: null,
        type: "box",
        size: 3,
        color: "#59fff1",
        layer: null,
        label: "Canopy Detection",
        tooltip: "Detected trees using deepForest Detecting model merging overlapped boxes on 60cm/pixel images"
    }

    /*
    "deepforest": {
        densityMap: null,
        trees: null,
        type: "box",
        size: 3,
        color: "#f3f7cb",
        layer: null,
        label: "Canopy Boxes (DeepForest)",
        tooltip: "Detected trees using deepForest Detecting model on 60cm/pixel images"
    },
    "deepforest10cm": {
        densityMap: null,
        trees: null,
        type: "box",
        size: 3,
        color: "#ac3bf7",
        layer: null,
        label: "Deep Forest 10cm",
        tooltip: "Detected trees using deepForest Detecting model on 10cm/pixel images"
    },
    //"deepforest10cm-merged": {
    "deepforest10cmMerged":{
        densityMap: null,
        trees: null,
        type: "box",
        size: 3,
        color: "#59fff1",
        layer: null,
        label: "Deep Forest Merged",
        tooltip: "Detected trees using deepForest Detecting model merging overlapped boxes on 10cm/pixel images"
    },
    "cv60cm": {
        densityMap: null,
        trees: null,
        type: "pt",
        size: 3,
        color: "#ff386d",
        layer: null,
        label: "CV enhanced 60cm",
        tooltip: "Model using computer vision enhanced images(60cm/pixel)"
    }
        */

};

function buildModelMenuHtml() {
    const modelOrder = [
        "training",
        "baseline",
        "cv60cm",
        "deepforest",
        "deepforest10cm",
        "deepforest10cmMerged"
    ];

    let html = "";

    modelOrder.forEach(key => {
        const model = modelData[key];
        if (!model) return;

        html += `
        <div class="label-row">
            <label>
                <input type="checkbox" name="model" value="${key}" ${key === "training" ? 'checked="checked"' : ""}>
                 ${model.label}
            </label>
            ${getToolTip(model.tooltip) || ""}
            <span class="model-loading-text"></span>
            <span class="model-symbol"></span>
        </div>`;
    });

    modelMenu.innerHTML = html;
}
buildModelMenuHtml();

document.querySelectorAll('input[name="mapView"]').forEach(input => {
    input.addEventListener('change', (e) => {
        const selected = e.target.value;

        // Remove all other base layers
        Object.values(baseLayers).forEach(layer => {
        if (map.hasLayer(layer)) {
            map.removeLayer(layer);
        }
        });

        // Add the selected one
        baseLayers[selected].addTo(map);
        if (selected === 'terrain' && map.getZoom() > 17) {
            map.setZoom(17);
  }

    });
});



const DENSITY_COLORS = [
  '#fc9d30',  // lowest
  '#fcf347',
  '#b7fc47',
  '#6af73b',
  '#29ba3a',
  '#198a2c',
  '#035112ff',
  '#0c2e13'   // highest
];

let densityBreaks = []; 

function genDensityColor(breaks) {
  return function (d) {
    density = Math.ceil(d);
    for (let i = breaks.length - 1; i >= 0; i--) {
      if (density > breaks[i]) return DENSITY_COLORS[i+1];
    }
    return DENSITY_COLORS[0];
  };
}

function getDensityColor(d) {
  const density = Math.ceil(d);
  for (let i = densityBreaks.length - 1; i >= 0; i--) {
    if (density > densityBreaks[i]) return DENSITY_COLORS[i + 1];
  }
  return DENSITY_COLORS[0];
}

function getDynamicBreaks(densities) {
    if (!densities.length) return { breaks: [], min: 0, max: 0 };

    const sorted = densities.slice().sort((a, b) => a - b);

    // Remove outliers (e.g. 2.5% trim on both ends)
    const trimPercent = 0.008;
    const start = Math.floor(sorted.length * trimPercent);
    const end = Math.ceil(sorted.length * (1 - trimPercent));
    const trimmed = sorted.slice(start, end);

    const rawMin = trimmed[0];
    const rawMax = trimmed[trimmed.length - 1];
    // Round min down, max up to multiple of 5
    let min = rawMin;
    let max = rawMax;
    if (max > 40)
    {
        min = Math.floor(rawMin / 5) * 5;
        max = Math.ceil(rawMax / 5) * 5;
    }

    const fullRange = max - min;
    const approxStep = Math.round(fullRange / DENSITY_COLORS.length);

    // Round step down to nearest multiple of 
    let step = approxStep;
    if (max > 40){
        step = Math.max(5, Math.floor(approxStep / 5) * 5);
    }
    const breaks = [];
    for (let i = 1; i < DENSITY_COLORS.length; i++) {
        breaks.push(min + i * step);
    }

    return { breaks, min, max: min + step * DENSITY_COLORS.length };
}

function addLegend() {
    const grades = [0, 1, 5, 10, 15, 20, 25];  // Manual bins
    let html = `<strong>Tree Density <br>in census block<br>(trees/ha)</strong><br><br>`;
    for (let i = grades.length - 1; i >= 0; i--) {
        const from = grades[i];
        const to = grades[i + 1];
        const label = to ? `${from}-${to}` : `> ${from}`;
        html += `
        <div>
            <span style="background:${getDensityColor(from)}"></span>${label}
        </div>`;
    }
    legend.innerHTML = html;
}

function genLegend(min, max, breaks) {
    const legend = document.getElementById("legend");
    if (!legend) return;

    let html = `<strong>Census Blocks<br>Tree Density<br>(trees/ha)</strong><br><br>`;
    const range = [min, ...breaks, max];

    for (let i = 0; i < DENSITY_COLORS.length; i++) {
        const from = range[i];
        const to = range[i + 1] - 1;
        let label = `${from.toFixed(0)}.00 - ${to.toFixed(0)}.99`;
        if (i === DENSITY_COLORS.length - 1)
        label = `> ${from.toFixed(0) - 1}.00`;

        const color = DENSITY_COLORS[i];

        html += `
        <div>
            <span style="background:${color}; border: 1px solid #ccc;"></span>
            ${label}
        </div>`;
    }

    legend.innerHTML = html;
}

function initSideBar(){   
    sidebar.addEventListener('mouseenter', () => {
        isPointerOnSidebar = true;
    });

    sidebar.addEventListener('mouseleave', () => {
        isPointerOnSidebar = false;
    });
}

function ShapeOptions(feature) {
  const density = feature.properties.density || 0; // if already computed
  //alert(density);
    //const factor = (3 - 1) / (26 - 1);
    //if (density >= 70){alert(getDensityColor(density));}
  return {
    
    fillColor: getDensityColor(density),
    //fillColor: interpolateColor('#0d3614', '#c98422', factor),
    weight: 1,
    color: "#888",
    fillOpacity: 0.5
  };
}

const hoverStyle = {
    color: "#fff",
    weight: 3,
    fillOpacity: 0.5
};

const clickBorderStyle = {
    weight: 2,
    color: "#fff", 
    fillOpacity: 0.5
};

const blankBlock = {
    fillColor: "#b8fca7",
    color: "#888",
    weight: 1,
    fillOpacity: 0.3
};

function createCircleMarker(feature, latlng) {
    const model = feature.properties.model;
    const modelStyle = modelData[model];

    const size = modelStyle.size || 2;
    const color = modelStyle.color || "#cccccc";

    return L.circleMarker(latlng, {
        radius: size,
        fillColor: color,
        color: "#333333",
        weight: 0.5,
        opacity: 1,
        fillOpacity: 1
    });
}

function removeCircleMarker(){
    map.eachLayer(function (l) {
        if (l instanceof L.CircleMarker) {
            map.removeLayer(l);
        }
    });
}


/****  Starting the section to create sensus blocks as the foundation of the map *****/
function initBlocks(){
    polygonLayer = L.geoJSON(census_block, {
        style: blankBlock,  // initial neutral style, will be updated dynamically
        onEachFeature: (feature, layer) => {
            layer.on('click', () => {
                if (toolon !== "blocks") return;

                if (selectedLayer && selectedLayer !== layer) {
                    selectedLayer.setStyle(
                        activeModels.size === 0
                            ? blankBlock
                            : ShapeOptions(selectedLayer.feature)
                    );
                }

                layer.setStyle(clickBorderStyle);
                selectedLayer = layer;
                selectedBlockFeature = feature;
                showTrees(feature); 
            });

            layer.on('mouseover', () => {
                if (toolon !== "blocks") return;
                if (layer !== selectedLayer) {
                    layer.setStyle(
                        activeModels.size === 0 ? blankBlock : hoverStyle
                    );
                }
            });

            layer.on('mouseout', () => {
                if (toolon !== "blocks") return;
                if (layer !== selectedLayer) {
                    layer.setStyle(
                        activeModels.size === 0
                            ? blankBlock
                            : ShapeOptions(feature)
                    );
                }
            });
        }
    }).addTo(map);
}

function getFilteredPolygons(data, features, model) {
    if (!features || features.length === 0) return null;

    const featureCollection = {
        type: "FeatureCollection",
        features: features
    };

    data.layer = L.geoJSON(featureCollection, {
        style: function(feature) {
            const modelStyle = modelData[model];
            return {
                color: modelStyle.color,
                weight: modelStyle.size || 2,
                fillOpacity: 0.1
            };
        }
    }).addTo(map);

    return featureCollection;
}

let activeTooltipBubble = null;
 
/* The showTrees function works only on sensus block since it is using the blocks as the base */
async function showTrees(blockFeature) {
    // Only run if current tool is "blocks" and block is selected
    if (toolon !== "blocks" || !selectedLayer) {
        return;
    }


    // If no models are active, don't draw anything
    if (activeModels.size === 0) return;

    const blockPolygon = turf.feature(blockFeature.geometry);
    const blockID = blockFeature.properties.OBJECTID;
    
    const response = await fetch(serverName + "/api/get_filtered_trees", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            models: Array.from(activeModels),
            blockID: blockID
        })
    });

    const result = await response.json();

    if (activeTooltipBubble) {
        activeTooltipBubble.remove();
        activeTooltipBubble = null;
    }
    // Remove all previous filtered layers for active models
    activeModels.forEach(model => {
        const data = modelData[model];
        if (data.layer && map.hasLayer(data.layer)) {
            map.removeLayer(data.layer);
            data.layer = null;
        }
    });

    if (result.error === "bigArea") {
      // Show tooltip bubble for large area message
      if (!activeTooltipBubble) {
        const centroid = turf.centroid(blockFeature.geometry);
        const latlng = L.latLng(centroid.geometry.coordinates[1], centroid.geometry.coordinates[0]);
        const point = map.latLngToContainerPoint(latlng);

        const bubble = document.createElement("div");
        bubble.className = "tooltip-bubble";
        bubble.innerHTML = infoDict['largeArea'] || "Selected area is too large.";
        bubble.style.display = "block";

        Object.assign(bubble.style, {
          position: "absolute",
          left: `${point.x}px`,
          top: `${point.y}px`,
          zIndex: 10000,
          maxWidth: "250px"
        });

        map.getContainer().appendChild(bubble);
        activeTooltipBubble = bubble;
      }
      return;
    }

    let combinedFeatures = []; 
    activeModels.forEach(model => {
        const data = modelData[model];
        if (!data) return;

        const filteredFeatures = result[model]["features"];
        if (!filteredFeatures || filteredFeatures.length === 0) return;

        filteredFeatures.forEach(f => {
            f.properties.model = model;
        });

        if (data.type === "pt") {
            data.layer = L.geoJSON({ type: "FeatureCollection", features: filteredFeatures }, {
                pointToLayer: createCircleMarker
            }).addTo(map);
        } else if (data.type === "box" || data.type === "merged") {
            //data.layer = L.geoJSON({ type: "FeatureCollection", features: filteredFeatures }).addTo(map);
            
            const filteredGeoJSON = getFilteredPolygons(data, filteredFeatures, model);
            //data.layer = L.geoJSON(filteredGeoJSON).addTo(map);
        }

        combinedFeatures = combinedFeatures.concat(filteredFeatures);
    });

    const combinedFeatureCollection = {
        type: "FeatureCollection",
        features: combinedFeatures
    };

    updateInfoBox(blockFeature, combinedFeatureCollection, activeModels.size);

}

async function updatePolygonStyle() {
    const numModels = activeModels.size;
    if (numModels === 0) {
        // No models selected, reset styles
        polygonLayer.setStyle(blankBlock);
        return;
    }
    
    document.getElementById("loading").style.display = "Calculating...";
    try {
        // Send active model list to server and get back density data per OBJECTID
        const response = await fetch(serverName + "/api/get_density", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ models: Array.from(activeModels) })
        });
        if (!response.ok) throw new Error("Failed to fetch density data");

        const densityData = await response.json(); 
        // densityData should be an object like { OBJECTID1: density1, OBJECTID2: density2, ... }

        // Update each polygon layer density property and style
        const layers = polygonLayer.getLayers();
        const allDensities = [];
        let maxD = 0;

        layers.forEach(layer => {
            const objectId = layer.feature.properties.OBJECTID;
            const density = densityData[objectId] || 0;
            layer.feature.properties.density = density;
            allDensities.push(density);
            if (density > maxD) maxD = density;
        });

        
        const { breaks, min, max } = getDynamicBreaks(allDensities);
        densityBreaks = breaks;  // global breaks for reuse
        getDensityColor = genDensityColor(breaks);
        //alert(getDensityColor);
        polygonLayer.setStyle(ShapeOptions); // uses global getDensityColor
        genLegend(min, max, densityBreaks, getDensityColor);

    } catch (error) {
        console.error(error);
        alert("Error loading density data.");
    } finally {
        document.getElementById("loading").style.display = "none";
    }
}


/****  Start the section for 100 Acre and stree view tool to show trees with tool selection ****/
async function updateVisiblePoints() {
    if (!selectionRect || (toolon !== "rectangle" && toolon !== "street")) {
        // No selection rectangle or wrong tool
        activeModels.forEach(model => {
            const data = modelData[model];
            if (data.layer && map.hasLayer(data.layer)) {
                map.removeLayer(data.layer);
                data.layer = null;
            }
        });
        return;
    }

    const rectBounds = selectionRect.getBounds();
    const turfPoly = turf.polygon([[
        [rectBounds.getWest(), rectBounds.getSouth()],
        [rectBounds.getEast(), rectBounds.getSouth()],
        [rectBounds.getEast(), rectBounds.getNorth()],
        [rectBounds.getWest(), rectBounds.getNorth()],
        [rectBounds.getWest(), rectBounds.getSouth()]
    ]]);

    // POST polygon and models to server
    const response = await fetch(serverName + "/api/get_filtered_trees", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            polygon: turfPoly,
            models: Array.from(activeModels)
        })
    });

    if (!response.ok) {
        console.error("Server error:", await response.text());
        return;
    }

    const result = await response.json();
    // Remove previous layers
    activeModels.forEach(model => {
        const data = modelData[model];
        if (data.layer && map.hasLayer(data.layer)) {
            map.removeLayer(data.layer);
            data.layer = null;
        }
    });

    if (activeModels.size === 0) return;
    let combinedFeatures = []; 

    activeModels.forEach(model => {
        const data = modelData[model];
        if (!data) return;

        const filteredFeatures = result[model]["features"];
        if (!filteredFeatures || filteredFeatures.length === 0) return;

        filteredFeatures.forEach(f => {
            f.properties.model = model;
        });

        if (data.type === "pt") {
            data.layer = L.geoJSON({ type: "FeatureCollection", features: filteredFeatures }, {
                pointToLayer: createCircleMarker
            }).addTo(map);
        } else if (data.type === "box" || data.type === "merged") {
            //data.layer = L.geoJSON({ type: "FeatureCollection", features: filteredFeatures }).addTo(map);
            
            const filteredGeoJSON = getFilteredPolygons(data, filteredFeatures, model);
            //data.layer = L.geoJSON(filteredGeoJSON).addTo(map);
        }

        combinedFeatures = combinedFeatures.concat(filteredFeatures);
    });

    const combinedFeatureCollection = {
        type: "FeatureCollection",
        features: combinedFeatures
    };

    updateInfoBox(turfPoly, combinedFeatureCollection, activeModels.size);
}

    

function genMapViewRect() {
    if (selectionRect) {
        map.removeLayer(selectionRect);
    }
    const bounds = map.getBounds();
    selectionRect = L.rectangle(bounds); // Not added to map
}



const MAX_WIDTH = 0.02;  // degrees
const MAX_HEIGHT = 0.02; // degrees

function genRec(center) {
    const offsetLat = 0.00286;  // ≈ 317 meters
    const offsetLng = 0.00345;  // ≈ 317 meters

    const bounds = L.latLngBounds(
        [center.lat - offsetLat, center.lng - offsetLng],
        [center.lat + offsetLat, center.lng + offsetLng]
    );

    // Update existing rectangle
    if (selectionRect) {
        selectionRect.setBounds(bounds);
    } else {
        selectionRect = L.rectangle(bounds, {
            color: '#fff',
            weight: 3,
            fillOpacity: 0.1,
            draggable: true
        }).addTo(map);

        selectionRect.dragging.enable();
        selectionRect.on('dragend', () => {updateVisiblePoints();});
        selectionRect.on("editable:dragend", updateVisiblePoints);

        // Minimal fallback:
        map.on("zoomend", updateVisiblePoints); // Update on zoom if dragging isn't available
    }
}
function onMapMoveOrZoom() {
    genMapViewRect();
    updateVisiblePoints();
}

function waitForZoomThenRun(targetZoom, callback) {
  if (map.getZoom() !== targetZoom) {
    map.once("zoomend", callback);
    map.setZoom(targetZoom);
  } else {
    callback(); // already at target zoom, just run it
  }
}

function onMapClickRectangle(e) {
    if (toolon !== "rectangle") return;
    const sidebar = document.getElementById('sidebar');
    const infoBox = document.getElementById('infoBox');
    const target = e.originalEvent.target;

    if ((sidebar && sidebar.contains(target)) ||
        (infoBox && infoBox.contains(target))) {
        return;
    }

    const center = e.latlng;
    genRec(center);
    updateVisiblePoints();
}

/* functions to handle tool change */
function handleToolChange(tool) {
    removeCircleMarker();
    toolon = tool
    // Remove existing rectangle
    if (selectionRect) {
        map.removeLayer(selectionRect);
        selectionRect = null;
    }

    // Remove old click handler
    map.off("zoomend", onMapMoveOrZoom);
    map.off("moveend", onMapMoveOrZoom);

    if (toolon !== "blocks" && selectedLayer) {
        selectedLayer.setStyle(ShapeOptions(selectedLayer.feature));
        selectedLayer = null;
    }

    if (tool === 'blocks') {
        const center = [34.156113, -118.131943];
        map.zoomControl.enable(); 
        map.options.minZoom = 0;
        map.options.maxZoom = 24;

        
        map.on("zoomend", () => {
            if (isPointerOnSidebar) return;  // Ignore if over sidebar
            if (toolon === "blocks" && selectedLayer) {
                showTrees(selectedLayer.feature);
            }
        });

        map.on("moveend", () => {
            if (isPointerOnSidebar) return;  // Ignore if over sidebar
            if (toolon === "blocks" && selectedLayer) {
                showTrees(selectedLayer.feature);
            }
        });
        //map.setView(center, 13);
        updateVisiblePoints()
    } 
    else if (tool === 'rectangle') {
        map.setZoom(15);
        map.zoomControl.enable();
        map.options.minZoom = 0;
        map.options.maxZoom = 24;

        const center = map.getCenter();
        genRec(center);
        updateVisiblePoints();

        // Remove any previous zoom listener and re-add
        map.off("zoomend", updateVisiblePoints);
        map.on("zoomend", updateVisiblePoints);

        // Remove any previous click listener for rectangle tool and re-add
        map.off("click", onMapClickRectangle);
        map.on("click", onMapClickRectangle);
    }
    else if (tool === "street") {
        const fixedZoom = 18;
        map.zoomControl.disable();
        map.options.minZoom = fixedZoom;
        map.options.maxZoom = fixedZoom;

        waitForZoomThenRun(fixedZoom, () => {
            genMapViewRect();         // now safe to generate selection
            onMapMoveOrZoom();        // update visible points
            map.on("moveend", onMapMoveOrZoom); // bind dynamic update
        });
    }

    if (tool === 'blocks' && selectedBlockFeature) {
        showTrees(selectedBlockFeature); // re-render tree points inside block
    }

}

/***  this section handels model change  
 * First load/get model data into indexDB
 * add/remove model layer
 * update polygon
 * ***/

function addModelLayer(model) {
    
    const data = modelData[model];
    if (!data) return;

    if (activeModels.has(model)) return;
    
    activeModels.add(model);
    
    // If current tool is "blocks" and a block is selected, update trees
    if (toolon === "blocks" && selectedLayer) {
        showTrees(selectedLayer.feature);
    }

    updatePolygonStyle()
}

function removeModelLayer(model) {
    
    const data = modelData[model];
    if (!data) return;
    
    activeModels.delete(model);

    if (data.layer && map.hasLayer(data.layer)) {
        map.removeLayer(data.layer);
        data.layer = null;
    }

    // If current tool is "blocks" and a block is selected, update trees
    if (toolon === "blocks" && selectedLayer) {
        showTrees(selectedLayer.feature);
    }
    updatePolygonStyle()
}


async function loadingModel() {
  const db = await openDB();
  const modelKeys = Object.keys(modelData);
  let completed = 0;

    for (const modelKey of modelKeys) {
        const row = document.querySelector(`.label-row input[value="${modelKey}"]`)?.closest('.label-row');
        if (!row) continue;

        const spanLoading = row.querySelector(".model-loading-text");
        const checkbox = row.querySelector("input");
        const symbol = row.querySelector(".model-symbol");
        const data = modelData[modelKey];

        if (!checkbox || !spanLoading || !symbol || !data) continue;

        // Show loading
        spanLoading.textContent = " (loading...)";
        checkbox.disabled = true;

        // Update the symbol (regardless of model loaded or not)
        symbol.style.width = `${data.size * 4}px`;
        symbol.style.height = `${data.size * 4}px`;
        symbol.style.borderRadius = data.type === "pt" ? "50%" : "0";
        symbol.style.backgroundColor = data.color;
        symbol.style.border = '1px solid #333';


        loadModelScriptWithCache(modelKey, db).then(m => {
        console.log(`Model ${m} loaded`);

        if (modelKey === "training") {
            document.querySelector('input[name="tool"][value="blocks"]').checked = true;
            const trainingCheckbox = document.querySelector('input[name="model"][value="training"]');
            trainingCheckbox.checked = true;
            trainingCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
        }

        spanLoading.textContent = "";
        checkbox.disabled = false;

        }).catch(err => {
        console.error(err);
        spanLoading.textContent = " (failed)";
        }).finally(() => {
            completed++;
            const percent = Math.round((completed / modelKeys.length) * 100);
            const globalLoader = document.querySelector("#map #loading");
            if (globalLoader) globalLoader.textContent = `Loading models... ${percent}%`;

            if (completed === modelKeys.length) {
                if (globalLoader) globalLoader.remove();
            }
        });
    }
}

function toggleTooltip(iconEl) {
  const bubble = iconEl.nextElementSibling;

  if (!bubble) return;

  // Close any other open tooltips
  document.querySelectorAll('.tooltip-bubble').forEach(el => {
    if (el !== bubble) el.style.display = 'none';
  });

  // Toggle current one
  bubble.style.display = (bubble.style.display === 'block') ? 'none' : 'block';
}



function processLoadingDoc(){
    window.addEventListener('DOMContentLoaded', () => {
        const groups = ["model", 'tool', 'mapView'];

        groups.forEach(name => {
            const radios = document.querySelectorAll(`input[name="${name}"]`);
            radios.forEach(radio => (radio.checked = false)); // Clear all first

            // Find the one with checked attribute in HTML and set checked true to force sync
            const defaultRadio = document.querySelector(`input[name="${name}"][checked]`);
            if (defaultRadio) {
                defaultRadio.checked = true;
            }
        });
        
        // Load initial dataset
        map.setZoom(13);
        baseLayers.satellite.addTo(map); // default view


        document.querySelectorAll('input[name="model"]').forEach(cb => {

            const model = cb.value;
            const row = document.querySelector(`.label-row input[value="${model}"]`)?.closest('.label-row');
            const symbol = row.querySelector(".model-symbol");

            const data = modelData[model];
            if (data && symbol ) {          
                symbol.style.width = `${data.size * 4}px`;
                symbol.style.height = `${data.size * 4}px`;
                symbol.style.borderRadius = data.type === "pt" ? "50%" : "0";
                symbol.style.backgroundColor = data.color;
                symbol.style.border = '1px solid #333';
            }

            cb.addEventListener('change', function () {
                const model = this.value; // "training", "baseline", or "deepforest"
                
                if (this.checked) {
                    addModelLayer(model);
                } else {
                    removeModelLayer(model);
                }
                if (activeModels.size === 0){
                    document.getElementById("infoBox").innerHTML = infoBoxDefaultHTML;
                }
                // Update visible points if tool is rectangle or streetMore actions
                if (toolon === "rectangle" || toolon === "street") {
                    //alert("here")
                    updateVisiblePoints();
                }
                // Also handle blocks tool if needed
                if (toolon === "blocks" && selectedBlockFeature) {
                    showTrees(selectedBlockFeature);
                }
            });

            if (modelData && modelData["training"]) {
                document.querySelector('input[name="tool"][value="blocks"]').checked = true;
                const trainingCheckbox = document.querySelector('input[name="model"][value="training"]');
                trainingCheckbox.checked = true;
                trainingCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    });

    // Automatically toggle when radio button changes
    document.querySelectorAll('input[name="tool"]').forEach(input => {
        input.addEventListener('change', (e) => {
                handleToolChange(e.target.value);
        });
    });


    const blocksTool = document.querySelector('input[name="tool"][value="blocks"]');
    if (blocksTool) {
        blocksTool.checked = true;
        blocksTool.dispatchEvent(new Event('change', { bubbles: true }));
    }
    document.getElementById("infoBox").innerHTML = infoBoxDefaultHTML;
    map.doubleClickZoom.disable();
    handleToolChange(document.querySelector('input[name="tool"]:checked').value);

    const app = document.getElementById('app');

    app.addEventListener('wheel', function(event) {
        event.preventDefault();  // Prevent page scroll on wheel inside #app
    }, { passive: false });

    const appSection = document.getElementById('app');

    appSection.addEventListener('wheel', (e) => {
    e.preventDefault(); // Prevent the page from scrolling

    // Manually zoom the Leaflet map (assuming your map instance is `map`)
    if (e.deltaY < 0) {
        map.zoomIn();
    } else {
        map.zoomOut();
    }
    }, { passive: false });
            
}

window.addEventListener("load", function () {
  const hash = window.location.hash;
  if (hash) {
    // Delay scroll slightly to ensure everything is rendered
    setTimeout(() => {
      const target = document.querySelector(hash);
      if (target) {
        target.scrollIntoView({ behavior: "auto", block: "start" });
      }
    }, 100); // You can tweak the delay
  }
});


