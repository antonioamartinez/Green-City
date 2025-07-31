### 📸 Computer Vision Workflow

The GreenCity CV pipeline enhances NAIP image chips before modeling. We flag weak inputs — blurry, dim, washed out, or misaligned — then correct them using a lightweight OpenCV stack. This boosts image clarity and improves model-readiness without synthetic artifacts.

Key steps:
1. Extract 224×224 chips from Earth Engine.
2. Score with interpretable metrics (e.g., brightness, contrast, sharpness).
3. Enhance via sharpening, CLAHE, gamma correction, and alignment.

Over 57,000 chips were processed, filtered, and polished. Enhancements increased pass rates and reduced metric failure clusters, improving segmentation and detection readiness.
