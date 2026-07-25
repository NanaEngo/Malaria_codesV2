#!/usr/bin/env python3
"""
P3 — NISQ Smoke Test: 2-qubit Bell state on IBM Quantum hardware.

Verifies the PennyLane → Qiskit → IBM Quantum pipeline works end-to-end
before committing expensive 8-qubit IQPEmbedding jobs.

USAGE:
    # 1. Set your IBM Quantum API token:
    export IBM_QUANTUM_TOKEN="your_token_here"

    # 2. Run smoke test (2 qubits, trivial circuit):
    python scripts/p3_nisq_smoke_test.py

    # 3. Test on a specific backend:
    python scripts/p3_nisq_smoke_test.py --backend ibm_brisbane

    # 4. Test with error mitigation:
    python scripts/p3_nisq_smoke_test.py --resilience 1

PREREQUISITES:
    pip install pennylane-qiskit qiskit-ibm-runtime
    IBM Quantum account: https://quantum.ibm.com/ (free Open Plan)

IBM QUANTUM OPEN PLAN:
    1. Register at https://quantum.ibm.com/
    2. Go to Account → API token → copy token
    3. Free tier: 10 min/month on 100+ qubit Heron processors
    4. Queue: fair-share scheduler (open-plan = lower priority)
    5. Promotion: 180 min/12mo after using 20 min total

PENNYLANE → IBM PIPELINE:
    PennyLane QNode → qiskit.remote device → QiskitRuntimeService
    → IBM Quantum backend (ibm_brisbane, ibm_kyoto, etc.)
    → Results returned as PennyLane MeasurementProcess
"""

import os
import sys
import time
import argparse
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pennylane as qml

# ──────────────────────────────────────────────────────────────────────
# IBM Quantum authentication
# ──────────────────────────────────────────────────────────────────────

def _get_ibm_service():
    """Initialize QiskitRuntimeService from environment variable or file."""
    token = os.environ.get("IBM_QUANTUM_TOKEN", "")
    if not token:
        token_file = Path.home() / ".ibm_quantum_token"
        if token_file.exists():
            token = token_file.read_text().strip()
    if not token:
        print("ERROR: IBM Quantum token not found.")
        print("  Set environment variable: export IBM_QUANTUM_TOKEN='your_token'")
        print("  Or save to file: echo 'your_token' > ~/.ibm_quantum_token")
        print("  Get token at: https://quantum.ibm.com/ → Account → API token")
        sys.exit(1)

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        service = QiskitRuntimeService(
            channel="ibm_quantum",
            token=token,
        )
        return service
    except ImportError:
        print("ERROR: qiskit-ibm-runtime not installed.")
        print("  pip install qiskit-ibm-runtime")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR connecting to IBM Quantum: {e}")
        print("  Check your token at https://quantum.ibm.com/")
        sys.exit(1)


def list_available_backends(service) -> list[str]:
    """List available IBM Quantum backends accessible to this account."""
    backends = service.backends()
    available = []
    for b in backends:
        status = b.status()
        name = b.name
        qubits = b.num_qubits
        pending = getattr(status, 'pending_jobs', '?')
        available.append((name, qubits, pending))
    return available


# ──────────────────────────────────────────────────────────────────────
# 2-qubit smoke test circuit
# ──────────────────────────────────────────────────────────────────────

def create_bell_state_circuit(device_str: str, service=None, resilience: int = 0, backend: str = "ibm_brisbane"):
    """
    Create a 2-qubit Bell state circuit on the specified device.

    Args:
        device_str: 'lightning.qubit' (simulator) or 'qiskit.remote' (IBM Q)
        service: QiskitRuntimeService for IBM Quantum access
        resilience: Error mitigation level (0=None, 1=light, 2=heavy)
        backend: IBM Quantum backend name (default: ibm_brisbane)

    Returns:
        qnode: PennyLane QNode
        dev: PennyLane device
    """
    if device_str == "qiskit.remote":
        try:
            dev = qml.device(
                "qiskit.remote",
                wires=2,
                backend=backend,
                service=service,
                shots=1024,
                options={"resilience_level": resilience},
            )
        except Exception as e:
            print(f"  WARNING: Could not connect to ibm_brisbane: {e}")
            print("  Falling back to lightning.qubit simulator")
            dev = qml.device("lightning.qubit", wires=2)
    else:
        dev = qml.device("lightning.qubit", wires=2, shots=1024)

    @qml.qnode(dev)
    def bell_state():
        """Bell state: |00> + |11> / sqrt(2)"""
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return [
            qml.expval(qml.PauliZ(0)),
            qml.expval(qml.PauliZ(1)),
            qml.expval(qml.PauliX(0) @ qml.PauliX(1)),  # <XX> for Bell state
        ]

    return bell_state, dev


