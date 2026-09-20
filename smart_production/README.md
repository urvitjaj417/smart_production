# AI-Based Smart Production Optimization System

End-to-end machine fault prediction and workflow optimizer. Built with **C** (sensor simulation) + **Python** (ML + dashboard) as an engineering student capstone project.

---

## What It Does

| Component | Description |
|-----------|-------------|
| Data generation | Simulated sensor readings with realistic fault injection |
| ML Model | Predicts machine failure (Logistic Regression / Random Forest / XGBoost) |
| Optimization Logic | If `failure_risk > 0.7` → reduce load / maintenance required |
| OEE Report | Overall Equipment Effectiveness per machine |
| Dashboard | Full HTML operations cockpit plus the Streamlit ML dashboard |
| REST API | Optional Flask API for integration with factory systems |

---

## Project Structure

```
smart_production/
├── generate_data.py          ← Python data generator (no gcc needed)
├── c_module/
│   ├── sensor_sim.c          ← C data generator (advanced, needs gcc)
│   └── Makefile
├── ml/
│   ├── data_loader.py        ← CSV loading + feature engineering
│   ├── model.py              ← Random Forest (main model)
│   ├── model_xgb.py          ← All 3 models: LR / RF / XGBoost + optimization logic
│   └── optimizer.py          ← OEE, bottleneck detection, workflow suggestions
├── dashboard/
│   ├── index.html            ← Full operations cockpit demo (primary front end)
│   └── app.py                ← Streamlit ML dashboard
├── api/
│   └── flask_api.py          ← Optional Flask REST API
├── data/                     ← CSV goes here (gitignored)
├── models/                   ← .pkl models go here (gitignored)
├── requirements.txt
└── README.md
```

---

## Quick Start

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Generate data

**Option A: Pure Python (recommended, no gcc needed)**
```bash
python generate_data.py
# or: python generate_data.py --records 3000 --out data/sensor_data.csv
```

**Option B: C module (faster, more realistic)**
```bash
cd c_module && make run && cd ..
```

### Step 3 — Train the model

```bash
# Train all three models and compare
python ml/model_xgb.py --model all

# Or just Random Forest (best results)
python ml/model_xgb.py --model rf

# Or XGBoost (needs: pip install xgboost)
python ml/model_xgb.py --model xgb
```

You will see printed output like:

```
[CNC_Mill_A] HIGH RISK (73%) -- Reduce load / Maintenance required
[Lathe_B]    MEDIUM RISK (51%) -- Monitor closely / Schedule inspection
[Drill_E]    LOW RISK (12%) -- Normal operation. No action needed.
```

### Step 4 — Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501

### Full operations cockpit demo

The primary front end is the standalone `dashboard/index.html`. It includes the
overview, predictive maintenance, shifts, OEE, alerts, raw data, shot peening,
CNC machining, work orders, and quality/NADCAP modules. Serve it locally with:

```bash
python -m http.server 8501 --directory dashboard
```

Then open http://localhost:8501.

### Demo walkthrough video

The repository includes a polished narrated walkthrough with a visible AI-agent
cursor, animated click indicators, numbered transitions, synchronized narration,
real browser interaction, and smooth scrolling through long sections. The
Quality & Compliance segment explicitly shows the populated NCR table, root-cause
charts, and calibration register while they are explained. The recommended
LinkedIn/company cut is `demo/smart_production_demo.mp4` in 1920×1080. A
3840×2160 master is available at `demo/smart_production_company_demo_uhd.mp4`.

### Step 5 (optional) — REST API

```bash
python api/flask_api.py

# Test:
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature_c":130,"vibration_mms":1.5,"pressure_bar":5.0,
       "current_a":13.0,"cycle_time_s":3.5,"output_rate_uph":100}'
```

---

## Dataset Columns

| Column | Description |
|--------|-------------|
| `machine_id` | Machine identifier |
| `temperature` | Sensor temperature (°C) |
| `pressure` | Operating pressure (bar) |
| `operating_time` | Hours of continuous operation |
| `output_rate` | Units produced per hour |
| `failure` | 0 = normal, 1 = fault |
| `fault_type` | Overheating / Bearing Wear / Pressure Drop / Electrical Surge |
| `facility` | Plant 1 / Plant 2 |
| `function` | Machining / Forming / Assembly / Surface Treatment / Inspection / Joining / Finishing |
| `process` | Primary production process for the asset |
| `special_process` | Shot Peening / Heat Treatment / Anodizing / NDT / Welding / Painting / None |
| `batch_id` | Production batch identifier |

---

## ML Model Results

| Model | F1 Score | ROC-AUC |
|-------|----------|---------|
| Logistic Regression | ~0.65 | ~0.96 |
| Random Forest | ~0.83 | ~0.99 |
| XGBoost | ~0.85 | ~0.99 |

---

## Optimization Logic (the unique part)

```python
if failure_risk > 0.7:
    suggest = "Reduce load / Maintenance required"
elif failure_risk > 0.4:
    suggest = "Monitor closely / Schedule inspection"
else:
    suggest = "Normal operation. No action needed."
```

If a bottleneck is detected (machine risk > 1.5x fleet average):
- Increase capacity on that machine
- Suggest alternate production flow

---

## Push to GitHub

```bash
git init
git add .
git commit -m "feat: AI production optimization system (C + Python)"
git remote add origin https://github.com/YOUR_USERNAME/smart-production
git push -u origin main
```

---

## Tech Stack

- **C (gcc)** — low-level sensor data simulation
- **Python** — data engineering, ML, dashboard, API
- **scikit-learn** — Logistic Regression, Random Forest
- **XGBoost** — gradient boosting classifier
- **Streamlit + Plotly** — interactive dashboard
- **Flask** — REST API wrapper

---

*Engineering student project — demonstrating real industrial AI concepts: predictive maintenance, OEE, bottleneck detection, and workflow optimization.*
