import os
import sys
import json
from datetime import datetime

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

from classical.dataset import CerebraQDataset
from hybrid.model import CerebraQHybrid
from explainability.gradcam import GradCAM


# =========================================================
# Configuration
# =========================================================

MANIFEST = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "dataset_manifest.csv"
)

CHECKPOINT = os.path.join(
    PROJECT_ROOT,
    "reports",
    "checkpoints",
    "cerebraq_hybrid_best.pt"
)

EXPLANATION_DIR = os.path.join(
    PROJECT_ROOT,
    "reports",
    "explainability"
)

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "reports",
    "patient_reports"
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


# =========================================================
# Device
# =========================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)


# =========================================================
# Load dataset
# =========================================================

dataset = CerebraQDataset(
    MANIFEST,
    "test"
)

manifest_df = pd.read_csv(
    MANIFEST
)

test_df = manifest_df[
    manifest_df["split"] == "test"
].reset_index(drop=True)


# =========================================================
# Select patient
# =========================================================

patient_index = 0

image, label = dataset[
    patient_index
]

image = image.unsqueeze(0).to(device)

true_label = int(label)

patient_row = test_df.iloc[
    patient_index
]

patient_id = str(
    patient_row["BraTS2023"]
)

processed_path = str(
    patient_row["processed_path"]
)


# =========================================================
# Load model
# =========================================================

model = CerebraQHybrid().to(device)

checkpoint = torch.load(
    CHECKPOINT,
    map_location=device
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

print("Loaded CerebraQ checkpoint.")


# =========================================================
# Prediction
# =========================================================

with torch.no_grad():

    logit = model(image)

    hgg_probability = torch.sigmoid(
        logit
    ).item()


prediction = (
    1
    if hgg_probability >= 0.5
    else 0
)


prediction_name = (
    "HGG"
    if prediction == 1
    else "LGG"
)

ground_truth_name = (
    "HGG"
    if true_label == 1
    else "LGG"
)

model_confidence = (
    hgg_probability
    if prediction == 1
    else 1.0 - hgg_probability
)


# =========================================================
# Locate processed patient file
# =========================================================

npz_path = os.path.join(
    PROJECT_ROOT,
    processed_path
)

if not npz_path.endswith(".npz"):

    npz_path = os.path.join(
        npz_path,
        "processed_roi.npz"
    )


# =========================================================
# Load processed MRI data
# =========================================================

data = np.load(
    npz_path
)

tumor_mask = data["mask"]

tumor_pixels = int(
    np.sum(tumor_mask > 0)
)

total_pixels = int(
    tumor_mask.size
)

tumor_fraction = (
    tumor_pixels / total_pixels
    if total_pixels > 0
    else 0.0
)


# =========================================================
# Generate Grad-CAM
# =========================================================

target_layer = model.classical.features[8]

gradcam = GradCAM(
    model,
    target_layer
)

cam = gradcam.generate(
    image,
    target_class=prediction
)

cam = (
    cam[0, 0]
    .detach()
    .cpu()
    .numpy()
)

gradcam_mean = float(
    np.mean(cam)
)

gradcam_max = float(
    np.max(cam)
)

gradcam.remove_hooks()


# =========================================================
# Explanation image
# =========================================================

explanation_path = os.path.join(
    EXPLANATION_DIR,
    f"{patient_id}_explainability.png"
)


# =========================================================
# Build report data
# =========================================================

report = {

    "project": "CerebraQ",

    "project_description":
        "Explainable Hybrid Quantum-Classical "
        "Framework for Brain MRI Analysis",

    "patient_id":
        patient_id,

    "analysis_type":
        "Research prototype model analysis",

    "model_prediction": {
        "class": prediction_name,
        "hgg_probability": round(
            hgg_probability,
            6
        ),
        "model_confidence": round(
            model_confidence,
            6
        )
    },

    "ground_truth": {
        "class": ground_truth_name,
        "available": True
    },

    "mri_modalities": [
        "T1 Native",
        "T1 Contrast",
        "T2 Weighted",
        "FLAIR"
    ],

    "tumor_roi": {
        "tumor_pixels": tumor_pixels,
        "roi_pixels": total_pixels,
        "tumor_fraction": round(
            tumor_fraction,
            6
        )
    },

    "explainability": {
        "method": "Grad-CAM",
        "target_layer":
            "Final convolutional layer",
        "mean_activation":
            round(gradcam_mean, 6),
        "maximum_activation":
            round(gradcam_max, 6),
        "visualization":
            explanation_path
    },

    "system_note":
        "This output is a research-model prediction "
        "and is not a clinical diagnosis or a replacement "
        "for professional medical interpretation.",

    "generated_at":
        datetime.now().isoformat()
}


# =========================================================
# Save JSON report
# =========================================================

json_path = os.path.join(
    REPORT_DIR,
    f"{patient_id}_report.json"
)

with open(
    json_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


# =========================================================
# Create human-readable report
# =========================================================

text_path = os.path.join(
    REPORT_DIR,
    f"{patient_id}_report.txt"
)


report_text = f"""
============================================================
CEREBRAQ PATIENT ANALYSIS REPORT
============================================================

Project:
CerebraQ - Explainable Hybrid Quantum-Classical
Framework for Brain MRI Analysis

Patient ID:
{patient_id}

============================================================
MODEL PREDICTION
============================================================

Predicted Class:
{prediction_name}

HGG Probability:
{hgg_probability:.2%}

Model Confidence:
{model_confidence:.2%}

Ground Truth:
{ground_truth_name}

============================================================
MRI INPUT
============================================================

Modalities:
- T1 Native
- T1 Contrast
- T2 Weighted
- FLAIR

============================================================
TUMOUR ROI
============================================================

Tumour Pixels:
{tumor_pixels}

ROI Pixels:
{total_pixels}

Tumour Pixel Fraction:
{tumor_fraction:.2%}

============================================================
EXPLAINABILITY
============================================================

Method:
Grad-CAM

Target Layer:
Final convolutional layer

Mean Grad-CAM Activation:
{gradcam_mean:.4f}

Maximum Grad-CAM Activation:
{gradcam_max:.4f}

Explanation Visualization:
{explanation_path}

============================================================
SYSTEM INTERPRETATION
============================================================

The CerebraQ model produced an {prediction_name}
prediction for this patient.

The Grad-CAM visualization identifies image regions
associated with the model's prediction.

This visualization describes model behaviour and should
not be interpreted as proof of medical causality.

============================================================
IMPORTANT NOTE
============================================================

CerebraQ is a research prototype.

The model output is not a clinical diagnosis and is
not intended to replace professional medical interpretation.

============================================================
Generated:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
============================================================
"""


with open(
    text_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        report_text.strip()
    )


# =========================================================
# Console output
# =========================================================

print()
print("=" * 60)
print("PATIENT ANALYSIS COMPLETE")
print("=" * 60)

print(
    "Patient:",
    patient_id
)

print(
    "Prediction:",
    prediction_name
)

print(
    f"HGG Probability: {hgg_probability:.2%}"
)

print(
    f"Model Confidence: {model_confidence:.2%}"
)

print(
    "Ground Truth:",
    ground_truth_name
)

print(
    "Tumour Pixels:",
    tumor_pixels
)

print()
print("JSON Report:")
print(json_path)

print()
print("Text Report:")
print(text_path)

print("=" * 60)
