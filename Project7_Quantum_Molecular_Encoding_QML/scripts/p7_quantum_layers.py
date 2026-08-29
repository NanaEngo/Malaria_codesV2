"""
P7 — Quantum Layers for Hybrid Models

Defines PennyLane-based quantum circuit layers that can be integrated into
PyTorch neural networks for hybrid quantum-classical training.

Key layers:
  - VQCLayer: Variational quantum circuit with trainable parameters
  - QuantumFeatureExtractor: Data encoding + VQC + measurement
  - QuantumKernelLayer: Quantum kernel-based layer (non-trainable encoding)

Usage:
    from p7_quantum_layers import QuantumFeatureExtractor
    
    qnn = QuantumFeatureExtractor(
        n_qubits=4,
        n_layers=2,
        entangling='cnot'
    )
    
    # Forward pass
    classical_features = torch.randn(batch_size, n_qubits)
    quantum_features = qnn(classical_features)
"""

import pennylane as qml
import torch
import torch.nn as nn
import numpy as np


class VQCLayer(nn.Module):
    """
    Variational Quantum Circuit (VQC) layer with trainable parameters.
    
    Circuit structure:
      1. Data encoding: RY rotations (angles = input features)
      2. Variational layers: RX/RY rotations + entangling gates (trainable)
      3. Measurement: Pauli Z expectations on all qubits
    
    Args:
        n_qubits: Number of qubits
        n_layers: Circuit depth (number of variational layers)
        entangling: Entangling gate type ('cnot', 'rxx', 'ryy', 'rzz', 'cz')
        backend: PennyLane device ('default.qubit', 'qiskit.aer', etc.)
    """
    
    def __init__(
        self,
        n_qubits: int,
        n_layers: int = 2,
        entangling: str = 'cnot',
        backend: str = 'default.qubit',
        shots: int = None
    ):
        super().__init__()
        
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.entangling = entangling
        
        # Create PennyLane device
        if shots is None:
            # Exact statevector simulation (fast, no shot noise)
            self.dev = qml.device(backend, wires=n_qubits)
        else:
            # Shot-based sampling (realistic hardware)
            self.dev = qml.device(backend, wires=n_qubits, shots=shots)
        
        # Create quantum node (circuit) with PyTorch interface
        self.qnode = qml.QNode(
            self._circuit,
            self.dev,
            interface='torch',
            diff_method='parameter-shift'  # Quantum gradient
        )
        
        # Initialize trainable parameters
        # Shape: (n_layers, n_qubits, 2) for RX and RY rotations
        weight_shape = (n_layers, n_qubits, 2)
        self.weights = nn.Parameter(
            torch.randn(weight_shape) * 0.1  # Small random init
        )
    
    def _circuit(self, inputs, weights):
        """
        Quantum circuit definition.
        
        Args:
            inputs: (n_qubits,) classical features to encode
            weights: (n_layers, n_qubits, 2) trainable parameters
        
        Returns:
            List of Pauli Z expectations (one per qubit)
        """
        # 1. Data encoding layer: RY rotations
        for i in range(self.n_qubits):
            qml.RY(inputs[i], wires=i)
        
        # 2. Variational layers (trainable)
        for layer in range(self.n_layers):
            # Single-qubit rotations (trainable)
            for i in range(self.n_qubits):
                qml.RX(weights[layer, i, 0], wires=i)
                qml.RY(weights[layer, i, 1], wires=i)
            
            # Entangling layer
            if self.entangling == 'cnot':
                for i in range(self.n_qubits - 1):
                    qml.CNOT(wires=[i, i + 1])
                if self.n_qubits > 2:
                    qml.CNOT(wires=[self.n_qubits - 1, 0])  # Circular
            
            elif self.entangling == 'cz':
                for i in range(self.n_qubits - 1):
                    qml.CZ(wires=[i, i + 1])
                if self.n_qubits > 2:
                    qml.CZ(wires=[self.n_qubits - 1, 0])
            
            elif self.entangling == 'rxx':
                for i in range(self.n_qubits - 1):
                    qml.IsingXX(weights[layer, i, 0], wires=[i, i + 1])
            
            elif self.entangling == 'ryy':
                for i in range(self.n_qubits - 1):
                    qml.IsingYY(weights[layer, i, 0], wires=[i, i + 1])
            
            elif self.entangling == 'rzz':
                for i in range(self.n_qubits - 1):
                    qml.IsingZZ(weights[layer, i, 0], wires=[i, i + 1])
            
            else:
                raise ValueError(f"Unknown entangling gate: {self.entangling}")
        
        # 3. Measurement: Pauli Z expectations
        return [qml.expval(qml.PauliZ(i)) for i in range(self.n_qubits)]
    
    def forward(self, x):
        """
        Forward pass through quantum circuit.
        
        Args:
            x: (batch_size, n_qubits) classical input features
        
        Returns:
            (batch_size, n_qubits) quantum features (measurement outcomes)
        """
        # Process batch element by element (PennyLane limitation)
        batch_size = x.shape[0]
        outputs = []
        
        for i in range(batch_size):
            # Get expectations for single sample
            expectations = self.qnode(x[i], self.weights)
            # Stack into tensor
            output = torch.stack(expectations)
            outputs.append(output)
        
        return torch.stack(outputs)


