import torch
import torch.nn as nn

from quantum.circuit_no_encoding import quantum_layer_no_encoding


class ClassicalFeatureExtractor(nn.Module):

    def __init__(self):

        super().__init__()

        self.features = nn.Sequential(

            nn.Conv2d(
                4, 32,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(
                32, 64,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(
                64, 128,
                kernel_size=3,
                padding=1
            ),

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


class CerebraQNoEncoding(nn.Module):

    def __init__(self):

        super().__init__()

        self.classical = ClassicalFeatureExtractor()

        self.quantum = quantum_layer_no_encoding

        self.classifier = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(16, 1)
        )

    def forward(self, x):

        # Classical CNN runs on CUDA.
        classical_features = self.classical(x)

        quantum_outputs = []

        for sample in classical_features:

            # PennyLane default.qubit is CPU based.
            # Move the individual feature vector to CPU.
            sample_cpu = sample.to("cpu")

            quantum_result = self.quantum(
                sample_cpu
            )

            # Move quantum result back to the
            # same device as the classical branch.
            quantum_result = quantum_result.to(
                classical_features.device
            )

            quantum_outputs.append(
                quantum_result
            )

        quantum_features = torch.stack(
            quantum_outputs
        )

        output = self.classifier(
            quantum_features
        )

        return output.squeeze(1)
