# Smart Production AI-Agent Walkthrough

**Product:** Smart_Production

**Author:** By:- URVIT JAJOO

**Video:** `smart_production_demo.mp4`

This guide follows the synchronized cursor walkthrough in the demo video. The visible cursor and click ripple represent an AI operations agent moving through the cockpit and opening each production-control function.

## Step 1 — Overview

The Overview page is the command center. It summarizes total records, active machines, total fault events, fleet fault rate, and average output in the KPI row. Machine health cards then compare fault rate, production output, and AI risk for each asset. The production charts provide a fleet-level view of fault concentration, average output, and output behavior over time.

The operator uses this page first to understand whether the factory is healthy, which machine needs attention, and whether production is trending normally.

## Step 2 — Failure Predictions

Failure Predictions turns sensor readings into maintenance priorities. It presents fault probability, predicted fault status, high-risk records, missed faults, model metrics, risk gauges, probability distributions, and fault-type breakdowns. High-risk records can be reviewed before a failure becomes an unplanned stoppage.

The purpose is not only to classify a fault, but to give maintenance and production teams an ordered view of where intervention is most urgent.

## Step 3 — Sensor Analytics

Sensor Analytics examines temperature, pressure, operating time, output rate, machine comparisons, fault markers, and sensor distributions. Trends expose gradual drift, while scatter and box plots help compare normal and fault conditions.

This page supports root-cause investigation. An operator can determine whether a fault is associated with overheating, pressure loss, reduced output, abnormal operating time, or a combination of signals.

## Step 4 — OEE, Shifts, Correlation, and Alerts

The OEE Report combines availability, performance, and quality into an equipment-effectiveness view. Shift Comparison shows how day, evening, and night operations differ. Correlation Matrix helps identify relationships between sensors and production outcomes. Alerts collect active risks that require follow-up.

Together, these functions connect machine health to operational performance. The management question becomes clear: where is capacity being lost, during which shift, and because of which measurable condition?

## Step 5 — Shot Peening

The Shot Peening module is the dedicated special-process workspace. Process Overview tracks parts, pass rate, media age, jobs queued, and daily production. Process Parameters monitor pressure, flow, and run behavior. Almen Intensity provides saturation-curve and historical intensity views. Coverage & Quality tracks surface results and roughness before and after processing.

The module also contains a Work Order Tracker, Planning Data, Spec Checker, Job Log, and Insert Job workflow. These functions connect customer work orders, part identity, peening location, setup, cycle time, loss categories, throughput, remarks, and process acceptance. The result is a traceable special-process record rather than a standalone machine chart.

## Step 6 — CNC Machining

The CNC Machining module monitors the machining cell. It shows cell records, spindle utilization, average output, fault rate, and high tool-wear risk. Individual machine cards expose spindle rating, coolant type, motor temperature, coolant pressure, and output rate.

Tooling & Wear, Job Log, Standards Reference, and Insert Job functions extend the page from monitoring into action. The operator can connect output degradation or fault trends to tooling condition, coolant behavior, job history, or a required insert change.

## Step 7 — Quality and Compliance

Quality & Compliance centralizes open NCRs, root-cause categories, dispositions, NCR trends, calibration status, and instrument registers. It also displays management-system certifications, including AS9100D, ISO 9001:2015, ISO 14001, and NADCAP.

NADCAP is shown in the context of special processes such as heat treatment, non-destructive testing, and shot peening. The page therefore links shop-floor process evidence with audit readiness, calibration control, non-conformance handling, and certification scope.

## Step 8 — Live Predict

Live Predict accepts a current sensor reading and returns a fault probability, risk level, predicted fault type, and recommended action. The result can be used for an immediate check during production or maintenance troubleshooting.

The workflow is intentionally simple: enter the current values, run the model, review the risk gauge, and follow the suggested action. This provides an operational entry point for the trained machine-learning model.

## Step 9 — Raw Data and AI Assistant

Raw Data provides searchable and filterable production records. Operators can inspect the underlying measurements, export full datasets, export faults, export high-risk records, and generate OEE reports.

The AI Assistant provides a conversational layer over the production context. Typical questions include why downtime increased, which machine requires maintenance, what process improvement should be tested, and how to summarize the current production condition.

## Step 10 — Advanced Operations

The Advanced Modules connect the cockpit to wider digital-manufacturing functions. Digital Twin represents the production environment, Computer Vision supports visual inspection concepts, ERP Integration connects production records to planning and enterprise systems, Supply Chain extends visibility beyond the plant, and Sustainability supports environmental and resource tracking.

These modules establish the path from an asset-level predictive-maintenance tool to an integrated operations platform.

## Step 11 — Predictive Quality

Predictive Quality links process parameters, inspection information, sensor behavior, and quality risk. Its purpose is to identify conditions that precede recurring defects, rather than waiting for an NCR after the fact.

For special processes, this can connect intensity, pressure, flow, coverage, material condition, inspection results, and part history to quality outcomes. The expected result is earlier containment and more consistent process capability.

## Step 12 — Executive Dashboard

The Executive Dashboard condenses delivery, quality, cost, capacity, compliance, and improvement priorities into a management view. It is intended for review meetings and escalation decisions rather than detailed operator diagnosis.

Leadership can move from the executive summary into the underlying OEE, machine, special-process, work-order, quality, and compliance evidence when a result requires investigation.

## End-to-End Operating Sequence

The recommended workflow is to begin with Overview, identify risk in Failure Predictions, investigate signals in Sensor Analytics, quantify the operational effect through OEE and shifts, inspect the relevant process module, validate Quality & Compliance status, and then use Live Predict or the AI Assistant for an immediate decision. Raw Data and exports provide traceability, while the advanced and executive modules support broader planning and governance.

This creates a closed loop from **sensor data**, to **AI risk**, to **production action**, to **quality evidence**, and finally to **management improvement priorities**.
