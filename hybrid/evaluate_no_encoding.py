import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, PROJECT_ROOT)

import torch
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from classical.dataset import CerebraQDataset
from hybrid.model_no_encoding import CerebraQNoEncoding


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
    "cerebraq_no_encoding_best.pt"
)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)

test_dataset = CerebraQDataset(
    MANIFEST,
    "test"
)

test_loader = DataLoader(
    test_dataset,
    batch_size=4,
    shuffle=False
)

print("Test patients:", len(test_dataset))

model = CerebraQNoEncoding().to(device)

checkpoint = torch.load(
    CHECKPOINT,
    map_location=device
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

all_labels = []
all_predictions = []

with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(device)

        logits = model(images)

        probabilities = torch.sigmoid(logits)

        predictions = (
            probabilities >= 0.5
        ).long()

        all_labels.extend(
            labels.cpu().numpy()
        )

        all_predictions.extend(
            predictions.cpu().numpy()
        )


accuracy = accuracy_score(
    all_labels,
    all_predictions
)

precision = precision_score(
    all_labels,
    all_predictions,
    zero_division=0
)

recall = recall_score(
    all_labels,
    all_predictions,
    zero_division=0
)

f1 = f1_score(
    all_labels,
    all_predictions,
    zero_division=0
)

cm = confusion_matrix(
    all_labels,
    all_predictions
)

print("\n" + "=" * 60)
print("NO-ENCODING TEST RESULTS")
print("=" * 60)

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(
    classification_report(
        all_labels,
        all_predictions,
        target_names=["LGG", "HGG"],
        zero_division=0
    )
)

print("=" * 60)
