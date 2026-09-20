# dashboard/app.py
# Run: python -m streamlit run dashboard/app.py

import sys, os, pickle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml"))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_loader import load_data, engineer_features, summary_stats, FEATURE_COLS, TARGET_COL

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Production Optimizer",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252840);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #4c6ef5;
        margin-bottom: 10px;
    }
    .health-good  { border-left-color: #2ecc71 !important; }
    .health-warn  { border-left-color: #f39c12 !important; }
    .health-bad   { border-left-color: #e74c3c !important; }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 20px 0 10px 0;
    }
    .recommend-box {
        background: #1a1f2e;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 6px 0;
        border-left: 3px solid #4c6ef5;
    }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.78rem; color: #8892a4; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 Smart Production")
    st.markdown("*AI-Based Optimization System*")
    st.markdown("---")
    csv_path = st.text_input("Sensor CSV", value="data/sensor_data.csv")
    st.markdown("---")
    page = st.radio("Navigate", [
        "🏠  Overview",
        "🔮  Failure Predictions",
        "📊  Sensor Analytics",
        "🏭  Facilities & Special Processes",
        "⚙️  Recommendations",
        "🎛️  Live Predict",
    ])
    st.markdown("---")
    st.caption("Built with Python · scikit-learn · Streamlit")

# ── Load data ──────────────────────────────────────────────────────────────
@st.cache_data
def load(path):
    return engineer_features(load_data(path))

try:
    df = load(csv_path)
except FileNotFoundError as e:
    st.error(f"**Data not found.** Run `python generate_data.py` first.\n\n{e}")
    st.stop()

# Optional production-scope filters. Older CSVs remain supported.
with st.sidebar:
    if "facility" in df.columns:
        facility_sel = st.selectbox("Facility", ["All"] + sorted(df["facility"].dropna().unique().tolist()))
        function_sel = st.selectbox("Function", ["All"] + sorted(df["function"].dropna().unique().tolist()))
        process_sel = st.selectbox("Special process", ["All"] + sorted(df["special_process"].dropna().unique().tolist()))
        if facility_sel != "All":
            df = df[df["facility"] == facility_sel]
        if function_sel != "All":
            df = df[df["function"] == function_sel]
        if process_sel != "All":
            df = df[df["special_process"] == process_sel]

# Load model if available
MODEL_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "models", "fault_model_rf.pkl"),
    os.path.join(os.path.dirname(__file__), "..", "models", "fault_model.pkl"),
]
model = None
for mp in MODEL_PATHS:
    if os.path.exists(mp):
        with open(mp, "rb") as f:
            model = pickle.load(f)
        break

# Add ML predictions if model available
if model:
    X = df[FEATURE_COLS].values
    df["ml_prob"] = model.predict_proba(X)[:, 1]
    df["ml_pred"] = (df["ml_prob"] >= 0.5).astype(int)
else:
    df["ml_prob"] = 0.0
    df["ml_pred"] = 0

stats = summary_stats(df)
machines = sorted(df["machine_name"].unique())

def risk_color(rate):
    if rate > 15: return "#e74c3c"
    if rate > 8:  return "#f39c12"
    return "#2ecc71"

def risk_label(rate):
    if rate > 15: return "CRITICAL"
    if rate > 8:  return "WARNING"
    return "HEALTHY"

# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
if "Facilities" in page:
    st.markdown("# 🏭 Facilities & Special Processes")
    st.markdown("Monitor production functions, facilities, and controlled special-process steps such as shot peening.")
    st.markdown("---")

    has_special = "special_process" in df.columns
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Facilities", df["facility"].nunique() if "facility" in df.columns else "—")
    k2.metric("Functions", df["function"].nunique() if "function" in df.columns else "—")
    k3.metric("Processes", df["process"].nunique() if "process" in df.columns else "—")
    k4.metric("Special-process records", int((df["special_process"] != "None").sum()) if has_special else "—")

    if has_special:
        left, right = st.columns(2)
        with left:
            st.markdown('<p class="section-title">Special Process Mix</p>', unsafe_allow_html=True)
            special = df[df["special_process"] != "None"].groupby("special_process").size().reset_index(name="records")
            fig_sp = px.bar(special.sort_values("records"), x="records", y="special_process", orientation="h",
                            color="records", color_continuous_scale="Blues",
                            labels={"records": "Records", "special_process": ""})
            fig_sp.update_layout(height=360, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                                 font_color="#c0c0c0", margin=dict(t=10, b=10))
            st.plotly_chart(fig_sp, use_container_width=True)
        with right:
            st.markdown('<p class="section-title">Facility Risk and Output</p>', unsafe_allow_html=True)
            facility_stats = df.groupby("facility").agg(
                fault_rate=(TARGET_COL, "mean"), avg_output=("output_rate", "mean"), records=(TARGET_COL, "size")
            ).reset_index()
            facility_stats["fault_rate"] *= 100
            fig_fac = px.bar(facility_stats, x="facility", y="fault_rate", color="fault_rate",
                             color_continuous_scale="RdYlGn_r", labels={"fault_rate": "Fault %", "facility": ""})
            fig_fac.update_layout(height=360, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                                  font_color="#c0c0c0", margin=dict(t=10, b=10))
            st.plotly_chart(fig_fac, use_container_width=True)

        st.markdown('<p class="section-title">Function / Process Register</p>', unsafe_allow_html=True)
        register_cols = [c for c in ["facility", "function", "process", "special_process", "batch_id"] if c in df.columns]
        register = df[register_cols].drop_duplicates().sort_values(register_cols).head(100)
        st.dataframe(register, use_container_width=True, hide_index=True)
    else:
        st.info("Regenerate data with the updated generator to enable facility and special-process monitoring.")

# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
elif "Overview" in page:
    st.markdown("# 🏭 Smart Production Dashboard")
    st.markdown("Real-time machine monitoring · Fault prediction · Workflow optimization")
    st.markdown("---")

    # Top KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Records",    f"{len(df):,}")
    c2.metric("Machines Online",  f"{len(machines)}")
    c3.metric("Total Faults",     f"{int(df[TARGET_COL].sum()):,}")
    c4.metric("Fleet Fault Rate", f"{df[TARGET_COL].mean()*100:.1f}%")
    c5.metric("Avg Output (uph)", f"{df['output_rate'].mean():.0f}")
    st.markdown("---")

    # Machine health cards
    st.markdown('<p class="section-title">Machine Health Status</p>', unsafe_allow_html=True)
    cols = st.columns(len(machines))
    for i, machine in enumerate(machines):
        row   = stats[stats["machine_name"] == machine].iloc[0]
        rate  = row["fault_rate_pct"]
        color = risk_color(rate)
        label = risk_label(rate)
        m_df  = df[df["machine_name"] == machine]
        avg_prob = m_df["ml_prob"].mean() * 100 if model else 0

        with cols[i]:
            st.markdown(f"""
            <div class="metric-card {'health-bad' if rate>15 else 'health-warn' if rate>8 else 'health-good'}">
                <div style="font-size:0.8rem;color:#8892a4;margin-bottom:4px">{machine}</div>
                <div style="font-size:1.4rem;font-weight:700;color:{color}">{label}</div>
                <div style="font-size:0.85rem;margin-top:8px">
                    Fault rate: <b>{rate}%</b><br>
                    Output: <b>{row['avg_output']:.0f} uph</b><br>
                    AI Risk: <b>{avg_prob:.0f}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Two column charts
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<p class="section-title">Fault Rate per Machine</p>', unsafe_allow_html=True)
        fig = px.bar(
            stats, x="machine_name", y="fault_rate_pct",
            color="fault_rate_pct", color_continuous_scale="RdYlGn_r",
            labels={"fault_rate_pct": "Fault %", "machine_name": ""},
        )
        fig.add_hline(y=10, line_dash="dot", line_color="orange",
                      annotation_text="Warning threshold")
        fig.update_layout(height=300, margin=dict(t=10, b=10),
                          plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                          font_color="#c0c0c0", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<p class="section-title">Output Rate per Machine</p>', unsafe_allow_html=True)
        fig2 = px.bar(
            stats, x="machine_name", y="avg_output",
            color="avg_output", color_continuous_scale="Blues",
            labels={"avg_output": "uph", "machine_name": ""},
        )
        fig2.update_layout(height=300, margin=dict(t=10, b=10),
                           plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           font_color="#c0c0c0", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Output over time
    st.markdown('<p class="section-title">Production Output Over Time</p>', unsafe_allow_html=True)
    df_ts = df.groupby(["timestamp","machine_name"])["output_rate"].mean().reset_index()
    fig3  = px.line(df_ts, x="timestamp", y="output_rate", color="machine_name",
                    labels={"output_rate":"Output (uph)","timestamp":""})
    fig3.update_layout(height=300, margin=dict(t=10,b=10),
                       plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                       font_color="#c0c0c0")
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — FAILURE PREDICTIONS
# ══════════════════════════════════════════════════════════════════════════
elif "Failure" in page:
    st.markdown("# 🔮 Failure Predictions")
    if not model:
        st.warning("Model not trained. Run: `python ml/model_xgb.py --model rf --csv data/sensor_data.csv`")
        st.stop()

    from sklearn.metrics import f1_score, confusion_matrix

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ML F1 Score",       f"{f1_score(df[TARGET_COL], df['ml_pred']):.3f}")
    c2.metric("Faults Detected",   f"{df['ml_pred'].sum():,}")
    c3.metric("High Risk (>70%)",  f"{(df['ml_prob']>0.7).sum():,}")
    c4.metric("Missed Faults",     f"{((df[TARGET_COL]==1)&(df['ml_pred']==0)).sum()}")
    st.markdown("---")

    # Risk gauges per machine
    st.markdown('<p class="section-title">Risk Score per Machine</p>', unsafe_allow_html=True)
    risk_data = df.groupby("machine_name")["ml_prob"].mean().reset_index()
    cols = st.columns(len(machines))
    for i, machine in enumerate(machines):
        prob = float(risk_data[risk_data["machine_name"]==machine]["ml_prob"].values[0])
        fig_g = go.Figure(go.Indicator(
            mode  = "gauge+number",
            value = prob * 100,
            title = {"text": machine, "font": {"size": 12}},
            number= {"suffix": "%", "font": {"size": 20}},
            gauge = {
                "axis":  {"range": [0,100], "tickwidth":1},
                "bar":   {"color": risk_color(prob*100) if prob*100>8 else "#2ecc71"},
                "steps": [
                    {"range":[0,40],  "color":"#1a2a1a"},
                    {"range":[40,70], "color":"#2a2010"},
                    {"range":[70,100],"color":"#2a1010"},
                ],
                "threshold":{"line":{"color":"white","width":2},"value":50},
            },
        ))
        fig_g.update_layout(height=200, margin=dict(t=30,b=0,l=20,r=20),
                            paper_bgcolor="#0e1117", font_color="#c0c0c0")
        cols[i].plotly_chart(fig_g, use_container_width=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<p class="section-title">Probability Distribution</p>', unsafe_allow_html=True)
        fig = px.histogram(
            df, x="ml_prob", color=TARGET_COL, nbins=40,
            color_discrete_map={0:"#2ecc71", 1:"#e74c3c"},
            labels={"ml_prob":"Fault Probability", TARGET_COL:"Actual"},
            barmode="overlay", opacity=0.75,
        )
        fig.add_vline(x=0.5, line_dash="dash", annotation_text="Threshold")
        fig.update_layout(height=300, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                          font_color="#c0c0c0", margin=dict(t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        if "fault_type" in df.columns:
            st.markdown('<p class="section-title">Fault Type Breakdown</p>', unsafe_allow_html=True)
            fault_df = df[df[TARGET_COL]==1]
            fig2 = px.pie(fault_df, names="fault_type",
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig2.update_layout(height=300, paper_bgcolor="#0e1117",
                               font_color="#c0c0c0", margin=dict(t=10,b=10))
            st.plotly_chart(fig2, use_container_width=True)

    # High-risk records table
    st.markdown('<p class="section-title">High-Risk Records (Prob > 70%)</p>', unsafe_allow_html=True)
    high_risk = df[df["ml_prob"] > 0.7][
        ["timestamp","machine_name","temperature","pressure","output_rate","ml_prob"]
    ].copy()
    high_risk["ml_prob"] = (high_risk["ml_prob"]*100).round(1).astype(str) + "%"
    high_risk = high_risk.sort_values("ml_prob", ascending=False).head(20)
    st.dataframe(high_risk.reset_index(drop=True), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 3 — SENSOR ANALYTICS
# ══════════════════════════════════════════════════════════════════════════
elif "Sensor" in page:
    st.markdown("# 📊 Sensor Analytics")
    st.markdown("---")

    machine_sel = st.selectbox("Select machine", ["All"] + machines)
    df_view = df if machine_sel == "All" else df[df["machine_name"]==machine_sel]

    # Temperature over time
    st.markdown('<p class="section-title">Temperature Over Time</p>', unsafe_allow_html=True)
    fig_t = px.line(df_view, x="timestamp", y="temperature", color="machine_name",
                    labels={"temperature":"Temperature (°C)","timestamp":""},
                    color_discrete_sequence=px.colors.qualitative.Plotly)
    fault_times = df_view[df_view[TARGET_COL]==1]["timestamp"]
    for ft in fault_times[:30]:   # mark first 30 faults
        fig_t.add_vline(x=ft, line_color="red", line_width=0.5, opacity=0.3)
    fig_t.update_layout(height=300, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                        font_color="#c0c0c0", margin=dict(t=10,b=10))
    st.plotly_chart(fig_t, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<p class="section-title">Temperature vs Output Rate</p>', unsafe_allow_html=True)
        fig2 = px.scatter(
            df_view, x="temperature", y="output_rate", color=TARGET_COL,
            color_discrete_map={0:"#2ecc71",1:"#e74c3c"},
            opacity=0.6, labels={"temperature":"Temp (°C)","output_rate":"Output (uph)"},
        )
        fig2.update_layout(height=320, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           font_color="#c0c0c0", margin=dict(t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        st.markdown('<p class="section-title">Pressure vs Temperature</p>', unsafe_allow_html=True)
        fig3 = px.scatter(
            df_view, x="pressure", y="temperature", color=TARGET_COL,
            color_discrete_map={0:"#2ecc71",1:"#e74c3c"},
            opacity=0.6, labels={"pressure":"Pressure (bar)","temperature":"Temp (°C)"},
        )
        fig3.update_layout(height=320, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                           font_color="#c0c0c0", margin=dict(t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<p class="section-title">Sensor Distribution: Normal vs Fault</p>', unsafe_allow_html=True)
    sensor = st.selectbox("Sensor", ["temperature","pressure","operating_time","output_rate"])
    fig4 = px.box(df_view, x="machine_name", y=sensor, color=TARGET_COL,
                  color_discrete_map={0:"#2ecc71",1:"#e74c3c"},
                  labels={TARGET_COL:"Fault"})
    fig4.update_layout(height=350, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                       font_color="#c0c0c0", margin=dict(t=10,b=10))
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# PAGE 4 — RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════
elif "Recommend" in page:
    st.markdown("# ⚙️ Workflow Recommendations")
    st.markdown("---")

    # OEE
    st.markdown('<p class="section-title">Overall Equipment Effectiveness (OEE)</p>', unsafe_allow_html=True)
    theoretical_max = df["output_rate"].quantile(0.95)
    oee_rows = []
    for _, row in stats.iterrows():
        avail  = max(0.5, 1 - (row["fault_count"] * 10) / (row["total_records"] * 480 / 12))
        perf   = min(1.0, row["avg_output"] / theoretical_max)
        qual   = 1 - (row["fault_rate_pct"] / 100)
        oee    = avail * perf * qual * 100
        oee_rows.append({"Machine": row["machine_name"],
                          "Availability": f"{avail*100:.1f}%",
                          "Performance":  f"{perf*100:.1f}%",
                          "Quality":      f"{qual*100:.1f}%",
                          "OEE":          f"{oee:.1f}%",
                          "_oee_val":     oee})

    oee_df = pd.DataFrame(oee_rows)
    fig_oee = px.bar(
        oee_df, x="Machine", y="_oee_val",
        color="_oee_val", color_continuous_scale="RdYlGn",
        labels={"_oee_val":"OEE %","Machine":""}, range_y=[0,100],
    )
    fig_oee.add_hline(y=85, line_dash="dot", line_color="white",
                      annotation_text="World-class = 85%")
    fig_oee.update_layout(height=300, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                          font_color="#c0c0c0", showlegend=False, margin=dict(t=10,b=10))
    st.plotly_chart(fig_oee, use_container_width=True)
    st.dataframe(oee_df.drop(columns=["_oee_val"]), use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">Machine Recommendations</p>', unsafe_allow_html=True)

    # Sort machines by fault rate descending
    for _, row in stats.sort_values("fault_rate_pct", ascending=False).iterrows():
        rate  = row["fault_rate_pct"]
        color = risk_color(rate)
        label = risk_label(rate)
        icon  = "🔴" if rate>15 else "🟠" if rate>8 else "🟢"

        if rate > 15:
            action = "Schedule immediate maintenance · Reduce load by 20% · Inspect all sensors"
        elif rate > 8:
            action = "Monitor closely · Plan maintenance this week · Check lubrication"
        else:
            action = "Continue normal operation · Route priority orders here"

        ml_risk = ""
        if model:
            m_prob = df[df["machine_name"]==row["machine_name"]]["ml_prob"].mean()*100
            if m_prob > 70:
                ml_risk = f"  |  AI Risk: **{m_prob:.0f}%** — Reduce load / Maintenance required"
            elif m_prob > 40:
                ml_risk = f"  |  AI Risk: **{m_prob:.0f}%** — Monitor closely"
            else:
                ml_risk = f"  |  AI Risk: **{m_prob:.0f}%** — Normal"

        st.markdown(f"""
        <div class="recommend-box" style="border-left-color:{color}">
            <b>{icon} {row['machine_name']}</b> — <span style="color:{color}">{label}</span><br>
            <small>Fault rate: {rate}%  ·  Avg output: {row['avg_output']:.0f} uph{ml_risk}</small><br>
            <small style="color:#8892a4">→ {action}</small>
        </div>
        """, unsafe_allow_html=True)

    # Best machine callout
    best = stats.sort_values("avg_output", ascending=False).iloc[0]
    st.markdown("---")
    st.success(f"**Optimal routing:** Send priority orders to **{best['machine_name']}** "
               f"(highest output: {best['avg_output']:.0f} uph, fault rate: {best['fault_rate_pct']}%)")

# ══════════════════════════════════════════════════════════════════════════
# PAGE 5 — LIVE PREDICT
# ══════════════════════════════════════════════════════════════════════════
elif "Live" in page:
    st.markdown("# 🎛️ Live Sensor Prediction")
    st.markdown("Enter current sensor readings to get an instant AI fault assessment.")
    if not model:
        st.error("Train the model first: `python ml/model_xgb.py --model rf --csv data/sensor_data.csv`")
        st.stop()

    st.markdown("---")
    c1, c2 = st.columns(2)
    machine_name = c1.selectbox("Machine", machines)
    temp    = c1.slider("Temperature (°C)",    20.0, 180.0, 75.0, 0.5)
    press   = c1.slider("Pressure (bar)",       0.5,  18.0,  5.0, 0.1)
    op_time = c2.slider("Operating Time (hrs)", 1.0,  24.0,  6.0, 0.1)
    output  = c2.slider("Output Rate (uph)",    5.0, 280.0,100.0, 1.0)

    if c2.button("Run AI Prediction", type="primary", use_container_width=True):
        tpr  = temp / (press + 1e-6)
        eff  = output / (op_time + 1e-6)
        X    = np.array([[temp, press, op_time, output, tpr, eff]], dtype=np.float32)
        prob = float(model.predict_proba(X)[0][1])

        # Rule-based safety net
        if (temp > 110 or press < 2.0 or output < 40) and prob < 0.5:
            prob = max(prob, 0.65)

        # Optimization logic (guide's key feature)
        if prob > 0.7:
            decision = "Reduce load / Maintenance required"
            d_color  = "#e74c3c"
            icon     = "🔴"
        elif prob > 0.4:
            decision = "Monitor closely / Schedule inspection"
            d_color  = "#f39c12"
            icon     = "🟠"
        else:
            decision = "Normal operation. No action needed."
            d_color  = "#2ecc71"
            icon     = "🟢"

        st.markdown("---")
        c1r, c2r, c3r = st.columns(3)
        c1r.metric("Machine",    machine_name)
        c2r.metric("Fault Probability", f"{prob*100:.1f}%")
        c3r.metric("Status",     "⚠️ FAULT RISK" if prob>=0.5 else "✅ NORMAL")

        st.markdown(f"""
        <div class="recommend-box" style="border-left-color:{d_color};font-size:1.05rem;padding:18px 22px">
            {icon} <b>AI Decision:</b> {decision}
        </div>
        """, unsafe_allow_html=True)

        col_g, col_b = st.columns([1, 1])
        with col_g:
            fig = go.Figure(go.Indicator(
                mode  = "gauge+number",
                value = prob * 100,
                title = {"text": "Fault Risk %"},
                number= {"suffix":"%"},
                gauge = {
                    "axis":  {"range":[0,100]},
                    "bar":   {"color": d_color},
                    "steps": [
                        {"range":[0,40],  "color":"#1a2a1a"},
                        {"range":[40,70], "color":"#2a2010"},
                        {"range":[70,100],"color":"#2a1010"},
                    ],
                    "threshold":{"line":{"color":"white","width":3},"value":50},
                },
            ))
            fig.update_layout(height=300, paper_bgcolor="#0e1117",
                              font_color="#c0c0c0", margin=dict(t=30,b=0))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            # Show how this reading compares to historical
            m_df = df[df["machine_name"]==machine_name]
            fig2 = go.Figure()
            fig2.add_trace(go.Box(
                y=m_df["temperature"], name="Historical",
                marker_color="#4c6ef5", boxmean=True
            ))
            fig2.add_trace(go.Scatter(
                x=["Historical"], y=[temp],
                mode="markers", name="Your reading",
                marker=dict(color=d_color, size=14, symbol="diamond"),
            ))
            fig2.update_layout(
                title="Your Temperature vs Historical",
                height=300, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                font_color="#c0c0c0", margin=dict(t=40,b=10),
                showlegend=True,
            )
            st.plotly_chart(fig2, use_container_width=True)
