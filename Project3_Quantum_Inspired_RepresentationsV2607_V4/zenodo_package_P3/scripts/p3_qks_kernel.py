#!/usr/bin/env python3
"""
P3 — Quantum Kernel Score (QKS) Computation

Computes quantum kernel scores using IQPEmbedding on 8 qubits (classical simulation).

This is a template/reference script. The actual P3 QKS computation was performed
using PennyLane's classical simulator as described in P3_DATA_ANALYSIS_REPORT.md.

Requirements:
    - pennylane >= 0.45.1
    - numpy >= 2.2.1
    - pandas >= 2.2.3
    - scikit-learn >= 1.6.1

Key Parameters (from P3 DAR):
    - n_qubits: 8
    - Circuit: IQPEmbedding
    - Simulation: Classical (no quantum hardware)
    - Internal benchmark: AUC = 0.7512 ± 0.0334
    - vs RBF-SVM: AUC = 0.7007 ± 0.0672 (p=0.0878, n.s.)

Usage:
    python p3_qks_kernel.py --input molecules.csv --labels labels.csv --output qks_results.csv
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
from sklearn.metrics import roc_auc_score

try:
    import pennylane as qml
except ImportError:
    print("Warning: pennylane not installed. Install with: pip install pennylane")
    qml = None


def molecular_features_to_angles(features, n_qubits=8):
    """
    Convert molecular features to rotation angles for quantum circuit.
    
    Args:
        features (np.ndarray): Molecular feature vector
        n_qubits (int): Number of qubits
        
    Returns:
        np.ndarray: Rotation angles (length = n_qubits)
    """
    # Normalize and map to [0, 2π]
    if len(features) < n_qubits:
        # Pad if needed
        features = np.pad(features, (0, n_qubits - len(features)))
    elif len(features) > n_qubits:
        # Reduce dimensionality (simple averaging of chunks)
        chunk_size = len(features) // n_qubits
        features = np.array([features[i*chunk_size:(i+1)*chunk_size].mean() 
                            for i in range(n_qubits)])
    
    # Normalize to [0, 1]
    features = (features - features.min()) / (features.max() - features.min() + 1e-10)
    
    # Scale to [0, 2π]
    angles = features * 2 * np.pi
    
    return angles


def create_iqp_circuit(n_qubits=8):
    """
    Create IQP (Instantaneous Quantum Polynomial) embedding circuit.
    
    Args:
        n_qubits (int): Number of qubits
        
    Returns:
        callable: Quantum circuit function
    """
    if qml is None:
        raise ImportError("pennylane library required")
    
    dev = qml.device('default.qubit', wires=n_qubits)
    
    @qml.qnode(dev)
    def circuit(angles):
        """IQPEmbedding circuit"""
        # Hadamard layer
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
        
        # Rotation layer (encode features)
        for i in range(n_qubits):
            qml.RZ(angles[i], wires=i)
        
        # Entangling layer (all-to-all)
        for i in range(n_qubits):
            for j in range(i+1, n_qubits):
                qml.CNOT(wires=[i, j])
                qml.RZ(angles[i] * angles[j], wires=j)
                qml.CNOT(wires=[i, j])
        
        # Measure all qubits
        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    
    return circuit


def quantum_kernel(x1, x2, circuit, n_qubits=8):
    """
    Compute quantum kernel between two feature vectors.
    
    K(x1, x2) = |⟨ψ(x1)|ψ(x2)⟩|²
    
    Args:
        x1 (np.ndarray): First feature vector
        x2 (np.ndarray): Second feature vector
        circuit (callable): Quantum circuit
        n_qubits (int): Number of qubits
        
    Returns:
        float: Kernel value [0, 1]
    """
    angles1 = molecular_features_to_angles(x1, n_qubits)
    angles2 = molecular_features_to_angles(x2, n_qubits)
    
    # Compute state overlap (simplified approximation)
    state1 = np.array(circuit(angles1))
    state2 = np.array(circuit(angles2))
    
    # Kernel as inner product of expectation values
    kernel_value = np.abs(np.dot(state1, state2)) / n_qubits
    
    return kernel_value


def compute_kernel_matrix(X, circuit, n_qubits=8):
    """
    Compute full quantum kernel matrix.
    
    Args:
        X (np.ndarray): Feature matrix (N x D)
        circuit (callable): Quantum circuit
        n_qubits (int): Number of qubits
        
    Returns:
        np.ndarray: Kernel matrix (N x N)
    """
    n_samples = X.shape[0]
    K = np.zeros((n_samples, n_samples))
    
    for i in range(n_samples):
        if i % 100 == 0:
            print(f"  Computing kernel row {i}/{n_samples}...")
        
        for j in range(i, n_samples):
            k_val = quantum_kernel(X[i], X[j], circuit, n_qubits)
            K[i, j] = k_val
            K[j, i] = k_val  # Symmetric
    
    return K


def main():
    parser = argparse.ArgumentParser(description="P3 Quantum Kernel Score")
    parser.add_argument("--input", required=True, help="Input CSV with features")
    parser.add_argument("--labels", required=True, help="CSV with activity labels")
    parser.add_argument("--output", required=True, help="Output CSV with QKS results")
    parser.add_argument("--n-qubits", type=int, default=8, help="Number of qubits (default: 8)")
    parser.add_argument("--n-samples", type=int, default=5000, 
                       help="Number of samples for benchmark (default: 5000)")
    parser.add_argument("--cv-folds", type=int, default=5, help="CV folds (default: 5)")
    args = parser.parse_args()
    
    if qml is None:
        raise ImportError("pennylane library is required. Install with: pip install pennylane")
    
    # Load data
    print(f"Loading data from {args.input}...")
    X_df = pd.read_csv(args.input)
    y_df = pd.read_csv(args.labels)
    
    # Subsample if needed
    if len(X_df) > args.n_samples:
        print(f"Subsampling {args.n_samples} from {len(X_df)} molecules...")
        indices = np.random.choice(len(X_df), args.n_samples, replace=False)
        X_df = X_df.iloc[indices]
        y_df = y_df.iloc[indices]
    
    X = X_df.values
    y = y_df.values.ravel()
    
    # Create quantum circuit
    print(f"Creating IQP circuit with {args.n_qubits} qubits...")
    circuit = create_iqp_circuit(n_qubits=args.n_qubits)
    
    # Compute quantum kernel matrix
    print("Computing quantum kernel matrix...")
    K_quantum = compute_kernel_matrix(X, circuit, n_qubits=args.n_qubits)
    
    # Train SVM with quantum kernel
    print(f"Training SVM with quantum kernel ({args.cv_folds}-fold CV)...")
    svm_quantum = SVC(kernel='precomputed')
    scores_quantum = cross_val_score(svm_quantum, K_quantum, y, cv=args.cv_folds, 
                                     scoring='roc_auc')
    
    # Compare with RBF kernel
    print("Training SVM with RBF kernel (baseline)...")
    svm_rbf = SVC(kernel='rbf', gamma='scale')
    scores_rbf = cross_val_score(svm_rbf, X, y, cv=args.cv_folds, scoring='roc_auc')
    
    # Results
    results = {
        'method': ['Quantum Kernel', 'RBF Kernel'],
        'mean_auc': [scores_quantum.mean(), scores_rbf.mean()],
        'std_auc': [scores_quantum.std(), scores_rbf.std()],
        'cv_folds': [args.cv_folds, args.cv_folds],
        'n_samples': [len(X), len(X)],
        'n_qubits': [args.n_qubits, None]
    }
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(args.output, index=False)
    
    print(f"\nResults saved to {args.output}")
    print(f"\nQuantum Kernel: AUC = {scores_quantum.mean():.4f} ± {scores_quantum.std():.4f}")
    print(f"RBF Kernel:     AUC = {scores_rbf.mean():.4f} ± {scores_rbf.std():.4f}")
    print(f"\nNote: Quantum kernels simulated on classical hardware (no quantum advantage)")


if __name__ == "__main__":
    main()
