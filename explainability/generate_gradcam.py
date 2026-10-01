import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt

from classical.dataset import CerebraQDataset
from hybrid.model import CerebraQHybrid
from explainability.gradcam import GradCAM


# =========================================================
# Paths
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

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "reports",
    "explainability"
)

os.makedirs(
    OUTPUT_DIR,
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
# Dataset
# =========================================================

dataset = CerebraQDataset(
    MANIFEST,
    "test"
)

print(
    "Test patients:",
    len(dataset)
)


# =========================================================
# Load trained CerebraQ model
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
# Target final convolutional layer
# =========================================================

target_layer = model.classical.features[8]

print(
    "Grad-CAM target layer:"
)

print(target_layer)


# =========================================================
# Create Grad-CAM
# =========================================================

gradcam = GradCAM(
    model,
    target_layer
)


# =========================================================
# Select test patient
# =========================================================

patient_index = 0

image, label = dataset[patient_index]

image = image.unsqueeze(0).to(device)

true_label = int(label)


# =========================================================
# Prediction
# =========================================================

with torch.no_grad():

    logit = model(image)

    probability = torch.sigmoid(
        logit
    ).item()


prediction = (
    1
    if probability >= 0.5
    else 0
)


# =========================================================
# Generate Grad-CAM
# =========================================================

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

mri = (
    image[0]
    .detach()
    .cpu()
    .numpy()
)


# =========================================================
# Read manifest
# =========================================================

manifest_df = pd.read_csv(
    MANIFEST
)

test_df = manifest_df[
    manifest_df["split"] == "test"
].reset_index(drop=True)


patient_id = test_df.iloc[
    patient_index
]["BraTS2023"]

processed_path = test_df.iloc[
    patient_index
]["processed_path"]


# =========================================================
# Locate processed NPZ
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


# =========================================================
# Modality names
# =========================================================

modality_names = [
    "T1 Native",
    "T1 Contrast",
    "T2 Weighted",
    "FLAIR"
]


# =========================================================
# Labels
# =========================================================

prediction_name = (
    "HGG"
    if prediction == 1
    else "LGG"
)

true_name = (
    "HGG"
    if true_label == 1
    else "LGG"
)


# =========================================================
# Create figure
# =========================================================

fig, axes = plt.subplots(
    2,
    4,
    figsize=(16, 8)
)


# =========================================================
# MRI modalities
# =========================================================

for i in range(4):

    ax = axes[0, i]

    ax.imshow(
        mri[i],
        cmap="gray"
    )

    ax.set_title(
        modality_names[i]
    )

    ax.axis("off")


# =========================================================
# Tumour ROI
# =========================================================

ax = axes[1, 0]

ax.imshow(
    mri[1],
    cmap="gray"
)

ax.imshow(
    tumor_mask,
    cmap="gray",
    alpha=0.45
)

ax.set_title(
    "Tumour ROI"
)

ax.axis("off")


# =========================================================
# Grad-CAM
# =========================================================

ax = axes[1, 1]

ax.imshow(
    mri[1],
    cmap="gray"
)

ax.imshow(
    cam,
    cmap="jet",
    alpha=0.50,
    vmin=0,
    vmax=1
)

ax.set_title(
    "CerebraQ Grad-CAM"
)

ax.axis("off")


# =========================================================
# FLAIR + Grad-CAM + tumour boundary
# =========================================================

ax = axes[1, 2]

ax.imshow(
    mri[3],
    cmap="gray"
)

ax.imshow(
    cam,
    cmap="jet",
    alpha=0.45,
    vmin=0,
    vmax=1
)

ax.contour(
    tumor_mask,
    levels=[0.5],
    linewidths=1.5
)

ax.set_title(
    "FLAIR + Explanation"
)

ax.axis("off")


# =========================================================
# Result panel
# =========================================================

ax = axes[1, 3]

ax.axis("off")

result_text = (
    "CerebraQ RESULT\n\n"
    "Prediction: " + prediction_name + "\n\n"
    "HGG Probability: "
    + f"{probability:.2%}"
    + "\n\n"
    "Ground Truth: " + true_name + "\n\n"
    "Patient: " + str(patient_id)
)

ax.text(
    0.05,
    0.50,
    result_text,
    fontsize=13,
    verticalalignment="center"
)


# =========================================================
# Figure title
# =========================================================

fig.suptitle(
    "CerebraQ - Explainable Brain MRI Analysis",
    fontsize=16
)

plt.tight_layout()


# =========================================================
# Save
# =========================================================

output_path = os.path.join(
    OUTPUT_DIR,
    f"{patient_id}_explainability.png"
)

plt.savefig(
    output_path,
    dpi=200,
    bbox_inches="tight"
)

plt.close()


# =========================================================
# Cleanup
# =========================================================

gradcam.remove_hooks()


# =========================================================
# Final output
# =========================================================

print("\n" + "=" * 60)

print("EXPLAINABILITY COMPLETE")

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
    f"HGG Probability: {probability:.2%}"
)

print(
    "Ground Truth:",
    true_name
)

print(
    "Saved:",
    output_path
)

print("=" * 60)