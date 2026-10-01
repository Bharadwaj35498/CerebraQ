import numpy as np

def normalize_features(x):
    x = np.asarray(x, dtype=np.float32)

    norm = np.linalg.norm(x)

    if norm < 1e-12:
        return np.zeros_like(x)

    return x / norm


def amplitude_encode(x):
    """
    Normalize a feature vector so it can be interpreted
    as an amplitude-encoded quantum state.

    The vector length must be a power of two.
    """

    x = normalize_features(x)

    n = len(x)

    if n == 0 or (n & (n - 1)) != 0:
        raise ValueError(
            f"Feature vector length must be a power of 2. Got {n}."
        )

    return x


def prepare_quantum_features(feature_vector, n_qubits=4):
    """
    Prepare a normalized feature vector for quantum encoding.

    For n_qubits=4, the quantum state contains 2^4 = 16 amplitudes.
    """

    expected_size = 2 ** n_qubits

    feature_vector = np.asarray(feature_vector, dtype=np.float32)

    if len(feature_vector) != expected_size:
        raise ValueError(
            f"Expected {expected_size} features for {n_qubits} qubits, "
            f"but received {len(feature_vector)}."
        )

    return amplitude_encode(feature_vector)
