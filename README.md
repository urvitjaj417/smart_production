# Smart Production

**AI-assisted manufacturing intelligence for predictive maintenance, special processes, quality, and operational decision-making.**

**Created by:** Urvit Jajoo

Smart Production is an end-to-end manufacturing analytics and operations demonstration. It combines sensor-data generation, machine-failure prediction, workflow recommendations, OEE analysis, CNC machining visibility, Shot Peening process control, NCR and calibration tracking, compliance monitoring, and executive reporting in one project.

## Product demonstration

The recommended company and LinkedIn walkthrough is available here:

[Open the 1080p LinkedIn/company demo](smart_production/demo/smart_production_demo.mp4)

A higher-resolution presentation master is also included:

[Open the UHD 3840×2160 master](smart_production/demo/smart_production_company_demo_uhd.mp4)

The walkthrough uses a visible AI-agent cursor, animated click indicators, synchronized narration, populated work-order and NCR data, and smooth scrolling through long operational sections.

## Main capabilities

| Area | Capabilities |
|---|---|
| Predictive maintenance | Failure probability, fault type, risk level, sensor analytics, and recommended action |
| Production operations | OEE, shift comparison, output trends, alerts, bottleneck analysis, and workflow recommendations |
| CNC machining | Spindle utilization, coolant pressure, motor temperature, output, fault trends, tooling wear, and job history |
| Shot Peening | Work orders, Almen intensity, coverage, roughness, media condition, planning, specification checks, and job insertion |
| Quality and compliance | NCRs, root causes, dispositions, calibration registers, AS9100D, ISO 9001, ISO 14001, and NADCAP visibility |
| Data workflows | CSV/XLSX upload, raw-data search, exports, simulated data, C sensor simulation, and REST prediction API |
| Advanced operations | Digital Twin, Computer Vision, ERP Integration, Supply Chain, Sustainability, Predictive Quality, and Executive Dashboard |

## Quick start

```bash
cd smart_production
python3 -m pip install -r requirements.txt
python3 generate_data.py --records 2000 --out data/sensor_data.csv
python3 ml/model_xgb.py --model rf
```

### Launch the HTML operations cockpit

```bash
cd smart_production
python3 -m http.server 8501 --bind 0.0.0.0 --directory dashboard
```

Open `http://localhost:8501` in a browser.

### Launch the Streamlit machine-learning dashboard

```bash
cd smart_production
streamlit run dashboard/app.py
```

### Run the Flask prediction API

```bash
cd smart_production
python3 api/flask_api.py
```

Example request:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature_c":130,"vibration_mms":1.5,"pressure_bar":1.5,"current_a":13.0,"cycle_time_s":3.5,"output_rate_uph":35}'
```

### Run the C sensor simulator

```bash
cd smart_production/c_module
make run
```

## Documentation

The detailed repository documentation is available in [`smart_production/README.md`](smart_production/README.md). The feature-by-feature walkthrough guide is available in [`smart_production/demo/walkthrough_guide.md`](smart_production/demo/walkthrough_guide.md).

The implementation includes both a standalone HTML cockpit for the complete product demonstration and a separate React/FastAPI application foundation for continued production integration.

## Validation status

The current main branch has been validated for Python syntax, data generation, machine-learning training, live prediction, Flask API behavior, C sensor simulation, C/Python schema compatibility, FastAPI import and training, frontend TypeScript/Vite build, HTML cockpit serving, and GitHub Actions path correctness.

## Repository structure

```text
smart_production/
├── api/                 Flask prediction API
├── backend/             FastAPI, SQLAlchemy, and model-training service
├── c_module/            C sensor simulator
├── dashboard/           HTML cockpit and Streamlit dashboard
├── demo/                Walkthrough videos and feature guide
├── frontend/            React/Vite frontend foundation
├── ml/                  Data loading, models, and optimization logic
├── generate_data.py     Python sensor-data generator
└── README.md            Detailed project documentation
```

## Professional context

Smart Production is designed as an engineering demonstration and extensible foundation for manufacturing organizations evaluating practical AI adoption. It can be extended with real historical sensor data and integrated with MES, ERP, SCADA, PLC, maintenance, quality, and calibration systems.

For collaboration, technical feedback, pilot discussions, or manufacturing transformation opportunities, please open an issue or contact the project author through GitHub.

## License

No license has been declared yet. Add an appropriate license before distributing the project for external reuse.