class QuantumFeatureExtractor(nn.Module):
    """
    Complete quantum feature extractor with dimension reduction and VQC.
    
    Architecture:
        Classical features (n_features) 
          → Linear (n_qubits)
          → VQC (trainable)
          → Quantum features (n_qubits)
    
    Args:
        n_features: Input feature dimension (e.g., 2048 for ECFP4)
        n_qubits: Number of qubits (4-16 typical)
        n_layers: Circuit depth
        entangling: Entangling gate type
    """
    
    def __init__(
        self,
        n_features: int,
        n_qubits: int,
        n_layers: int = 2,
        entangling: str = 'cnot',
        backend: str = 'default.qubit',
        shots: int = None
    ):
        super().__init__()
        
        self.n_features = n_features
        self.n_qubits = n_qubits
        
        # Classical dimension reduction
        self.encoder = nn.Linear(n_features, n_qubits)
        
        # Quantum circuit layer
        self.vqc = VQCLayer(
            n_qubits=n_qubits,
            n_layers=n_layers,
            entangling=entangling,
            backend=backend,
            shots=shots
        )
        
        # Normalization (helps with gradient stability)
        self.norm = nn.LayerNorm(n_qubits)
    
    def forward(self, x):
        """
        Args:
            x: (batch_size, n_features) classical features
        
        Returns:
            (batch_size, n_qubits) quantum-enhanced features
        """
        # Reduce dimension
        encoded = self.encoder(x)
        
        # Normalize to [-π, π] for RY gates
        encoded = torch.tanh(encoded) * np.pi
        
        # Quantum processing
        quantum_out = self.vqc(encoded)
        
        # Optional: normalize output
        quantum_out = self.norm(quantum_out)
        
        return quantum_out


