const infoBoxDefaultHTML = `
  <h4>Tree Benefits</h4>
  <div class="infoText"><b>How Much CO2 Does A Tree Absorb?</b></div>
  <div class="infoText">On average, each tree absorbs 10 kilograms/22 pounds of CO2 per year</div>
  <hr>
  <div class="infoText"><b>How much pollutant (PM₂.₅) can a tree remove?</b></div>
  <div class="infoText">An urban tree removes 0.015 kg (15 g) PM₂.₅ pollutant per year</div>
`;

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

const activeModels = new Set();

const modelData = {
    "baseline": {
        polygon: null,
        trees: null,
        type: "pt",
        color: "#f7b283",
        size: 3,
        layer: null  // add this!
    },
    "training": {
        polygon: null,
        trees: null,
        type: "pt",
        size: 3,
        color: "#7dc7ff",
        layer: null
    },
    "deepforest": {
        polygon: null,
        trees: null,
        type: "box",
        size: 3,
        color: "#f3f7cb",
        layer: null
    },
    "deepforest10cm": {
        polygon: null,
        trees: null,
        type: "box",
        size: 3,
        color: "#ac3bf7",
        layer: null
    },
    "cv60cm": {
        polygon: null,
        trees: null,
        type: "pt",
        size: 3,
        color: "#ff386d",
        layer: null
    }
};

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
function updateInfoBox(feature, selectedPoints, numModel) {
  const areaSqMeters = turf.area(feature);
  const areaAcres = areaSqMeters / 4046.8564224;
  const hectare = areaAcres / 2.47105;

  let avgDensity, avgTreeCount;

  const objectId = feature.properties?.OBJECTID;

  if (objectId !== undefined) {
    // ✅ Block-based: use average polygon densities
    let totalDensity = 0;
    let count = 0;

    activeModels.forEach(model => {
      const features = modelData[model].polygon.features;
      const match = features.find(f => f.properties.OBJECTID === objectId);
      if (match && typeof match.properties.density === "number") {
        totalDensity += match.properties.density;
        count++;
      }
    });

    avgDensity = count > 0 ? totalDensity / count : 0;
    avgTreeCount = avgDensity * hectare;

  } else {
    // ✅ Free-form: use raw point counts
    const pointCount = selectedPoints.features.length / numModel;
    avgTreeCount = pointCount;
    avgDensity = pointCount / hectare;
  }

  // Build output
  let htmlOut = `<h4>Selected Area</h4>`;
  htmlOut += `<div class="infoText">Area: ${areaAcres.toFixed(0)} Acre<br>`;
  htmlOut += `Model Selected: ${numModel}<br>`;
  htmlOut += `Avg Tree Count: ${avgTreeCount.toFixed(0)}<br>`;
  htmlOut += `Density: ${avgDensity.toFixed(2)} (count/hectare)<br>`;
  htmlOut += `<div><hr></div>`;

  // CO₂ (kg and tonnes)
  const totalCO2_kg = avgTreeCount * 10;
  const totalCO2_tonnes = totalCO2_kg / 1000;
  htmlOut += `<div class="infoText">The selected area absorbed a total of ${totalCO2_kg.toFixed(2)} kg (${totalCO2_tonnes.toFixed(2)} tonnes) CO₂ per year</div>`;
  htmlOut += `<div><hr></div>`;

  // PM2.5 (kg and tonnes)
  const PM25_per_tree_kg = 0.015;
  const total_pm25_kg = avgTreeCount * PM25_per_tree_kg;
  const total_pm25_tonnes = total_pm25_kg / 1000;
  htmlOut += `<div class="infoText">The selected area removed approximately ${total_pm25_kg.toFixed(2)} kg (${total_pm25_tonnes.toFixed(4)} tonnes)  pollution (PM₂.₅) per year</div>`;

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
    */
}

