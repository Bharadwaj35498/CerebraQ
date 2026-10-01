import os
import torch
import numpy as np
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

from dataset import CerebraQDataset
from model import CerebraQCNN

MANIFEST = r".\data\processed\dataset_manifest.csv"
CHECKPOINT = r".\reports\checkpoints\classical_cnn_best.pt"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device:", device)

model = CerebraQCNN().to(device)

checkpoint = torch.load(CHECKPOINT, map_location=device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

print("Loaded best checkpoint")
print("Best epoch:", checkpoint["epoch"])
print("Best validation loss:", checkpoint["val_loss"])

def evaluate(split):
    dataset = CerebraQDataset(MANIFEST, split)
    loader = DataLoader(dataset, batch_size=16, shuffle=False)

    y_true = []
    y_pred = []
    y_prob = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)

            logits = model(images)
            probs = torch.sigmoid(logits)

            preds = (probs >= 0.5).float()

            y_true.extend(labels.numpy())
            y_pred.extend(preds.cpu().numpy())
            y_prob.extend(probs.cpu().numpy())

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    print("\n" + "=" * 60)
    print(split.upper(), "SET")
    print("=" * 60)

    print("Patients :", len(dataset))
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print("\nConfusion Matrix")
    print(cm)

    print("\nClassification Report")
    print(classification_report(
        y_true,
        y_pred,
        target_names=["LGG", "HGG"],
        zero_division=0
    ))

evaluate("val")
evaluate("test")