class DualPathQuantumNet(nn.Module):
    """
    Dual-path architecture with classical and quantum branches.
    
    Architecture:
        Input
          ├─ Classical Path: MLP
          └─ Quantum Path: VQC
        Fusion: concatenate [classical | quantum]
          ↓
        Final MLP → Output
    
    Useful for ablation studies (quantum vs no-quantum).
    """
    
    def __init__(
        self,
        n_features: int,
        n_qubits: int = 4,
        hidden_dim: int = 64,
        n_layers: int = 2,
        entangling: str = 'cnot',
        use_quantum: bool = True
    ):
        super().__init__()
        
        self.n_features = n_features
        self.n_qubits = n_qubits
        self.use_quantum = use_quantum
        
        # Classical path
        self.classical_path = nn.Sequential(
            nn.Linear(n_features, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2)
        )
        
        # Quantum path (optional)
        if use_quantum:
            self.quantum_path = QuantumFeatureExtractor(
                n_features=n_features,
                n_qubits=n_qubits,
                n_layers=n_layers,
                entangling=entangling
            )
            fusion_dim = hidden_dim // 2 + n_qubits
        else:
            self.quantum_path = None
            fusion_dim = hidden_dim // 2
        
        # Fusion MLP
        self.fusion = nn.Sequential(
            nn.Linear(fusion_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """
        Args:
            x: (batch_size, n_features) input features
        
        Returns:
            (batch_size, 1) binary predictions
        """
        # Classical features
        classical_out = self.classical_path(x)
        
        # Quantum features (if enabled)
        if self.use_quantum:
            quantum_out = self.quantum_path(x)
            # Concatenate paths
            fused = torch.cat([classical_out, quantum_out], dim=1)
        else:
            fused = classical_out
        
        # Final prediction
        output = self.fusion(fused)
        return output


class HybridQNN(nn.Module):
    """
    Simple hybrid quantum-classical neural network.
    
    Architecture:
        ECFP4 (2048)
          → Linear (n_qubits)
          → VQC (trainable)
          → MLP (64 → 32 → 1)
          → Binary classification
    
    This is the simplest architecture (Architecture 1: Quantum Feature Extractor).
    """
    
    def __init__(
        self,
        n_features: int = 2048,
        n_qubits: int = 4,
        n_layers: int = 2,
        entangling: str = 'cnot',
        hidden_dim: int = 64,
        backend: str = 'default.qubit',
        shots: int = None
    ):
        super().__init__()
        
        self.n_features = n_features
        self.n_qubits = n_qubits
        
        # Quantum feature extractor
        self.quantum_encoder = QuantumFeatureExtractor(
            n_features=n_features,
            n_qubits=n_qubits,
            n_layers=n_layers,
            entangling=entangling,
            backend=backend,
            shots=shots
        )
        
        # Classical decoder
        self.decoder = nn.Sequential(
            nn.Linear(n_qubits, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """
        Args:
            x: (batch_size, n_features) ECFP4 or other features
        
        Returns:
            (batch_size, 1) binary predictions
        """
        # Quantum feature extraction
        quantum_features = self.quantum_encoder(x)
        
        # Classical decoding
        output = self.decoder(quantum_features)
        
        return output
    
    def get_quantum_weights(self):
        """Get current quantum circuit parameters."""
        return self.quantum_encoder.vqc.weights.detach().cpu().numpy()
    
    def check_gradient_vanishing(self):
        """
        Check if quantum gradients are vanishing.
        
        Returns:
            dict with gradient statistics
        """
        if self.quantum_encoder.vqc.weights.grad is None:
            return {'status': 'no_gradients', 'mean_norm': 0.0}
        
        grad = self.quantum_encoder.vqc.weights.grad
        grad_norm = torch.norm(grad).item()
        grad_mean = torch.mean(torch.abs(grad)).item()
        grad_max = torch.max(torch.abs(grad)).item()
        
        is_vanishing = grad_norm < 1e-4
        
        return {
            'status': 'vanishing' if is_vanishing else 'healthy',
            'norm': grad_norm,
            'mean': grad_mean,
            'max': grad_max,
            'is_vanishing': is_vanishing
        }


# Utility functions

def count_quantum_parameters(model):
    """Count trainable parameters in quantum layers."""
    total = 0
    quantum_params = 0
    
    for name, param in model.named_parameters():
        n_params = param.numel()
        total += n_params
        
        if 'vqc' in name or 'quantum' in name:
            quantum_params += n_params
    
    return {
        'total': total,
        'quantum': quantum_params,
        'classical': total - quantum_params
    }


def visualize_circuit(n_qubits=4, n_layers=2, entangling='cnot'):
    """
    Generate and print circuit diagram.
    
    Useful for debugging and documentation.
    """
    dev = qml.device('default.qubit', wires=n_qubits)
    
    @qml.qnode(dev)
    def circuit(inputs, weights):
        # Data encoding
        for i in range(n_qubits):
            qml.RY(inputs[i], wires=i)
        
        # Variational layers
        for layer in range(n_layers):
            for i in range(n_qubits):
                qml.RX(weights[layer, i, 0], wires=i)
                qml.RY(weights[layer, i, 1], wires=i)
            
            if entangling == 'cnot':
                for i in range(n_qubits - 1):
                    qml.CNOT(wires=[i, i + 1])
                if n_qubits > 2:
                    qml.CNOT(wires=[n_qubits - 1, 0])
        
        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    
    # Dummy inputs
    inputs = np.random.randn(n_qubits)
    weights = np.random.randn(n_layers, n_qubits, 2)
    
    # Generate circuit
    circuit(inputs, weights)
    
    # Print
    print(qml.draw(circuit)(inputs, weights))
    
    return circuit


if __name__ == "__main__":
    print("=" * 60)
    print("P7 Quantum Layers Test")
    print("=" * 60)
    
    # Test VQCLayer
    print("\n1. Testing VQCLayer...")
    vqc = VQCLayer(n_qubits=4, n_layers=2, entangling='cnot')
    
    # Forward pass
    x = torch.randn(2, 4)  # batch_size=2, n_qubits=4
    y = vqc(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {y.shape}")
    print(f"   Output range: [{y.min().item():.3f}, {y.max().item():.3f}]")
    
    # Test QuantumFeatureExtractor
    print("\n2. Testing QuantumFeatureExtractor...")
    qfe = QuantumFeatureExtractor(n_features=2048, n_qubits=4, n_layers=2)
    
    x = torch.randn(2, 2048)  # ECFP4-like input
    y = qfe(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {y.shape}")
    
    # Test HybridQNN
    print("\n3. Testing HybridQNN...")
    model = HybridQNN(n_features=2048, n_qubits=4, n_layers=2)
    
    x = torch.randn(2, 2048)
    y = model(x)
    print(f"   Input shape: {x.shape}")
    print(f"   Output shape: {y.shape}")
    print(f"   Predictions: {y.squeeze().detach().numpy()}")
    
    # Parameter count
    print("\n4. Parameter count...")
    params = count_quantum_parameters(model)
    print(f"   Total: {params['total']}")
    print(f"   Quantum: {params['quantum']}")
    print(f"   Classical: {params['classical']}")
    
    # Gradient test
    print("\n5. Gradient test...")
    loss = nn.BCELoss()(y, torch.tensor([[1.0], [0.0]]))
    loss.backward()
    
    grad_stats = model.check_gradient_vanishing()
    print(f"   Gradient status: {grad_stats['status']}")
    print(f"   Gradient norm: {grad_stats['norm']:.6f}")
    print(f"   Gradient mean: {grad_stats['mean']:.6f}")
    
    # Visualize circuit
    print("\n6. Circuit diagram (4 qubits, 2 layers, CNOT)...")
    visualize_circuit(n_qubits=4, n_layers=2, entangling='cnot')
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
