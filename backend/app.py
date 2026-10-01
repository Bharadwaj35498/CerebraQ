import os
import json
from flask import Flask, jsonify

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "reports",
    "patient_reports"
)

EXPLANATION_DIR = os.path.join(
    PROJECT_ROOT,
    "reports",
    "explainability"
)

app = Flask(__name__)


# =========================================================
# Health check
# =========================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "project": "CerebraQ",
        "service": "CerebraQ Backend API"
    })


# =========================================================
# List available analysed patients
# =========================================================

@app.route("/api/patients", methods=["GET"])
def patients():

    patients = []

    if os.path.exists(REPORT_DIR):

        for filename in os.listdir(REPORT_DIR):

            if filename.endswith("_report.json"):

                patient_id = filename.replace(
                    "_report.json",
                    ""
                )

                patients.append(
                    patient_id
                )

    return jsonify({
        "count": len(patients),
        "patients": patients
    })


# =========================================================
# Get patient report
# =========================================================

@app.route("/api/patient/<patient_id>", methods=["GET"])
def patient_report(patient_id):

    report_path = os.path.join(
        REPORT_DIR,
        f"{patient_id}_report.json"
    )

    if not os.path.exists(report_path):

        return jsonify({
            "error": "Patient report not found",
            "patient_id": patient_id
        }), 404

    with open(
        report_path,
        "r",
        encoding="utf-8"
    ) as f:

        report = json.load(f)

    return jsonify(report)


# =========================================================
# Get explanation information
# =========================================================

@app.route(
    "/api/explanation/<patient_id>",
    methods=["GET"]
)
def explanation(patient_id):

    image_path = os.path.join(
        EXPLANATION_DIR,
        f"{patient_id}_explainability.png"
    )

    exists = os.path.exists(
        image_path
    )

    return jsonify({
        "patient_id": patient_id,
        "available": exists,
        "filename":
            f"{patient_id}_explainability.png"
    })


# =========================================================
# Model performance
# =========================================================

@app.route("/api/metrics", methods=["GET"])
def metrics():

    return jsonify({

        "classical_cnn": {
            "accuracy": 0.8140,
            "precision": 0.8286,
            "recall": 0.9355,
            "f1": 0.8788
        },

        "cerebraq": {
            "accuracy": 0.8372,
            "precision": 0.8529,
            "recall": 0.9355,
            "f1": 0.8923
        },

        "cerebraq_no_qft": {
            "accuracy": 0.8837,
            "precision": 0.9062,
            "recall": 0.9355,
            "f1": 0.9206
        },

        "cerebraq_no_entanglement": {
            "accuracy": 0.8605,
            "precision": 0.8788,
            "recall": 0.9355,
            "f1": 0.9062
        },

        "cerebraq_direct_angle_injection": {
            "accuracy": 0.7442,
            "precision": 0.8571,
            "recall": 0.7742,
            "f1": 0.8136
        }

    })


# =========================================================
# Run server
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CEREBRAQ BACKEND API")
    print("=" * 60)

    print("Project root:", PROJECT_ROOT)
    print("Report directory:", REPORT_DIR)

    print()
    print("Starting server...")
    print("API: http://127.0.0.1:5000")

    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