/*
 *  Model select base on GeoJson of the tree points against census blocks
 */

 // color of each census block base on tree density
 /*
function getDensityColor(d) {
  return d > 25  ? '#0c2e13' :
         d > 20  ? '#0e6920' :
         d > 15  ? '#198a2c':
         d > 10  ? '#29ba3a':
         d > 5   ? '#6af73b' :
         d > 1   ? '#b7fc47':
         d > 0   ? '#fcf347':
                   '#fc9d30';
}
*/
const DENSITY_COLORS = [
  '#fc9d30',  // lowest
  '#fcf347',
  '#b7fc47',
  '#6af73b',
  '#29ba3a',
  '#198a2c',
  '#0e6920',
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

  const grades = [0, 1, 5, 10, 15, 20, 25];
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

function genLegend(min, max, breaks, getDensityColor) {
  const legend = document.getElementById("legend");
  if (!legend) return;

  let html = `<strong>Census Blocks<br>Tree Density<br>(trees/ha)</strong><br><br>`;
  const range = [min, ...breaks, max];

  for (let i = 0; i < DENSITY_COLORS.length; i++) {
    const from = range[i];
    const to = range[i + 1]-1;
    let label = `${from.toFixed(0)}.00 - ${to.toFixed(0)}.99`;
    if (i == DENSITY_COLORS.length - 1)
        label = `> ${from.toFixed(0)-1}.00`;

    const color = DENSITY_COLORS[i];

    html += `
      <div>
        <span style="
          background:${color};
          border: 1px solid #ccc;
        "></span>
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
                     
/* The showTrees function works only on sensus block since it is using the blocks as the base */
function showTrees(blockFeature) {
    // Only run if current tool is "blocks" and block is selected
    if (toolon !== "blocks" || !selectedLayer) {
        return;
    }

    // Remove all previous filtered layers for active models
    activeModels.forEach(model => {
        const data = modelData[model];
        if (data.layer && map.hasLayer(data.layer)) {
            map.removeLayer(data.layer);
            data.layer = null;
        }
    });


    // If no models are active, don't draw anything
    if (activeModels.size === 0) return;

    const blockPolygon = turf.feature(blockFeature.geometry);

    let combinedFeatures = []; 

    activeModels.forEach(model => {
        const data = modelData[model];
        if (!data || !data.trees) return;

        let filteredGeoJSON = null;

        if (data.type === "pt") {
            const filtered = turf.pointsWithinPolygon(data.trees, blockPolygon);
            if (filtered.features.length === 0) return;

            // Inject model name
            filtered.features.forEach(f => {
                f.properties.model = model;
            });

            filteredGeoJSON = filtered;

            data.layer = L.geoJSON(filteredGeoJSON, {
                pointToLayer: createCircleMarker
            }).addTo(map);

        } else if (data.type === "box") {
            const centroids = {
                type: "FeatureCollection",
                features: data.trees.features.map(feature => {
                    const center = turf.centroid(feature);
                    center.properties.parent = feature;
                    return center;
                })
            };

            const filteredPoints = turf.pointsWithinPolygon(centroids, blockPolygon);
            if (filteredPoints.features.length === 0) return;

            const filteredPolygons = {
                type: "FeatureCollection",
                features: filteredPoints.features.map(f => {
                    const poly = f.properties.parent;
                    poly.properties.model = model;  // Inject model here
                    return poly;
                })
            };


            filteredGeoJSON = filteredPolygons;

            data.layer = L.geoJSON(filteredGeoJSON, {
                style: function(feature) {
                    const model = feature.properties.model;
                    const modelStyle = modelData[model];
                    return {
                        color: modelStyle.color,
                        weight: modelStyle.size || 2,
                        fillOpacity: 0.1
                    };
                }
            }).addTo(map);
        }// if box
        combinedFeatures = combinedFeatures.concat(filteredGeoJSON.features);
        
    });


    const combinedFeatureCollection = {
        type: "FeatureCollection",
        features: combinedFeatures
    };

    updateInfoBox(blockFeature, combinedFeatureCollection, activeModels.size);
}

function updatePolygonStyle() {
    const numModels = activeModels.size;

    if (numModels === 0) {
        // No models selected, reset styles
        polygonLayer.setStyle(blankBlock);
        return;
    }
    const layers = polygonLayer.getLayers();
    const allDensities = [];
    let maxD = 0;
    //activeModels.forEach(model => {alert(model)});
    layers.forEach(layer => {
        const objectId = layer.feature.properties.OBJECTID;
        if (objectId === undefined) {
            console.warn("Feature missing OBJECTID:", layer.feature);
            return;
        }

        let totalDensity = 0;
        let count = 0;

        activeModels.forEach(model => {
            const modelFeatures = modelData[model].polygon.features;
            const matchingFeature = modelFeatures.find(f => f.properties.OBJECTID === objectId);
            if (matchingFeature && typeof matchingFeature.properties.density === "number") {
                totalDensity += matchingFeature.properties.density;
                count++;
            }
        });

        const avgDensity = count > 0 ? totalDensity / count : 0;
        layer.feature.properties.density = avgDensity;
        if (avgDensity > maxD){ maxD = avgDensity;};
        allDensities.push(avgDensity); 
    });


    const { breaks, min, max } = getDynamicBreaks(allDensities);
    densityBreaks = breaks;  // global breaks for reuse
    getDensityColor = genDensityColor(breaks);
    //alert(getDensityColor);
    polygonLayer.setStyle(ShapeOptions); // uses global getDensityColor
    genLegend(min, max, densityBreaks, getDensityColor);


    //polygonLayer.setStyle(feature => ShapeOptions(feature, getDensityColor));
    //genLegend(allDensities, breaks, getDensityColor);
}


/****  Start the section for 100 Acre and stree view tool to show trees with tool selection ****/
function updateVisiblePoints() {
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

    // Remove previous layers
    activeModels.forEach(model => {
        const data = modelData[model];
        if (data.layer && map.hasLayer(data.layer)) {
            map.removeLayer(data.layer);
            data.layer = null;
        }
    });

    if (activeModels.size === 0) return;

    let combinedFeatures = [];  // top of function
    activeModels.forEach(model => {
        const data = modelData[model];
        if (!data || !data.trees) return;

        let filteredGeoJSON = null;

        if (data.type === "pt") {
            const filtered = {
                type: "FeatureCollection",
                features: data.trees.features.filter(pt =>
                    turf.booleanPointInPolygon(pt, turfPoly)
                )
            };

            if (filtered.features.length === 0) return;

            filtered.features.forEach(f => {
                f.properties.model = model;
            });

            filteredGeoJSON = filtered;

            data.layer = L.geoJSON(filteredGeoJSON, {
                pointToLayer: createCircleMarker
            }).addTo(map);

        } else if (data.type === "box") {
            const centroids = {
                type: "FeatureCollection",
                features: data.trees.features.map(feature => {
                    const center = turf.centroid(feature);
                    center.properties.parent = feature;
                    return center;
                })
            };

            const filteredPoints = turf.pointsWithinPolygon(centroids, turfPoly);
            if (filteredPoints.features.length === 0) return;

            const filteredPolygons = {
                type: "FeatureCollection",
                features: filteredPoints.features.map(f => {
                    const poly = f.properties.parent;
                    poly.properties.model = model;
                    return poly;
                })
            };

            filteredGeoJSON = filteredPolygons;

            data.layer = L.geoJSON(filteredGeoJSON, {
                style: function(feature) {
                    const model = feature.properties.model;
                    const modelStyle = modelData[model];
                    return {
                        color: modelStyle.color,
                        weight: modelStyle.size || 2,
                        fillOpacity: 0.1
                    };
                }
            }).addTo(map);
        }// if box
        combinedFeatures = combinedFeatures.concat(filteredGeoJSON.features);

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
    if (sidebar && sidebar.contains(e.originalEvent.target)) {
        // Click was inside sidebar — ignore
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

function loadModelScript(modelKey) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = `./js/${modelKey}.js`; // your file should be named like cv60cm.js etc.
    script.onload = () => {
      try {
        modelData[modelKey].polygon = window[`census_blocks_${modelKey}`];
        modelData[modelKey].trees = window[modelKey];
        resolve(modelKey);
      } catch (err) {
        reject(`Failed to load data for ${modelKey}: ${err}`);
      }
    };
    script.onerror = () => reject(`Failed to load JS for ${modelKey}`);
    document.head.appendChild(script);
  });
}

// === IndexedDB setup ===
async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("ModelStore", 1);

    request.onupgradeneeded = function (event) {
      const db = event.target.result;
      if (!db.objectStoreNames.contains("models")) {
        db.createObjectStore("models", { keyPath: "key" });
      }
    };

    request.onsuccess = (event) => resolve(event.target.result);
    request.onerror = (event) => reject("IndexedDB error: " + event.target.errorCode);
  });
}

async function getModelFromDB(db, key) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction("models", "readonly");
    const store = tx.objectStore("models");
    const request = store.get(key);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function saveModelToDB(db, key, polygon, trees) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction("models", "readwrite");
    const store = tx.objectStore("models");
    const request = store.put({ key, polygon, trees });
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

async function loadModelScriptWithCache(modelKey, db) {
  const cached = await getModelFromDB(db, modelKey);
  if (cached && cached.polygon && cached.trees) {
    // Restore from IndexedDB
    modelData[modelKey].polygon = cached.polygon;
    modelData[modelKey].trees = cached.trees;
    return modelKey;
  } else {
    // Load the script and save data
    return loadModelScript(modelKey).then((loadedKey) => {
      const polygon = modelData[modelKey].polygon;
      const trees = modelData[modelKey].trees;
      return saveModelToDB(db, modelKey, polygon, trees).then(() => loadedKey);
    });
  }
}
async function loadingModel() {
  const db = await openDB();
  const modelKeys = Object.keys(modelData);
  let completed = 0; // ✅ Counter to track completed loads

  for (const modelKey of modelKeys) {
    const label = document.querySelector(`input[value="${modelKey}"]`).parentElement;
    const span = label.querySelector(".model-loading-text");
    const checkbox = label.querySelector("input");

    span.textContent = " (loading...)";
    checkbox.disabled = true;

    loadModelScriptWithCache(modelKey, db).then(m => {
      console.log(`Model ${m} loaded`);

      if (modelKey === "training") {
        document.querySelector('input[name="tool"][value="blocks"]').checked = true;
        const trainingCheckbox = document.querySelector('input[name="model"][value="training"]');
        trainingCheckbox.checked = true;
        trainingCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
      }

      span.textContent = "";
      checkbox.disabled = false;

    }).catch(err => {
      console.error(err);
      span.textContent = " (failed)";
    }).finally(() => {
      // ✅ Increase counter regardless of success or failure
      completed++;
      if (completed === modelKeys.length) {
        const loader = document.querySelector("#map #loading");
        if (loader) loader.remove(); // or loader.style.display = "none";
      }
    });
  }
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
            const span = cb.parentElement.querySelector('.model-symbol');
            const data = modelData[model];
            if (data && span ) {
                span.style.width = `${data.size * 4}px`;
                span.style.height = `${data.size * 4}px`;
                span.style.borderRadius = data.type === "pt" ? "50%" : "0";  // force square corners
                span.style.backgroundColor = data.color;
                span.style.border = '1px solid #333';
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
        });
    });

    // Automatically toggle when radio button changes
    document.querySelectorAll('input[name="tool"]').forEach(input => {
        input.addEventListener('change', (e) => {
                handleToolChange(e.target.value);
        });
    });


    
    document.getElementById("infoBox").innerHTML = infoBoxDefaultHTML;
    map.doubleClickZoom.disable();
    handleToolChange(document.querySelector('input[name="tool"]:checked').value);
    window.onload = function() {
    console.log("Everything (DOM + assets) loaded.");
    };
            
}