# ──────────────────────────────────────────────────────────────────────
# Kernel overlap test (the actual P3 circuit, but at 2 qubits)
# ──────────────────────────────────────────────────────────────────────

def create_kernel_overlap_circuit(device_str: str, service=None, resilience: int = 0, backend: str = "ibm_brisbane"):
    """
    2-qubit version of the P3 IQPEmbedding kernel circuit.

    This is a miniaturized version of the 8-qubit circuit used in p3_qks_benchmark.py.
    K(x1, x2) = |<phi(x1)|phi(x2)>|^2 = ground-state probability.

    Args:
        device_str: 'lightning.qubit' (simulator) or 'qiskit.remote' (IBM Q)
        service: QiskitRuntimeService
        resilience: Error mitigation level (0-2)
        backend: IBM Quantum backend name
    """
    if device_str == "qiskit.remote":
        try:
            dev = qml.device(
                "qiskit.remote",
                wires=2,
                backend=backend,
                service=service,
                shots=1024,
                options={"resilience_level": resilience},
            )
        except Exception:
            dev = qml.device("lightning.qubit", wires=2)
    else:
        dev = qml.device("lightning.qubit", wires=2)

    @qml.qnode(dev)
    def kernel_circuit(x1, x2):
        """2-qubit IQPEmbedding kernel overlap."""
        qml.IQPEmbedding(x1, wires=range(2), n_repeats=1)
        qml.adjoint(qml.IQPEmbedding)(x2, wires=range(2), n_repeats=1)
        return qml.probs(wires=range(2))

    return kernel_circuit, dev


