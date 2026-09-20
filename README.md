# Smart Production

### AI-assisted manufacturing intelligence for predictive maintenance, special processes, quality, and operational excellence.

**Smart Production** is an end-to-end manufacturing analytics and digital-operations demonstration created by **Urvit Jajoo**. It shows how sensor data, machine-learning risk detection, production workflows, special-process control, quality evidence, and executive reporting can work together in one operational cockpit.

> **Sensor data → AI risk detection → Production action → Quality evidence → Management improvement**

## Why Smart Production?

Manufacturing teams often have machine data, quality records, work orders, and compliance information distributed across different systems. Smart Production demonstrates a connected operating model that helps teams identify risk earlier, understand the production impact, and move from analysis to action with traceable records.

The project is designed as an extensible engineering foundation for organizations exploring practical AI adoption across machining, aerospace, automotive, industrial production, surface treatment, and quality operations.

## Product walkthrough

The narrated walkthrough is designed for company presentations and LinkedIn sharing. It includes a visible AI-agent cursor, animated click indicators, synchronized narration, populated work-order and NCR data, and smooth scrolling through long operational sections.

- [Watch the 1080p company and LinkedIn demo](smart_production/demo/smart_production_demo.mp4)
- [Open the UHD 3840×2160 presentation master](smart_production/demo/smart_production_company_demo_uhd.mp4)
- [Read the step-by-step feature guide](smart_production/demo/walkthrough_guide.md)

## Capabilities

| Manufacturing area | Demonstrated capability |
|---|---|
| **Predictive maintenance** | Failure probability, fault type, risk level, sensor trends, and recommended action |
| **Production intelligence** | OEE, shift comparison, output trends, alerts, bottleneck analysis, and workflow recommendations |
| **CNC machining** | Spindle utilization, coolant pressure, motor temperature, output, fault trends, tooling wear, and job history |
| **Shot Peening** | Work orders, Almen intensity, coverage, roughness, media condition, planning, specification checks, and job insertion |
| **Quality and compliance** | NCRs, root causes, dispositions, calibration registers, AS9100D, ISO 9001, ISO 14001, and NADCAP visibility |
| **Data operations** | CSV/XLSX workflows, raw-data search, exports, simulated data, C sensor simulation, and REST predictions |
| **Advanced operations** | Digital Twin, Computer Vision, ERP Integration, Supply Chain, Sustainability, Predictive Quality, and Executive Dashboard |

## Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                  Smart Production Cockpit                   │
├──────────────────────┬──────────────────────┬────────────────┤
│ HTML Operations UI   │ Streamlit ML UI      │ React Frontend │
├──────────────────────┴──────────────────────┴────────────────┤
│ Python ML + Flask API │ FastAPI + SQLAlchemy │ C Sensor Sim │
├──────────────────────────────────────────────────────────────┤
│ CSV / simulated data │ PostgreSQL-ready API │ Model layer  │
└──────────────────────────────────────────────────────────────┘
```

The repository contains a standalone HTML cockpit for the complete product demonstration, a Streamlit machine-learning dashboard, a Flask prediction API, a FastAPI/SQLAlchemy backend foundation, a React/Vite frontend foundation, and a C-based sensor simulator.

## Run locally

### 1. Install the Python runtime

```bash
cd smart_production
python3 -m pip install -r requirements.txt
```

### 2. Generate production sensor data and train a model

```bash
python3 generate_data.py --records 2000 --out data/sensor_data.csv
python3 ml/model_xgb.py --model rf
```

Available model options are `lr` for Logistic Regression, `rf` for Random Forest, `xgb` for XGBoost, and `all` for comparison.

### 3. Launch the operations cockpit

```bash
python3 -m http.server 8501 --bind 0.0.0.0 --directory dashboard
```

Open `http://localhost:8501` in a browser.

### 4. Launch the Streamlit ML dashboard

```bash
streamlit run dashboard/app.py
```

### 5. Run the Flask prediction API

```bash
python3 api/flask_api.py
```

Example prediction request:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature_c":130,"vibration_mms":1.5,"pressure_bar":1.5,"current_a":13.0,"cycle_time_s":3.5,"output_rate_uph":35}'
```

A high-risk response includes the predicted fault, probability, risk level, fault type, and recommended decision context.

### 6. Run the C sensor simulator

```bash
cd c_module
make run
```

The C module produces sensor-style CSV data with machine, facility, function, process, special-process, and fault fields.

## Repository map

```text
smart_production/
├── api/                 Flask prediction API
├── backend/             FastAPI, SQLAlchemy, and model-training service
├── c_module/            C sensor simulator
├── dashboard/           HTML operations cockpit and Streamlit dashboard
├── demo/                Company videos and feature guide
├── frontend/            React/Vite frontend foundation
├── ml/                  Data loading, models, and optimization logic
├── generate_data.py     Python sensor-data generator
└── README.md            Detailed implementation documentation
```

## Validation

The main branch has been checked for Python syntax, data generation, model training, live prediction, Flask API behavior, C simulator execution, C/Python schema compatibility, FastAPI import and training, frontend TypeScript/Vite compilation, HTML cockpit serving, and GitHub Actions path correctness.

This is an engineering demonstration and extensible foundation, not a certified production-control system. Real deployment should connect validated historical data and approved interfaces for MES, ERP, SCADA, PLC, maintenance, quality, calibration, and cybersecurity requirements.

## Collaboration

Smart Production is intended for technical collaboration, manufacturing transformation discussions, pilot exploration, and further integration with real factory systems. Contributions, implementation feedback, and use-case discussions are welcome through GitHub issues and pull requests.

**Created by Urvit Jajoo**

## License

No open-source license has been declared yet. Add an appropriate license before distributing or reusing the project externally.
