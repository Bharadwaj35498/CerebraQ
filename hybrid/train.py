import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from classical.dataset import CerebraQDataset
from hybrid.model import CerebraQHybrid


MANIFEST = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "dataset_manifest.csv"
)

CHECKPOINT_DIR = os.path.join(
    PROJECT_ROOT,
    "reports",
    "checkpoints"
)

BATCH_SIZE = 4
EPOCHS = 20
LEARNING_RATE = 1e-3
PATIENCE = 5

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)

train_dataset = CerebraQDataset(
    MANIFEST,
    "train"
)

val_dataset = CerebraQDataset(
    MANIFEST,
    "val"
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)

print("Training patients:", len(train_dataset))
print("Validation patients:", len(val_dataset))

model = CerebraQHybrid().to(device)

pos_weight = torch.tensor(
    [147 / 52],
    device=device
)

criterion = nn.BCEWithLogitsLoss(
    pos_weight=pos_weight
)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)

best_val_loss = float("inf")
epochs_without_improvement = 0

checkpoint_path = os.path.join(
    CHECKPOINT_DIR,
    "cerebraq_hybrid_best.pt"
)

for epoch in range(EPOCHS):

    model.train()

    train_loss = 0.0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()

        optimizer.step()

        train_loss += (
            loss.item() * images.size(0)
        )

    train_loss /= len(train_dataset)

    model.eval()

    val_loss = 0.0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            val_loss += (
                loss.item() * images.size(0)
            )

    val_loss /= len(val_dataset)

    print(
        f"Epoch {epoch + 1:02d}/{EPOCHS} | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {val_loss:.4f}"
    )

    if val_loss < best_val_loss:

        best_val_loss = val_loss
        epochs_without_improvement = 0

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "epoch": epoch + 1,
                "val_loss": val_loss
            },
            checkpoint_path
        )

        print("  ? Saved best hybrid model")

    else:

        epochs_without_improvement += 1

    if epochs_without_improvement >= PATIENCE:

        print(
            f"\nEarly stopping after epoch {epoch + 1}."
        )

        break


print("\nHybrid training complete.")
print("Best validation loss:", best_val_loss)
print("Checkpoint:", checkpoint_path)
