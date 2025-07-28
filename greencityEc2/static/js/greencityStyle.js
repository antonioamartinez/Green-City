// street1.jpg - https://wpra.net/1981/01/01/save-the-trees-and-open-spaces/
// street2.jpg, street3.jpg - https://www.altaonline.com/culture/art/a60924832/southern-california-palm-citrus-trees-climate-change/

let baseURL;

if (window.location.protocol === "file:") {
  // Assume relative path for local files
    baseURL = "../";  // or set to a relative path like "../static/assets/img/"
} else {
    baseURL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/`;
}

const sectionHTML = {

"navbarResponsive": `
    <ul class="navbar-nav ms-auto">
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
            About
            </a>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#about">About GreenCity</a></li>
                <li><a class="dropdown-item" href="#about2">Motivation</a></li>
                <li><a class="dropdown-item" href="#about3">Problem</a></li>
            </ul>
        </li>
         <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
            Project
            </a>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#project">Data Source & Dataset</a></li>
                <li><a class="dropdown-item" href="#project2">Detection Models</a></li>
                <li><a class="dropdown-item" href="#project3">Web Application</a></li>
            </ul>
        </li>
        <li class="nav-item"><a class="nav-link" href="#project">Project</a></li>
        <li class="nav-item"><a class="nav-link" href="#app">App</a></li>
        <li class="nav-item"><a class="nav-link" href="#evaluation">Evaluation</a></li>
        <li class="nav-item"><a class="nav-link" href="#signup">Contact</a></li>
    </ul>
`,
"about": `
    <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 1.3)")</script>
    <p class="pageTitle"></p>
    <div class="section-block">
        <span class="section-head"> GreenCity <br>Is A Machine Learning Platform for Urban Tree Canopy Monitoring & Green Equity</span>
        <div class="section-text">
            A Story of Data, Justice, and Leaves In many cities, access to trees is a luxury. Wealthier neighborhoods enjoy cool, 
            green streets—while lower-income communities endure heat, pollution, and poor health outcomes.  
            <br>Manual tree inspections are expensive and rare in underserved areas. But the need for data is urgent.
            <br>
            <span class="section-title" style="padding:20px; margin-left:50px;"><br>That's where GreenCity steps in<br></span>
            <br>Like a digital guardian, GreenCity utilizes satellite vision and machine learning to identify where shade grows—and where it doesn't. 
            It maps trees, analyzes canopy, and makes environmental inequity visible.
            With it, city planners, local advocates, and arborist groups can finally back up their instincts with real, block-by-block data.
            <br><br>
        </div>
        
        <div class="section-text"><img src="${baseURL}/static/assets/img/street1.jpg" style="width: 40vw;">
            <br><span class="imgText">1981 -WPRA funded Friends of the Arroyo to replace live oaks near the Colorado Street Bridge</span>
        </div>
    </div>
 `,

"about2": `
    <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 1.3)")</script>
    <p class="pageTitle">Problem & Motivation</p>
    <div class="section-block">
        <span class="section-title" style="margin-left:100px; font-size:2em; ">Tree Canopy Isn't Equally Shared</span>
        <span class="section-text">
            <table><tr>
                <td style="align-content: center; display: flex;">
                    <div class="block-box borderbox" style="padding:30px;">Low income U.S. neighborhoods have 15-30% less tree cover.  They're 1.5-4°C hotter</div>
                </td>
                <td rowspan="2" style="vertical-align: top;">
                    <img src="${baseURL}/static/assets/img/pic1.png" style="width: 25vw;">
                    <br><br><img src="${baseURL}/static/assets/img/pic2.png" style="width: 20vw;"><br>
                    
                </td>
                </tr>
                <tr>
                <td  style="vertical-align: top; padding:50px; width:80%;">Nationwide studies show low-income neighborhoods have 15-30% less tree cover and can experience 1.5-4°C (up to 35-39°F) higher summer temperatures than wealthier neighborhoods. 
                These disparities aren't just numbers on a page—they translate into very real consequences for residents: hotter streets, poorer air quality, and greater health risks, especially during heat waves. 
                For example, in Palo Alto, canopy coverage is around 38%, but just next door in East Palo Alto, it's only 13.5%.
                <br>
                <br>
                These patterns reflect decades of uneven public investment, infrastructure, and environmental planning. 
                Low-income areas can have 41% fewer trees, which means less shade, more direct sun exposure, and children walking to school on hotter, unshaded sidewalks. 
                This is an environmental justice issue. Urban trees do much more than beautify a neighborhood—they cool streets, clean the air, reduce electricity bills, and support public health.
                <br><br>
                These patterns reflect decades of uneven public investment, infrastructure, and environmental planning. 
                Low-income areas can have 41% fewer trees, which means less shade, more direct sun exposure, and children walking to school on hotter, unshaded sidewalks. 
                This is an environmental justice issue. Urban trees do much more than beautify a neighborhood—they cool streets, clean the air, reduce electricity bills, and support public health.
                
                </td>
                </tr>
                <tr><td colspan="2"><div style="font-size: 0.7em;">
                    <ul><li>McDonald, R. I., Kroeger, T., Zhang, P., & Hamel, P. (2021). The value of US urban tree cover for reducing heat-related health impacts and electricity consumption. PLOS ONE, 16(3), e0248529. </li>
                        <li>https://doi.org/10.1371/journal.pone.0248529
                            Nowak, D. J., Greenfield, E. J., Hoehn, R. E., & Lapoint, E. (2013). Urban forest structure, ecosystem services and change in seven US cities. Urban Forestry & Urban Greening, 14(2), 126-135.</li>
                        <li>American Forests. (2021). Tree Equity Score: Methodology and Summary. https://www.americanforests.org/article/american-forests-launches-nationwide-tree-equity-scores/</li>
                    </ul>
                </div></td></tr>
            </table>
        </span>
    </div>
  `,
  "about3": `
 <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 3.3)")</script>
    <p class="pageTitle">Why It's Hard to See the Problem</p>
    <div class="section-block" style="background-color: rgba(0, 0, 0, 0.5);">

        <span class="section-text">
        <table style="text-valign:top;">
            <tr>
                <td style="vertical-align: top; width:60%; ">
                    <div class="borderbox">
                        <br>Existing inventories are often:
                        <div><br>
                            <ul>
                                <li>Outdated (5-15 years old)</li>
                                <li>Incomplete</li>
                                <li>Costly ($1.80-$2.50 per tree)</li>
                                <li>Labor intensive</li>
                                <li>inaccessible for smaller cities</li>
                            </ul>
                            <br>
                        </div>
                    </div>
                    <div style="font-size:1em;  padding:30px; ">                
                        A  key barrier stands in the way of progress: a lack of reliable, up-to-date data. 
                        Most cities rely on tree inventories that are 5-15 years old, often incomplete, and typically focus only on street trees, missing private lots and parks. 
                        Manual surveys are slow and expensive (costing up to $2.50 per tree), making it impossible for most communities—especially smaller or under-resourced cities—to keep accurate, actionable records. 
                        In some neighborhoods, a thriving canopy seen in person might not even appear in the city's database. 
                        This “visibility gap” makes tree inequity hard to see, hard to measure, and even harder to fix.
                        <br><br>
                        Cities, planners, and advocates are now under growing pressure to meet tree equity and canopy expansion goals, report on climate resilience, and apply for federal or state urban greening grants (e.g., the Inflation Reduction Act, CAL FIRE). But they simply can't do it without better data.
                    </div>
                    
                </td>
                <td  style="vertical-align:top;"><img src="${baseURL}/static/assets/img/pic5small.png" style="width: 30vw;">
                    <br><div class="imgText">Jacarandas in bloom in Long Beach on May 28. (Christina House / Los Angeles Times)</div>
                    
                </td>
            </tr>
            <tr><td colspan="2"><div style="font-size: 0.7em;">
                <ul><li>City of Pasadena Open Tree Inventory Data (2023). https://data.cityofpasadena.net</li>
                    <li>International Society of Arboriculture. (2002). Tree Inventories: A Guide for Urban Forest Managers. Arboricultural Update. https://auf.isa-arbor.com/content/14/2/36</li>
                    <li>Portland Parks & Recreation. (2020). CIP Tree Inventory Manual. https://www.portland.gov/sites/default/files/2020/cip-tree-inventory-user-manual.pdf</li>
                </ul>
                </div>
                </td>
            </tr>
        </table>
    </span>

    </div>

  `,

  "project":
  `
    <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 4.3)")</script>
    <p class="pageTitle">Data Source & Dataset</p>
    <div class="section-block" style="background-color: rgba(0, 0, 0, 0.5);">

        <span class="section-text">
        <table style="text-valign:top;">
            <tr>
                <td style="vertical-align: top; width:60vw; ">
                
                    <div style="font-size:1em;  padding:10px; ">                
                        Our project, GreenCity, aims to close this data gap—making tree canopy data visible, measurable, and actionable for every city, regardless of size or budget. Our mission is to empower communities to plan greener, healthier, and more resilient neighborhoods.
                        <br><br>
                        To address the visibility gap, we built a workflow around high-resolution aerial imagery and open city tree inventories, focusing on both model-ready data preparation and state-of-the-art deep learning techniques:<br>

                        </div>
                    
                    <div style="padding:20px; width:60vw;">
                        <div class="section-title">Data Science Approach</div>
                        <br>
                        <ol>
                            <li>
                                <strong>Data Collection &amp; Preparation:</strong>
                                <ul>
                                    <li>
                                        <strong>Imagery:</strong> We sourced NAIP aerial imagery at 0.6m per pixel and archival 10cm imagery, covering the City of Pasadena.
                                    </li>
                                    <li>
                                        <strong>Tree Inventories:</strong> We used the Pasadena Open Data platform, which, while valuable, highlighted the typical limitations of city tree records—outdated, incomplete, and street-focused.
                                    </li>
                                </ul>
                            </li>
                            <br>
                            <li>
                                <strong>Image Quality Assessment:</strong>&nbsp;<br>
                                Before modeling, we assessed over <strong>28,000 image chips</strong> using five key computer vision metrics—contrast, sharpness, edge density, centeredness, and brightness. These metrics, drawn from remote sensing and object detection literature, helped us filter poor-quality chips and flag those needing enhancement.&nbsp;<br>
                                Instead of discarding weak chips, we used these scores to target computer vision-based enhancements (contrast amplification, sharpening) in dense, ambiguous canopy zones. This not only saved computational resources, but directly improved our downstream model accuracy.
                            </li>
                        </ol>
                    </div>
                </td>
            </tr>
        </table>

  `,

  "project2":
  `
    <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 4.3)")</script>
    <p class="pageTitle">Tree Detection Models</p>
    <div class="section-block" style="background-color: rgba(0, 0, 0, 0.5);">

        <span class="section-text">
        <table style="text-valign:top;">
            <tr>
                <td style="vertical-align: top; width:60vw; ">
                
                    <div style="font-size:1em;  padding:10px; ">      
                        <ul>
                            <li>
                                <strong>VGG-16 Fully Convolutional Network (FCN):</strong>
                                <ul>
                                    <li>
                                        <strong>Input:</strong> Multispectral imagery (RGB channels), processed as 256x256 tiles for training and 2048x2048 for inference.
                                    </li>
                                    <li>
                                        <strong>Output:</strong> Confidence maps downsampled by 32×, indicating tree likelihood. Peak-finding turned these maps into tree point locations.
                                    </li>
                                    <li>
                                        <strong>Architecture:</strong> Modified VGG-16 with 21 layers and ~17 million trainable parameters.
                                    </li>
                                    <li>
                                        <strong>Purpose:</strong> Foundational for detecting tree locations to support further canopy analysis.
                                    </li>
                                </ul>
                            </li>
                            <br>
                            <li>
                                <strong>DeepForest (RetinaNet with ResNet-50 backbone):</strong>
                                <ul>
                                    <li>
                                        <strong>Model:</strong> One-stage object detector with FPN for multi-scale detection, pre-trained on over 30 forest datasets (annotated at 10cm resolution, then fine-tuned for urban shapes).
                                    </li>
                                    <li>
                                        <strong>Output:</strong> Bounding boxes per detected crown, plus confidence score.
                                    </li>
                                    <li>
                                        <strong>Parameters:</strong> ~34 million trainable.
                                    </li>
                                    <li>
                                        <strong>Experiments:</strong>
                                        <ul>
                                            <li>
                                                Released model on 60cm imagery (94% recall, but oversized boxes—high coverage, low precision).
                                            </li>
                                            <li>
                                                Released model on outdated 10cm imagery (93.2% recall, but imagery not current).
                                            </li>
                                            <li>
                                                Custom-trained on 60cm imagery from 2024 (80.6% recall, most consistent with ground truth).
                                            </li>
                                            <li>
                                                Retrained and hyperparameter-tuned with contrast-enhanced 60cm imagery (best result: 88.7% recall, accurate crown-level detection).
                                            </li>
                                        </ul>
                                    </li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </td>
                <td  style="vertical-align:top;"><img src="${baseURL}/static/assets/img/pic4.png" style="width: 25vw;">
                    <br>
                    
                </td>
            </tr>
            
        </table>
    </span>

    </div>
  `,
   "project3":
  `
    <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 4.3)")</script>
    <p class="pageTitle">Web Application for Visualizations</p>
    <div class="section-block" style="background-color: rgba(0, 0, 0, 0.5);">

        <span class="section-text">
        <table style="text-valign:top;">
            <tr>
                <td style="vertical-align: top; width:60vw; ">
                
                    <div style="font-size:1em;  padding:10px; ">      
                        
                        <li>
                            Interactive web tool (using Leaflet, Bootstrap, OpenStreetMap) where users can:
                            <ul>
                                <li>
                                    Compare different model results (tree points, canopy polygons).
                                </li>
                                <li>
                                    Select areas by census block, fixed area, or street segment.
                                </li>
                                <li>
                                    Visualize results as heatmaps and statistics for planning and reporting.
                                </li>
                                <li>
                                    See multiple map views (satellite, street, terrain) and detailed tooltips.
                                </li>
                            </ul>
                        </li>
                        
                    </div>
                </td>
                <td  style="vertical-align:top;"><img src="${baseURL}/static/assets/img/pic4.png" style="width: 25vw;">
                    <br>
                    
                </td>
            </tr>
            <tr><td colspan="2"><div style="font-size: 0.7em;">
                <ul><li>City of Pasadena Open Tree Inventory Data (2023). https://data.cityofpasadena.net</li>
                    <li>International Society of Arboriculture. (2002). Tree Inventories: A Guide for Urban Forest Managers. Arboricultural Update. https://auf.isa-arbor.com/content/14/2/36</li>
                    <li>Portland Parks & Recreation. (2020). CIP Tree Inventory Manual. https://www.portland.gov/sites/default/files/2020/cip-tree-inventory-user-manual.pdf</li>
                </ul>
                </div>
                </td>
            </tr>
        </table>
    </span>

    </div>
  `,
  "evaluation":
  `
    <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 6.8)")</script>
    <p class="pageTitle">Evaluation</p>
    <div class="section-block" >
        <span class="section-title" style="margin-left:100px; font-size:1.5em; ">Experiment Summary Table — What We Tried and Learned</span>
    <span class="section-text">
        
        <table>
            <tr><td colspan="2" style="text-align: center;">
                <table border="1" cellspacing="0" cellpadding="6" style="border: 1px solid rgb(255, 255, 255); background-color:rgba(0, 0, 0, 0.5); ">
                <thead>
                    <tr>
                    <th>Experiment</th>
                    <th>Imagery</th>
                    <th>Weights Used</th>
                    <th>Detection recall within 12 meters</th>
                    <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                    <td>1. Released model on 60cm imagery</td>
                    <td>60cm (2024)</td>
                    <td>DeepForest v1.5.2</td>
                    <td>94.02%</td>
                    <td>Boxes were oversized inflating coverage by over predicting.</td>
                    </tr>
                    <tr>
                    <td>2. Released model on 10cm imagery</td>
                    <td>10cm (2014)</td>
                    <td>DeepForest v1.5.2</td>
                    <td>93.22%</td>
                    <td>Better, but outdated imagery.</td>
                    </tr>
                    <tr>
                    <td>3. Custom-trained on 60cm</td>
                    <td>60cm (2024)</td>
                    <td>Trained from scratch</td>
                    <td>80.56%</td>
                    <td>More consistent with ground truth</td>
                    </tr>
                    <tr>
                    <td>4. CV-enhanced imagery (trained)</td>
                    <td>60cm (2024)</td>
                    <td>Retrained & tuned</td>
                    <td>88.70%</td>
                    <td>Best so far — enhanced contrast & tuning</td>
                    </tr>
                </tbody>
                </table>

            </td></tr>
            
        </table>
    </span>

    </div>
  `
}

function loadContent(){
    for (const id in sectionHTML) {
        const section = document.getElementById(id);
        if (section) {
            section.innerHTML = sectionHTML[id];
        } else {
            console.warn(`Section with id="${id}" not found in DOM.`);
        }
    }
}


function createCircles(){
        
    const layer = document.getElementById('background-layer');
    const section = layer.parentElement;
    const sectionWidth = section.offsetWidth;
    const sectionHeight = section.offsetHeight;

    const sizes = [0.2, 0.8, 0.4, 0.3, 0.4, 0.3]; // 50%, 25%, 10%
    const hightPos = [0.04, 3.1, 2.2, 3.7, 3, 2.7];
    const widthPos = [0.01, 0.02, 0.5, 1, 0.6, 0.05];
    const numCircles = 6;
    const sections = 6;

    for (let i = 0; i < numCircles; i++) {
        const sizeFactor = sizes[i];
        const pxSize = sectionWidth * sizeFactor;

        const circle = document.createElement('div');
        circle.classList.add('circle');
        circle.style.width = pxSize + 'px';
        circle.style.height = pxSize + 'px';

        //const x =  (maxX - minX) + minX;
        const x = widthPos[i] * sectionWidth;
        const y = hightPos[i] * sectionHeight;

        circle.style.left = x + 'px';
        circle.style.top = y + 'px';

        layer.appendChild(circle);
    }
}

function getBlock(hight, yPos){
    const line = document.createElement("div");
    line.className = "verticleBlock";
    line.style.height = hight;
    line.style.top = yPos;
    document.body.appendChild(line);
}


document.addEventListener('DOMContentLoaded', () => {
    const logo   = document.getElementById('logo');
    const app = document.getElementById('app');
    const initPage = document.getElementById('page-top');


    // ‑‑‑ Observe when the trigger section enters the viewport ‑‑‑
    function onScroll() {

        // check top page for logo change
        const toprect = initPage.getBoundingClientRect();
        const newSrc = '../static/assets/img/logo.png'; 
        const topSrc = '../static/assets/img/logoTop.png'
        const topViewport = toprect.top < -15 ; 

        if (topViewport)  {          // section’s top has reached viewport top
            logo.src = newSrc;
            logo.classList.add('topPage');
        } else {
            logo.src = topSrc;
            logo.classList.remove('topPage');

        }

        // check app page for logo change
        const rect = app.getBoundingClientRect();
        const inViewport = rect.top <= 150 && rect.bottom >  150; // section still intersects the viewport

        if (inViewport)  {          // section’s top has reached viewport top
            logo.classList.add('shrunk');
        } else {
            logo.classList.remove('shrunk');
        }
        
        
    }

    loadContent();
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
});