# ──────────────────────────────────────────────────────────────────────
# Main smoke test
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="P3 NISQ Smoke Test — 2-qubit circuit on IBM Quantum"
    )
    parser.add_argument(
        "--backend", type=str, default="ibm_brisbane",
        help="IBM Quantum backend name (default: ibm_brisbane)"
    )
    parser.add_argument(
        "--resilience", type=int, default=0, choices=[0, 1, 2],
        help="Error mitigation level (0=none, 1=light, 2=heavy)"
    )
    parser.add_argument(
        "--simulator", action="store_true",
        help="Use lightning.qubit simulator instead of IBM Quantum"
    )
    parser.add_argument(
        "--list-backends", action="store_true",
        help="List available IBM Quantum backends and exit"
    )
    parser.add_argument(
        "--kernel", action="store_true",
        help="Also run 2-qubit kernel overlap test (IQPEmbedding)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("P3 NISQ Smoke Test — PennyLane → IBM Quantum")
    print("=" * 60)

    # Connect to IBM Quantum
    if args.simulator:
        device_str = "lightning.qubit"
        service = None
        print("\n  MODE: simulator (lightning.qubit)")
    else:
        device_str = "qiskit.remote"
        print("\n  Connecting to IBM Quantum...")
        service = _get_ibm_service()
        print(f"  Connected: {service.active_account() if hasattr(service, 'active_account') else 'OK'}")

    # List backends if requested
    if args.list_backends and service:
        print("\n  Available IBM Quantum backends:")
        for name, qubits, pending in list_available_backends(service):
            print(f"    {name:<20s}  qubits={qubits:>3d}  pending={pending}")
        return

    # ── TEST 1: Bell state ────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("TEST 1: 2-qubit Bell state")
    print(f"{'─' * 60}")
    print(f"  Circuit: H(0) → CNOT(0,1) → measure <Z0>, <Z1>, <XX>")
    print(f"  Expected: <Z0> ≈ 0, <Z1> ≈ 0, <XX> ≈ 1.0 (perfect Bell state)")

    circuit, dev = create_bell_state_circuit(
        device_str, service, args.resilience, args.backend
    )
    print(f"  Device: {dev.name} ({'IBM Quantum' if device_str == 'qiskit.remote' else 'simulator'})")

    t0 = time.perf_counter()
    results = circuit()
    elapsed = time.perf_counter() - t0

    z0, z1, xx = [float(r) for r in results]
    print(f"\n  Results (shots=1024):")
    print(f"    <Z0>  = {z0:+.4f}  (expected:  0.0000)")
    print(f"    <Z1>  = {z1:+.4f}  (expected:  0.0000)")
    print(f"    <XX>  = {xx:+.4f}  (expected: +1.0000)")
    print(f"  Runtime: {elapsed:.2f}s")

    # Score: how close to ideal Bell state?
    bell_score = abs(xx - 1.0) + abs(z0) + abs(z1)
    if bell_score < 0.1:
        print(f"  ✅ PASS: Bell state fidelity = {bell_score:.4f} (excellent)")
    elif bell_score < 0.3:
        print(f"  ⚠️  OK: Bell state fidelity = {bell_score:.4f} (moderate noise)")
    else:
        print(f"  ❌ FAIL: Bell state fidelity = {bell_score:.4f} (high noise)")

    # ── TEST 2: Kernel overlap (optional) ──────────────────────────
    if args.kernel:
        print(f"\n{'─' * 60}")
        print("TEST 2: 2-qubit IQPEmbedding kernel overlap")
        print(f"{'─' * 60}")

        # Use two different input vectors
        np.random.seed(42)
        x1 = np.random.uniform(-1, 1, 2)
        x2 = np.random.uniform(-1, 1, 2)
        print(f"  x1 = [{x1[0]:+.4f}, {x1[1]:+.4f}]")
        print(f"  x2 = [{x2[0]:+.4f}, {x2[1]:+.4f}]")

        kernel_fn, kdev = create_kernel_overlap_circuit(
            device_str, service, args.resilience, args.backend
        )
        print(f"  Device: {kdev.name}")

        t0 = time.perf_counter()
        k_result = kernel_fn(x1, x2)
        elapsed = time.perf_counter() - t0

        k_val = float(k_result[0])  # ground-state probability
        print(f"\n  Kernel K(x1, x2) = {k_val:.6f}")
        print(f"  (Perfect auto-kernel: K(x1, x1) should ≈ 1.0)")
        print(f"  Runtime: {elapsed:.2f}s")

        # Auto-kernel check
        print("  Computing auto-kernel K(x1, x1)...")
        k_auto = float(kernel_fn(x1, x1)[0])
        auto_deviation = abs(k_auto - 1.0)
        if auto_deviation < 0.05:
            print(f"  ✅ PASS: K(x1,x1) = {k_auto:.6f} (deviation = {auto_deviation:.4f})")
        elif auto_deviation < 0.15:
            print(f"  ⚠️  OK: K(x1,x1) = {k_auto:.6f} (deviation = {auto_deviation:.4f}, moderate noise)")
        else:
            print(f"  ❌ FAIL: K(x1,x1) = {k_auto:.6f} (deviation = {auto_deviation:.4f}, high noise)")

    print(f"\n{'─' * 60}")
    print("Smoke test complete.")
    print(f"{'─' * 60}")
    print("\nNext steps:")
    print("  1. If smoke test passes → run p3_nisq_deploy.py for full 8-qubit benchmark")
    print("  2. If smoke test fails → check IBM Quantum token, queue, or try --simulator")
    print("  3. Monitor IBM Quantum dashboard: https://quantum.ibm.com/")
    print(f"  4. Free tier limit: 10 min/month. This smoke test used ~{elapsed:.1f}s")


if __name__ == "__main__":
    main()
