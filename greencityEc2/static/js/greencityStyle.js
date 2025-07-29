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

        <li class="nav-item"><a class="nav-link" href="#app">App</a></li>
        
        <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
            Evaluation
            </a>
            <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#evaluation">Evaluation</a></li>
                <li><a class="dropdown-item" href="#impact">Key Learnings & Impact</a></li>
            </ul>
        </li>
        
        <li class="nav-item"><a class="nav-link" href="#signup">Contributors</a></li>
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
                <td style="vertical-align: top; width:40vw; ">
                
                    <div style="font-size:1em;  padding:10px; ">                
                        Our project, GreenCity, aims to close this data gap—making tree canopy data visible, measurable, and actionable for every city, regardless of size or budget. Our mission is to empower communities to plan greener, healthier, and more resilient neighborhoods.
                        <br><br>
                        To address the visibility gap, we built a workflow around high-resolution aerial imagery and open city tree inventories, focusing on both model-ready data preparation and state-of-the-art deep learning techniques:<br>

                        </div>
                    
                    <div style="padding:20px; width:40vw;">
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
                <td  style="vertical-align:top;"><img src="${baseURL}/static/assets/img/pic6.png" style="width: 40vw;">
                    <br>
                    <div class="borderbox">
                    <ul>
                    <li>Filtered images with 5 key quality metrics</li>
                    <li>Enhanced only images needing improvement(contrast, sharpness, etc)</li>
                    <li>Result: Model train only on best quality data for accurate tree and canopy detection.</li>
                    </ul>
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
                                        <strong>Output:</strong> Confidence maps downsampled by 32x, indicating tree likelihood. Peak-finding turned these maps into tree point locations.
                                    </li>
                                    <li>
                                        <strong>Architecture:</strong> Modified VGG-16 with 21 layers and ~17 million trainable parameters.
                                    </li>
                                    <li>
                                        <strong>Purpose:</strong> Foundational for detecting tree locations to support further canopy analysis.
                                    </li>
                                </ul>
                            </li>
                            <br><br><br>
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
                <td  style="vertical-align:top; text-align:center;">
                    <img src="${baseURL}/static/assets/img/pic7.png" style="width: 40vw;"><br>
                    
                            <img src="${baseURL}/static/assets/img/pic4.png" style="width: 35vw; padding:20px">
                            <br>

                    <br><br><br><br>
                    <img src="${baseURL}/static/assets/img/pic8.png" style="width: 40vw;"><br><br>
                    
                            <img src="${baseURL}/static/assets/img/pic9.png" style="width: 40vw; padding:20px">
                    <br><table style="font-size: 0.9em; padding:5px; text-align:center;">
                            <tr>
                                <td style="padding:5px;">Released model 60cm imagery</td>
                                <td style="padding:5px;">Released model 10 cm per pixel</td>
                                <td style="padding:5px;">Custom Trained 60cm</td>
                                <td style="padding:5px;">Custom Trained 60cm (Optimized Tiles)</td>
                            </tr></table>

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
                <td style="vertical-align: top; width:45vw; ">
                
                    <div style="font-size:1em;  padding:10px; ">      
                        
                        <li>
                            Interactive web tool where users can:
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
                    Web App Architecture & Flow Chart<br>
                    <img src="${baseURL}/static/assets/img/pic10.png" style="width: 45vw;">
                </td>
                <td  style="vertical-align:top;">
                    <div style="vertical-align:top; width:35vw; padding: 20px; border:1px solid;">
                    Tools and Platform:
                    <ul >
                    <li style="padding: 10px;">
                        <strong>Leaflet</strong> - A lightweight open-source JavaScript library for interactive maps.  
                        <br><em>Chosen for its simplicity and flexibility in rendering geospatial data directly in the browser, perfect for integrating with custom map layers and user interactions.</em>
                    </li>
                    <li style="padding: 10px;">
                        <strong>OpenStreetMap</strong> - A free, editable map of the world built by a community of mappers.  
                        <br><em>Used as the base tile layer for maps in Leaflet, offering an open, community-driven alternative to Google Maps without API quotas or fees.</em>
                    </li>
                    <li style="padding: 10px;">
                        <strong>AWS</strong> - Amazon Web Services provides scalable cloud infrastructure.  
                        <br><em>Chosen to host the Flask server and support backend services with reliable uptime, scalability, and integration with tools like EC2, S3, and Route 53.</em>
                    </li>
                    <li style="padding: 10px;">
                        <strong>Bootstrap</strong> - A responsive front-end CSS framework.  
                        <br> <em>Used for layout and UI consistency across devices, enabling rapid development of responsive, mobile-friendly pages with minimal custom styling.</em>
                    </li>
                    </ul>
                    </div>
                    
                </td>
            </tr>
            <tr><td colspan="2"><div style="font-size: 0.7em;">
                
                </div>
                </td>
            </tr>
        </table>
    </span>

    </div>
  `
  ,
  "evaluation":
  `
    <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 6.8)")</script>
    <p class="pageTitle">Evaluation</p>
    <div class="section-block" >
        <span class="section-title" style=" font-size:1.5em; ">Experiment Summary Table — What We Tried and Learned</span>
    <span class="section-text">
        <table width="100%">
            <tr>
            <td colspan="2" >
                <table style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr>
                    <th class="tableCell">Experiment</th>
                    <th class="tableCell">Imagery</th>
                    <th class="tableCell">Recall</th>
                    <th class="tableCell">Takeaway</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                    <td class="tableCell">1. Released Model</td>
                    <td class="tableCell">60cm (2024)</td>
                    <td class="tableCell">94.02%</td>
                    <td class="tableCell">Overestimated Canopy</td>
                    </tr>
                    <tr>
                    <td class="tableCell">2. Released Model</td>
                    <td class="tableCell">10cm (2014)</td>
                    <td class="tableCell">93.22%</td>
                    <td class="tableCell">Outdated imagery</td>
                    </tr>
                    <tr>
                    <td class="tableCell">3. Custom-trained</td>
                    <td class="tableCell">60cm (2024)</td>
                    <td class="tableCell">80.56%</td>
                    <td class="tableCell">Best Match to Ground</td>
                    </tr>
                    <tr>
                    <td class="tableCell">4. CV-enhanced</td>
                    <td class="tableCell">60cm (2024)</td>
                    <td class="tableCell">88.70%</td>
                    <td class="tableCell">Most accurate Results</td>
                    </tr>
                    <tr>
                    <td class="tableCell">5. Optimal Parameter</td>
                    <td class="tableCell">60cm (2024)</td>
                    <td class="tableCell">93.31%</td>
                    <td class="tableCell">Best Overall</td>
                    </tr>
                </tbody>
                </table>
            </td>
            </tr>
            <tr>
            <td style="padding:5px; width:50vw;">
                <ul style="padding:5px;">
                <li style="padding:5px;">
                    <strong>Tree Location Detection (VGG-16):</strong>
                    <ul>
                        <li>
                            <strong>Recall:</strong> 81% within 12 meters of ground truth locations (using KDTree matching).
                        </li>
                        <li>
                            <strong>Localization:</strong> 4.8m average distance to closest true tree.
                        </li>
                        <li>
                            <strong>Metrics:</strong> Chosen for their focus on completeness (recall) and spatial accuracy (distance), crucial for environmental planning and resource allocation.
                        </li>
                    </ul>
                </li>
                <li style="padding:5px;">
                    <strong>Canopy Detection (DeepForest):</strong>
                    <ul>
                        <li>
                            <strong>Best Recall:</strong> Up to 88.7% on enhanced 60cm imagery (using intersection with ground truth within a 12m threshold).
                        </li>
                        <li>
                            <strong>Experiment Insights:</strong>
                            <ul>
                                <li>
                                    Released models on lower-resolution or outdated imagery inflated recall with oversized, imprecise boxes.
                                </li>
                                <li>
                                    Custom training and targeted enhancements improved both precision and recall, aligning model output with true 2024 canopy data.
                                </li>
                            </ul>
                        </li>
                    </ul>
                </li>
                <li style="padding:5px;">
                    <strong>Evaluation Methods:</strong>
                    <ul>
                        <li>
                            Cross-model comparisons.
                        </li>
                        <li>
                            Manual annotation of large trees (future step for even better crown size awareness).
                        </li>
                        <li>
                            Five CV-based metrics tracked improvements not just visually, but statistically, after each enhancement.
                        </li>
                    </ul>
                </li>
                </ul>
            </td>
            <td style="vertical-align:top; padding:20px;">
                    <img src="${baseURL}/static/assets/img/pic11.png" style="width: 30vw;"></td>
            </tr>
            
        </table>
    </span>

    </div>
  `

  ,
  "impact":
  `
    <div class="verticleLine"></div><script>getBlock("15%", "calc(100vh * 6.8)")</script>
    <p class="pageTitle">Key Learnings & Impact</p>
    <div class="section-block" >
    <span class="section-text">
        <table width="100%">
            <tr>
            <td style="padding:5px; width:50vw;">
                <ul>
                <li style="padding:5px;">
                    <strong>Data Quality is Everything:</strong> Automated metrics for contrast, sharpness, and edge density allowed us to focus enhancement efforts, leading to measurable improvements in detection (not just “looking better,” but performing better).
                </li>
                <li style="padding:5px;">
                    <strong>Hyperparameter Tuning Makes a Difference:</strong>
                    <ul>
                        <li>
                            Smaller patch sizes (600–800px) and 25% overlap prevented rural overfitting and improved crown delineation in dense city environments.
                        </li>
                        <li>
                            Lowered score thresholds (0.45–0.50) retained larger crowns and avoided missing significant trees.
                        </li>
                        <li>
                            NMS (Non-Maximum Suppression) set at IoU 0.5 prevented loss of multi-branch or irregularly shaped crowns.
                        </li>
                    </ul>
                </li>
                <li style="padding:5px;">
                    <strong>Bridging the Data Gap Enables Equity:</strong>
                    <ul>
                        <li>
                            Our approach provides accessible, up-to-date tree data—allowing cities, planners, GIS teams, and advocates to target greening investments, track canopy goals, and support grant applications.
                        </li>
                        <li>
                            Making data visible, measurable, and actionable is critical for climate resilience, public health, and advancing climate justice.
                        </li>
                    </ul>
                </li>
                <li style="padding:5px;">
                    <strong>User-Driven Development:</strong>
                    <ul>
                        <li>
                            The GreenCity tool is already designed for—and with—urban forestry planners, sustainability officers, GIS analysts, and community groups in mind.
                        </li>
                        <li>
                            Our MVP lets users see, compare, and analyze canopy cover at multiple scales and with different models, supporting real-world decision making.
                        </li>
                    </ul>
                </li>
            </ul>
            </td>
            <td style="vertical-align:top; padding:20px;">
                    <img src="${baseURL}/static/assets/img/pic13.png" style="width: 30vw;"></td>
            </tr>
            
        </table>
    </span>

    </div>
  `
   ,
  "signup":
  `
    <div class="section-block" >
    <span class="section-text">
        <table width="100%">
            <tr>
            <td style="width:40vw; padding:10px;">
                <h2>
                Acknowledgements
                </h2>
            <ul>
                <li>
                    <a href="https://data.cityofpasadena.net/" target="_blank">City of Pasadena Open Data (tree inventory, aerial imagery)</a>
                </li>
                <li>
                    <a href="https://www.americanforests.org/article/american-forests-launches-nationwide-tree-equity-scores/" target="_blank">American Forests (Tree Equity Score, Methodology and Summary)</a>
                </li>
                <li>
                    <a href="https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248529" target="_blank">McDonald, R. I. et al., PLOS ONE, 2021 – The value of US urban tree cover for reducing heat-related health impacts and electricity consumption</a>
                </li>
                <li>
                    <a href="https://www.sciencedirect.com/science/article/abs/pii/S1618866714000413" target="_blank">Nowak, D. J., Greenfield, E. J., Hoehn, R. E., &amp; Lapoint, E. (2013). Urban forest structure, ecosystem services and change in seven US cities. Urban Forestry &amp; Urban Greening, 14(2), 126–135.</a>
                </li>
                <li>
                    <a href="https://clf.org/blog/the-truth-about-tree-equity/" target="_blank">Conservation Law Foundation: The Truth About Tree Equity</a>
                </li>
                <li>
                    <a href="https://time.com/6996432/trees-heat-waves-essay/" target="_blank">Time Magazine (2024): Shade Is Survival</a>
                </li>
                <li>
                    <a href="https://auf.isa-arbor.com/content/14/2/36" target="_blank">International Society of Arboriculture: Tree Inventories – A Guide for Urban Forest Managers (2002)</a>
                </li>
                <li>
                    <a href="https://www.portland.gov/parks/trees/tree-inventory" target="_blank">Portland Parks &amp; Recreation: Tree Inventory Manual (2020)</a>
                </li>
                <li>
                    <a href="https://deepforest.readthedocs.io/en/latest/" target="_blank">DeepForest open-source contributors</a>
                </li>
                <li>
                    <a href="https://earthengine.google.com/" target="_blank">Google Earth Engine</a>
                </li>
                <li>
                    <a href="https://github.com/JonathanVentura/urban-tree-detection" target="_blank">Jonathan Ventura Urban Tree Detection Project &amp; Data</a>
                </li>
                <li>
                    <a href="https://research-it.berkeley.edu/services-projects/high-performance-computing-savio" target="_blank">UCB HPC cluster (Savio)</a>
                </li>
                <li>
                    Project instructors: <a href="https://www.ischool.berkeley.edu/people/fred-nugen" target="_blank">Fred Nugen</a> and <a href="https://www.ischool.berkeley.edu/people/korin-reid" target="_blank">Korin Reid</a>
                </li>
            </ul>
            </td>
            <td style="vertical-align:top; width:50vw; padding:10px;">
                    <h2>MIDS Capstone Project Summer 2025<br></h2>
                    <div class="borderbox" style="width:35vw;">
                    <h5>Team members:</h5>
                    <div class="field__item"><a href="/people/fengchen-liu">Fengchen Liu</a> - Machine Learning Engineer</div>
                    <div class="field__item"><a href="/people/antonio-martinez">Antonio Martinez</a> - Project Manager</div>
                    <div class="field__item"><a href="/people/richard-oldham">Richard Oldham</a> - Infrastructure and Data Engineer</div>
                    <div class="field__item"><a href="/people/minghwei-sun">Minghwei Sun</a> - MVP Application Developer</div>
                    </div>
            </td>
            </tr>
            
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

    const sizes = [0.2, 0.5, 0.4, 0.3, 0.4, 0.3, 0.5, 0.3]; // 50%, 25%, 10%
    const hightPos = [0.2, 0.1, 1.5, 1.8, 2.1, 2.8, 3.7, 4.5];
    const widthPos = [0.05, 0.3, 0.4, 0.3, 0.45, 0.2, 0.4, 0.2];
    const numCircles = 8;
    const sections = 8;

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

