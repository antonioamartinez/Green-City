# 🌿 GreenCity Image Enhancement Pipeline

## 🎯 Objective

The image enhancement phase improves the visual quality and model readiness of 224×224 image chips used in our computer vision pipeline. These chips, drawn from overhead NAIP imagery, are inputs for downstream tasks like **canopy segmentation** and **tree detection**.

We target known failure modes — **blurry textures**, **dim lighting**, **washed-out contrast**, and **off-center canopy locations** — and correct them using a lightweight, interpretable transformation stack. The goal is to reduce noise and reveal tree structure **without sacrificing realism**.

---

## 🛠️ Pipeline Overview

Each raw image chip is passed through the following transformation steps:

1. **🧼 Unsharp Masking**  
   Sharpens edge features while suppressing low-frequency blur.  
   Tuned to avoid halos or sharpening artifacts.

2. **🌈 Contrast Limited Adaptive Histogram Equalization (CLAHE)**  
   Boosts local contrast while protecting against noise amplification.  
   Especially effective in shaded or overcast zones.

3. **🔆 Gamma Correction**  
   Brightens midtones and evens out lighting across varied environments.

4. **🎯 Optional Center Cropping / Alignment**  
   Realigns canopy centroids closer to the chip center.  
   Useful for anchor-based detection models.

All enhancements are applied using OpenCV. Raw and enhanced versions are stored separately to support ablation studies and filter effectiveness tracking.

---

## 🖼️ Visual Results

**Before vs After: Pairplot Summary (57K Chips)**  
Comparison of raw and enhanced distributions across five core metrics:

| 📊 Metric           | 🟥 Raw Distribution                | 🟦 Corrected Distribution          |
|---------------------|------------------------------------|------------------------------------|
| **Sharpness**       | Clustered <100 (blur heavy)        | Shifted to 200–250 range           |
| **Brightness**      | Narrow band 80–100                 | Expanded to 100–150, more natural  |
| **Contrast**        | Clipped <50, failure-prone         | Boosted to 60–80, fewer fails      |
| **Edge Density**    | Flat to moderate slope             | Steeper correlation w/ sharpness   |
| **Centroid Offset** | Failures centered ~0.2–0.3         | More passes near 0–0.1             |

🧠 *These shifts are not only numerical — they’re clearly visible in the side-by-side pairplots.*

---

## 📈 Impact on Filtering & Modeling

✅ **Fewer false negatives**  
Chips previously flagged for failure (e.g. low contrast) now pass.

✅ **Cleaner segmentation cues**  
Edges and textures are better defined for canopy segmentation.

✅ **Improved object localization**  
Centering realigns targets to improve anchor-based detection performance.

---

## ✅ Summary

The enhancement pipeline is a critical pre-modeling step. It lifts the quality floor of our dataset, sharpens separability in metric space, and gives our models **a cleaner shot at learning**. All transformations are:

- 🔍 Interpretable  
- ⚡ Fast  
- 🏗️ Deployment-friendly  

…and tailored to real-world municipal applications.

---
