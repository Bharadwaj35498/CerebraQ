import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, PROJECT_ROOT)

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from classical.dataset import CerebraQDataset
from hybrid.model_no_entanglement import CerebraQNoEntanglement


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

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)

train_dataset = CerebraQDataset(MANIFEST, "train")
val_dataset = CerebraQDataset(MANIFEST, "val")

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

model = CerebraQNoEntanglement().to(device)

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
patience_counter = 0

checkpoint_path = os.path.join(
    CHECKPOINT_DIR,
    "cerebraq_no_entanglement_best.pt"
)

for epoch in range(1, EPOCHS + 1):

    model.train()
    train_loss = 0.0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        logits = model(images)

        loss = criterion(
            logits,
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

            logits = model(images)

            loss = criterion(
                logits,
                labels
            )

            val_loss += (
                loss.item() * images.size(0)
            )

    val_loss /= len(val_dataset)

    print(
        f"Epoch {epoch:02d}/{EPOCHS} | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {val_loss:.4f}"
    )

    if val_loss < best_val_loss:

        best_val_loss = val_loss
        patience_counter = 0

        torch.save(
            {
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "val_loss": val_loss
            },
            checkpoint_path
        )

        print("  ? Saved best No-Entanglement model")

    else:

        patience_counter += 1

        if patience_counter >= PATIENCE:

            print(
                f"\nEarly stopping after epoch {epoch}."
            )
            break


print("\nNo-Entanglement training complete.")
print(
    f"Best validation loss: {best_val_loss}"
)
print(
    f"Checkpoint: {checkpoint_path}"
)
