import pennylane as qml

N_QUBITS = 4
N_LAYERS = 2

dev = qml.device(
    "default.qubit",
    wires=N_QUBITS
)


def quantum_circuit_no_encoding(inputs, weights):

    # Direct angle injection of the 16 classical features.
    # Four features are assigned to each qubit.
    for wire in range(N_QUBITS):

        start = wire * 4
        end = start + 4

        for feature_index in range(start, end):
            qml.RY(
                inputs[feature_index],
                wires=wire
            )

    # Trainable variational layers
    for layer in range(N_LAYERS):

        for wire in range(N_QUBITS):
            qml.RY(
                weights[layer, wire],
                wires=wire
            )

        # Ring entanglement
        for wire in range(N_QUBITS - 1):
            qml.CZ(
                wires=[wire, wire + 1]
            )

        qml.CZ(
            wires=[N_QUBITS - 1, 0]
        )

    # Quantum Fourier Transform
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


quantum_layer_no_encoding = qml.qnn.TorchLayer(
    qml.QNode(
        quantum_circuit_no_encoding,
        dev,
        interface="torch",
        diff_method="backprop"
    ),
    weight_shapes
)
