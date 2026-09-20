# api/flask_api.py
# Optional REST API -- lets external systems POST sensor readings and get predictions.
#
# Run : python api/flask_api.py
# Test:
#   curl -X POST http://localhost:5000/predict \
#     -H "Content-Type: application/json" \
#     -d '{"temperature_c":130,"vibration_mms":1.5,"pressure_bar":5.0,
#          "current_a":13.0,"cycle_time_s":3.5,"output_rate_uph":100}'

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ml"))

from flask import Flask, request, jsonify
from model import predict_live, load_model

app = Flask(__name__)

REQUIRED = [
    "temperature_c", "vibration_mms", "pressure_bar",
    "current_a", "cycle_time_s", "output_rate_uph",
]


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "Smart Production Optimization API",
        "endpoints": {
            "POST /predict": "Predict fault from sensor readings",
            "GET  /health":  "Service health check",
        }
    })


@app.route("/health", methods=["GET"])
def health():
    try:
        load_model()
        model_status = "ready"
    except FileNotFoundError:
        model_status = "not_trained -- run: python ml/model.py train"
    return jsonify({"status": "ok", "model": model_status})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    missing = [f for f in REQUIRED if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        result = predict_live({k: float(data[k]) for k in REQUIRED})
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("[flask_api] Running at http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
