import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from dataset import CerebraQDataset
from model import CerebraQCNN


MANIFEST = r".\data\processed\dataset_manifest.csv"
CHECKPOINT_DIR = r".\reports\checkpoints"

BATCH_SIZE = 16
EPOCHS = 30
LEARNING_RATE = 1e-3

os.makedirs(CHECKPOINT_DIR, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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


model = CerebraQCNN().to(device)

# 147 HGG / 52 LGG
# Positive class = HGG
pos_weight = torch.tensor([147 / 52], device=device)

criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)

best_val_loss = float("inf")


for epoch in range(EPOCHS):

    # -------------------------
    # Training
    # -------------------------
    model.train()

    train_loss = 0.0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        train_loss += loss.item() * images.size(0)

    train_loss /= len(train_dataset)

    # -------------------------
    # Validation
    # -------------------------
    model.eval()

    val_loss = 0.0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(outputs, labels)

            val_loss += loss.item() * images.size(0)

    val_loss /= len(val_dataset)

    print(
        f"Epoch {epoch + 1:02d}/{EPOCHS} | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {val_loss:.4f}"
    )

    # Save best model
    if val_loss < best_val_loss:

        best_val_loss = val_loss

        checkpoint = os.path.join(
            CHECKPOINT_DIR,
            "classical_cnn_best.pt"
        )

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "epoch": epoch + 1,
                "val_loss": val_loss
            },
            checkpoint
        )

        print("  ✓ Saved best model")


print("\nTraining complete.")
print("Best validation loss:", best_val_loss)