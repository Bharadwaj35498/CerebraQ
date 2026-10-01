import torch
import torch.nn as nn

from quantum.circuit_no_entanglement import (
    quantum_layer_no_entanglement
)


class ClassicalFeatureExtractor(nn.Module):

    def __init__(self):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(4, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),

            nn.AdaptiveAvgPool2d((1, 1))
        )

        self.projection = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 16)
        )

    def forward(self, x):
        x = self.features(x)
        return self.projection(x)


class CerebraQNoEntanglement(nn.Module):

    def __init__(self):
        super().__init__()

        self.classical = ClassicalFeatureExtractor()

        self.quantum = quantum_layer_no_entanglement

        self.classifier = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(16, 1)
        )

    def forward(self, x):

        classical_features = self.classical(x)

        quantum_features = self.quantum(
            classical_features
        )

        output = self.classifier(
            quantum_features
        )

        return output.squeeze(1)
