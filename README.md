# 🚀 MOIL Smart Mining Hub — Orelytics

### AI/ML and Space Technology for Manganese Mining

MOIL Smart Mining Hub is an AI/ML and Space Technology-based decision-support platform designed for manganese mining.

It integrates satellite, geological, exploration, environmental and operational information into one interactive dashboard to support:

- 🛰️ Manganese prospectivity mapping
- 📈 Production and shortfall-risk analysis
- 🌧️ Environmental and weather monitoring
- ⚙️ Operational monitoring
- 🚨 Risk indicators and alerts
- 🔄 What-If Scenario Simulation
- 📊 Interactive mining analytics

---

## 🎯 Problem Statement

**SIH26009 — Using AI/ML and Space Technology to Identify Manganese Reserves and Overcome Production Shortfalls**

Mining teams work with information from different sources such as geological data, exploration records, satellite observations, environmental conditions and production data.

Our goal is to bring these sources together and convert them into useful decision-support information.

---

## 💡 Our Solution

The platform follows the workflow:

**Data → Integration → AI/ML → Prediction → Risk/Alerts → Decision Support**

The system combines:

### 🛰️ Space & Environmental Data
- Sentinel-2 SWIR
- Sentinel-1 SAR
- Vegetation / NDVI
- Soil moisture
- Rainfall and weather information

### 🪨 Mining & Exploration Data
- Geological information
- Borehole information
- Ore-grade information
- Exploration indicators

### ⚙️ Operational Data
- Production
- Target vs actual production
- Equipment/fleet information
- Operational indicators

---

## 🤖 AI/ML

The prototype uses machine learning to support:

- Production estimation
- Production shortfall-risk analysis
- Manganese prospectivity assessment

The current implementation uses a **HistGradientBoostingRegressor** for production-related prediction.

> Model outputs are intended as decision-support indicators and require validation using authorized operational data before real-world deployment.

---

## 🗺️ Key Features

### 1. Manganese Prospectivity Mapping
Provides a model-based prospectivity score to identify areas that may be worth further exploration.

### 2. Satellite Analysis
Uses satellite-derived layers such as SWIR, SAR, vegetation and soil moisture as supporting evidence.

### 3. Borehole & Ore Grade Analysis
Combines subsurface exploration information with surface observations to provide additional mining context.

### 4. Production Shortfall Analysis
Compares production-related information to identify potential shortfall risks.

### 5. Alerts
Converts selected data conditions into risk indicators and alerts for easier decision-making.

### 6. What-If Scenario Simulator
Allows users to explore possible operational scenarios and view estimated changes in the prototype.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and machine learning |
| Streamlit | Interactive web dashboard |
| Scikit-learn | Machine learning |
| HistGradientBoostingRegressor | Production prediction |
| Plotly | Interactive visualizations |
| Google Earth Engine | Geospatial/satellite data processing |
| Sentinel-1 / Sentinel-2 | Satellite observations |
| NASA SMAP | Soil moisture information |

---

## 🏗️ System Architecture

```text
Satellite Data
      +
Geological Data
      +
Exploration Data
      +
Environmental Data
      +
Operational Data
      ↓
Data Processing & Integration
      ↓
AI / ML Models
      ↓
Predictions & Risk Indicators
      ↓
Interactive Streamlit Dashboard
      ↓
Alerts + What-If Analysis
      ↓
Human Decision Support
