import pennylane as qml
from pennylane import numpy as np

N_QUBITS = 4
N_LAYERS = 2

dev = qml.device("default.qubit", wires=N_QUBITS)


def quantum_circuit(inputs, weights):
    """
    Differentiable CerebraQ quantum feature extractor.

    16 classical features
        -> amplitude encoding
        -> Hadamard
        -> trainable RY rotations
        -> CZ entanglement
        -> QFT
        -> Pauli-Z measurements
    """

    qml.AmplitudeEmbedding(
        inputs,
        wires=range(N_QUBITS),
        normalize=True
    )

    for wire in range(N_QUBITS):
        qml.Hadamard(wires=wire)

    for layer in range(N_LAYERS):

        for wire in range(N_QUBITS):
            qml.RY(
                weights[layer, wire],
                wires=wire
            )

        for wire in range(N_QUBITS - 1):
            qml.CZ(
                wires=[wire, wire + 1]
            )

        qml.CZ(
            wires=[N_QUBITS - 1, 0]
        )

    qml.QFT(wires=range(N_QUBITS))

    return [
        qml.expval(qml.PauliZ(wires=wire))
        for wire in range(N_QUBITS)
    ]


weight_shapes = {
    "weights": (N_LAYERS, N_QUBITS)
}


quantum_layer = qml.qnn.TorchLayer(
    qml.QNode(
        quantum_circuit,
        dev,
        interface="torch",
        diff_method="backprop"
    ),
    weight_shapes
)
