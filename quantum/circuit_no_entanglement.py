import pennylane as qml

N_QUBITS = 4
N_LAYERS = 2

dev = qml.device("default.qubit", wires=N_QUBITS)


def quantum_circuit_no_entanglement(inputs, weights):

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

        # Intentionally no CZ gates.
        # This ablation removes quantum entanglement
        # while keeping the trainable rotations unchanged.

    qml.QFT(
        wires=range(N_QUBITS)
    )

    return [
        qml.expval(
            qml.PauliZ(wires=wire)
        )
        for wire in range(N_QUBITS)
    ]


weight_shapes = {
    "weights": (N_LAYERS, N_QUBITS)
}


quantum_layer_no_entanglement = qml.qnn.TorchLayer(
    qml.QNode(
        quantum_circuit_no_entanglement,
        dev,
        interface="torch",
        diff_method="backprop"
    ),
    weight_shapes
)
