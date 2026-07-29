# MIET Smart Campus Energy Command Centre (DSS)

An enterprise-grade **Energy Decision Support System (DSS)** designed for Meerut Institute of Engineering and Technology (MIET). The application analyzes smart-meter data, calculates energy efficiencies, triggers real-time alerts, runs interactive parameter simulation, and generates executive-ready audit reports.

---

## 🏛️ System Architecture & Services
This application is designed using a **Service-Oriented Clean Architecture** pattern, decoupling the presentation layout (Streamlit) from business mathematical rules (Services) and caching database accesses (Data Service).

```
d:\sakshi\
├── app.py                     # Main Streamlit router entry point
├── config/
│   ├── settings.py            # Calibrated settings management (JSON serialization)
│   ├── constants.py           # Default utility tariffs and carbon coefficients
│   └── logging.py             # System-wide log handlers
├── data/
│   └── miet_campus_dataset.csv # Raw CSV data points
├── services/
│   ├── data_service.py        # Dataset caching, feature engineering, and schema validators
│   ├── dashboard_service.py   # Health scores (0-100), KPI card consolidations
│   ├── analytics_service.py   # Aggregations for Plotly charting
│   ├── ml_service.py          # Regression pipelines, feature importance, and simulation
│   ├── optimization_service.py# HVAC setback checks and shiftable machinery loads
│   ├── recommendation_service.py # Explainable AI recommendation engine with ROI math
│   ├── alert_service.py       # Rule scan engine flagging low power factors & idle runs
│   └── report_service.py      # PDF Report compiler (ReportLab)
├── ui/
│   ├── dashboard.py           # Flagship Director Decision Centre view
│   ├── dataset_explorer.py    # Raw telemetry exploration and CSV exporter
│   ├── analytics.py           # Energy Command Centre charts and heatmaps
│   ├── simulator.py           # Scenario Planning Simulator and "what-if" input controllers
│   ├── load_optimization.py   # Load shifting tables and HVAC calibrations
│   ├── recommendations.py     # AI recommendations ROI and explainability notes
│   ├── alerts.py              # Operational warning logs
│   ├── reports.py             # Executive Report generator page
│   └── settings.py            # Calibration control page for managers
├── tests/
│   ├── test_data.py           # Tests for data_service.py validation
│   ├── test_ml.py             # Tests for ml_service.py prediction math
│   └── test_alerts.py         # Tests for alert_service.py rules
├── requirements.txt           # Python dependency definition
└── README.md                  # Detailed installation & user guide (This file)
```

---

## 🚀 Installation & Launch Guide

### Prerequisites
* Python 3.8 or higher.
* `pip` package manager.

### 1. Ingest Dependencies
Install all required libraries (Streamlit, Pandas, Scikit-Learn, Plotly, Matplotlib, ReportLab) using the consolidated package manifest:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Start the Streamlit local server:
```bash
streamlit run app.py
```

### 3. Run Automated Unit Tests
To verify data schemas, model math, and alert routines:
```bash
python -m unittest discover -s tests
```

---

## 📘 User Persona Guide

The application automatically customizes access routes based on selected user profiles:

### 1. Director (Executive View)
* **Flagship View**: Accesses the *Director Decision Centre* for high-level brief readings.
* **Smart Actions**: Reviews the *AI Recommendations* panel containing annual savings calculations, carbon offsets, and explainability narratives.
* **Reporting**: Generates the downloadable multi-page *Executive PDF Audit Report* featuring signature sections.

### 2. Energy Manager (Operations View)
* **Load Shifting**: Analyzes laboratory and workshop schedules to balance peak grid loads.
* **Planning Simulator**: Modifies temperature, occupancy, AC units, and lighting/HVAC values via sliders to forecast hourly utility budgets.
* **Analytics**: Monitors weather-to-energy correlations and building-by-building load graphs.

### 3. Electrical Engineer (Technical View)
* **Power Quality**: Monitors line voltage, current, frequency, and power factors.
* **Smart Alerts**: Receives critical warnings regarding low power factors (< 0.90) and hardware idle leaks.
* **Dataset Audits**: Searches, filters, and downloads clean CSV logs via the *Telemetry Explorer*.

### 4. Administrator (Control View)
* **Calibration Settings**: Modifies utility electricity tariffs (INR/kWh), grid carbon offsets, target power factors, and temperature comfort zones.

---

## 🧠 Smart Decision Features

* **Campus Energy Health Score (0-100)**: Evaluates electrical compliance, HVAC scheduling, occupancy waste, and carbon performance.
* **Scenario Planning Simulator**: Compares live hypothetical changes (e.g. increasing students by 20% or ACs by 5) with historical baselines.
* **Explainable Recommendations**: Breaks down ROI savings calculations (INR/year) with underlying formulas and triggers.
