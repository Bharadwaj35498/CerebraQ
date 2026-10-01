import os
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


class CerebraQDataset(Dataset):
    def __init__(self, manifest_path, split):
        self.df = pd.read_csv(manifest_path)
        self.df = self.df[self.df["split"] == split].reset_index(drop=True)

        self.label_map = {"LGG": 0, "HGG": 1}

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        data = np.load(row["processed_path"])

        image = data["image"].astype(np.float32)

        # (4, 64, 64)
        image = torch.from_numpy(image)

        label = self.label_map[row["Grade"]]
        label = torch.tensor(label, dtype=torch.float32)

        return image, label