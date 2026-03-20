
# 🔥 Burned Area Detector - Professional QGIS Plugin

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-589632.svg)](https://plugins.qgis.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-GPLv2-red.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)]()
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)]()

A comprehensive QGIS plugin for burned area detection and analysis from Sentinel-2 satellite imagery using advanced fuzzy logic and region growing algorithms.

---

## 👨‍🎓 **Author & Institution**

| | |
|---|---|
| **Author** | Ghulam Abbas Zafari |
| **Institution** | Politecnico di Milano |
| **Degree** | MSc in Geoinformatics Engineering |
| **Thesis** | Development and Integration of Advanced Features in Burned Area Detector Plugin |
| **Contact** | ghulamabbas.zafari@gmail.com |
| **GitHub** | [zafariabbas68](https://github.com/zafariabbas68) |
| **Portfolio** | [personal-website-gaz.onrender.com](https://personal-website-gaz.onrender.com) |

---

## 📖 **Table of Contents**

- [Overview](#-overview)
- [Features](#-features)
- [Plugin Tabs](#-plugin-tabs)
- [Algorithm Description](#-algorithm-description)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Input Requirements](#-input-requirements)
- [Output Format](#-output-format)
- [Validation Metrics](#-validation-metrics)
- [Citation](#-citation)
- [License](#-license)

---

## 🌍 **Overview**

The **Burned Area Detector** plugin is a professional tool for detecting and analyzing areas affected by wildfires using Sentinel-2 satellite imagery. Developed as part of a Master's thesis at Politecnico di Milano, this plugin implements advanced algorithms based on fuzzy logic and region growing segmentation, providing accurate and reliable burned area mapping.

This plugin is designed for:
- **Researchers** studying wildfire impacts
- **Environmental agencies** monitoring forest fires
- **Emergency responders** assessing post-fire damage
- **GIS professionals** working with remote sensing data

---

## ✨ **Features**

| Feature | Description |
|---------|-------------|
| 🔥 **Burned Area Detection** | Fuzzy logic algorithm with region growing segmentation |
| 📈 **Burn Severity** | USGS severity classification using dNBR (7 classes) |
| 📊 **Validation** | Confusion matrix, accuracy metrics, and statistical analysis |
| 🌍 **Pre-Processing** | SCL-based cloud, water, and snow masking |
| 🔄 **Change Detection** | NDVI/NBR difference analysis for vegetation recovery |
| 🗺️ **Agreement Map** | Spatial accuracy visualization (TP, FP, FN, TN) |
| ⚡ **Batch Processing** | Process multiple image pairs automatically |

---

## 🗂️ **Plugin Tabs**

The plugin features a professional multi-tab interface:

| Tab | Icon | Function |
|-----|------|----------|
| Detection | 🔥 | Main burned area detection with adjustable parameters |
| Burn Severity | 📈 | USGS severity classification (Enhanced Regrowth to High Severity) |
| Validation | 📊 | Accuracy assessment with reference data |
| Pre-Processing | 🌍 | SCL band masking for clouds, water, and snow |
| Change Detection | 🔄 | NDVI/NBR difference maps for recovery analysis |
| Agreement Map | 🗺️ | Spatial visualization of classification accuracy |
| Batch Processing | ⚡ | Automated processing of multiple image pairs |

---

## 🧠 **Algorithm Description**

### **Fuzzy Logic Algorithm**
Based on the research from CNR-IREA (Sali et al., 2021), the algorithm combines multiple spectral indices:

1. **Spectral Indices Calculation**
   - NDVI (Normalized Difference Vegetation Index)
   - NBR (Normalized Burn Ratio)
   - dNDVI and dNBR differences

2. **Fuzzy Membership Functions**
   - Sigmoid functions for each evidence
   - Customizable thresholds (seed and grow)

3. **Ordered Weighted Averaging (OWA)**
   - Evidence aggregation
   - Configurable operators (AND, OR, AVERAGE)

4. **Region Growing Segmentation**
   - Seed-based expansion
   - Iterative pixel aggregation
   - Commission/omission error balancing

### **Burn Severity Classification**
Based on USGS standards (dNBR values):

| Class | Severity Level | dNBR Range | Color |
|-------|---------------|------------|-------|
| 1 | Enhanced Regrowth High | -0.500 to -0.251 | 🟢 Dark Green |
| 2 | Enhanced Regrowth Low | -0.250 to -0.101 | 🟢 Green |
| 3 | Unburned | -0.100 to 0.099 | 🟢 Light Green |
| 4 | Low Severity | 0.100 to 0.269 | 🟡 Yellow |
| 5 | Moderate-Low Severity | 0.270 to 0.439 | 🟠 Orange |
| 6 | Moderate-High Severity | 0.440 to 0.659 | 🔴 Red-Orange |
| 7 | High Severity | 0.660 to 1.300 | 🔴 Red |

---

## 📦 **Installation**

### **Method 1: QGIS Plugin Manager (Recommended)**
1. Open QGIS
2. Go to **Plugins → Manage and Install Plugins**
3. Search for **"Burned Area Detector"**
4. Click **Install Plugin**
5. The plugin icon will appear in the toolbar

### **Method 2: Manual Installation**
1. Download the plugin ZIP file from [GitHub Releases](https://github.com/zafariabbas68/Burned-area-detection/releases)
2. In QGIS, go to **Plugins → Manage and Install Plugins**
3. Click **Install from ZIP**
4. Select the downloaded ZIP file
5. Click **Install**

### **Method 3: From Source**
```bash
# Clone the repository
git clone https://github.com/zafariabbas68/Burned-area-detection.git

# Copy to QGIS plugins directory
# macOS:
cp -r Burned-area-detection ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/

# Linux:
cp -r Burned-area-detection ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

# Windows:
# Copy to: C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```

---

## 📖 **Usage Guide**

### **Step 1: Load Sentinel-2 Images**
1. Open QGIS
2. Go to **Layer → Add Layer → Add Raster Layer**
3. Select your pre-fire and post-fire Sentinel-2 images

### **Step 2: Open Plugin**
1. Click the **fire icon** 🔥 in the toolbar
2. The main dialog with 7 tabs will open

### **Step 3: Detection Tab**
1. Select **Pre-fire Image** and **Post-fire Image** from dropdowns
2. Adjust parameters if needed:
   - **Seed Threshold** (0-1): Higher = more conservative (default: 0.9)
   - **Grow Threshold** (0-1): Lower = more aggressive (default: 0.1)
   - **Max Iterations**: Region growing steps (default: 50)
3. Choose output file path
4. Click **Run Detection**

### **Step 4: Burn Severity Tab**
1. Load pre-fire and post-fire NBR layers
2. Optional: Provide burned area mask
3. Click **Generate Severity Map**

### **Step 5: Validation Tab**
1. Select your burned area map and reference layer
2. Click **Run Validation**
3. View confusion matrix and accuracy metrics
4. Export results as CSV or HTML

### **Step 6: Batch Processing**
1. Click **Add Image Pairs**
2. Select multiple pre-fire and post-fire images
3. Click **Process All Pairs**

---

## 📋 **Input Requirements**

| Requirement | Specification |
|-------------|---------------|
| **Sensor** | Sentinel-2 Level-2A (recommended) |
| **Format** | GeoTIFF (.tif, .tiff) |
| **Bands** | Red (B4), NIR (B8), SWIR2 (B12) |
| **Projection** | Same projection for both images |
| **Extent** | Same spatial extent for both images |
| **Reference Data** | CEMS polygons or manual reference (for validation) |

---

## 📤 **Output Format**

The plugin generates GeoTIFF files with the following values:

| Value | Meaning | Color |
|-------|---------|-------|
| 1 | Burned area | 🔴 Red |
| 0 | Unburned area | 🟢 Green |
| 255 | No data / Masked | ⚪ White/Gray |

**Burn Severity Output:**
| Value | Severity Level |
|-------|---------------|
| 1-7 | Severity class (1=Enhanced Regrowth, 7=High Severity) |
| 3 | Unburned |

---

## 📊 **Validation Metrics**

The validation tab calculates the following metrics:

| Metric | Formula | Description |
|--------|---------|-------------|
| **Overall Accuracy** | (TP + TN) / Total | Percentage of correctly classified pixels |
| **Commission Error** | FP / (TP + FP) | Overestimation error |
| **Omission Error** | FN / (TP + FN) | Underestimation error |
| **Dice Coefficient** | 2TP / (2TP + FP + FN) | Spatial overlap similarity (F1 score) |
| **Kappa Coefficient** | (p0 - pe) / (1 - pe) | Inter-rater agreement |

### **Confusion Matrix**

| | Predicted Burned | Predicted Unburned |
|---|---|---|
| **Actual Burned** | True Positive (TP) | False Negative (FN) |
| **Actual Unburned** | False Positive (FP) | True Negative (TN) |

---

## 📝 **Citation**

If you use this plugin in your research, please cite:

```bibtex
@software{zafari_2025_burned_area_detector,
  author = {Zafari, Ghulam Abbas},
  title = {Burned Area Detector: A QGIS Plugin for Wildfire Analysis},
  year = {2025},
  institution = {Politecnico di Milano},
  url = {https://github.com/zafariabbas68/Burned-area-detection}
}
```

**APA Format:**
> Zafari, G.A. (2025). *Burned Area Detector: A QGIS Plugin for Wildfire Analysis* [Computer software]. Politecnico di Milano. https://github.com/zafariabbas68/Burned-area-detection

---

## 📄 **License**

This plugin is released under the **GNU General Public License v2.0**.

```
Copyright (c) 2025 Ghulam Abbas Zafari

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

---

## 🤝 **Contributing**

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📧 **Contact**

| | |
|---|---|
| **Email** | ghulamabbas.zafari@gmail.com |
| **GitHub** | [zafariabbas68](https://github.com/zafariabbas68) |
| **LinkedIn** | [Ghulam Abbas Zafari](https://linkedin.com/in/ghulam-abbas-zafari) |
| **Portfolio** | [personal-website-gaz.onrender.com](https://personal-website-gaz.onrender.com) |

---

## 🙏 **Acknowledgments**

- **Prof. Daniele Oxoli, PhD** - Supervisor, Politecnico di Milano
- **CNR-IREA** - For the fuzzy algorithm research
- **Copernicus Programme** - For Sentinel-2 data and CEMS reference products
- **QGIS Development Team** - For the excellent GIS platform

---

## 📊 **Version History**

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | March 2025 | Initial release with 7 professional tabs |
| | | - Burned area detection with fuzzy logic |
| | | - Burn severity classification (USGS) |
| | | - Validation with confusion matrix |
| | | - SCL cloud/water masking |
| | | - Change detection analysis |
| | | - Agreement map generation |
| | | - Batch processing support |

---

<div align="center">
  <sub>Developed with ❤️ by Ghulam Abbas Zafari | Politecnico di Milano</sub>
</div>
