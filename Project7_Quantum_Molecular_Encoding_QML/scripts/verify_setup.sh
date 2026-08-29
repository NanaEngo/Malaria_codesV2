#!/bin/bash
# P7 — Setup Verification Script
# Checks if environment is correctly configured before running tests

set -e

PROJECT_DIR="/home/vital/Documents/GitHub/Malaria_codesV2/Project7_Quantum_Molecular_Encoding_QML"
cd "$PROJECT_DIR"

echo "======================================================================"
echo "P7 Setup Verification"
echo "======================================================================"
echo ""

# Check if conda environment exists
echo "1. Checking conda environment..."
if conda env list | grep -q "malaria_qml_hybrid"; then
    echo "   ✅ Environment 'malaria_qml_hybrid' exists"
else
    echo "   ❌ Environment 'malaria_qml_hybrid' not found"
    echo ""
    echo "   Create it with:"
    echo "   conda env create -f environment.yml"
    exit 1
fi

# Check if environment is activated
echo ""
echo "2. Checking if environment is activated..."
if [[ "$CONDA_DEFAULT_ENV" == "malaria_qml_hybrid" ]]; then
    echo "   ✅ Environment is activated"
else
    echo "   ❌ Environment not activated"
    echo ""
    echo "   Activate it with:"
    echo "   conda activate malaria_qml_hybrid"
    exit 1
fi

# Check Python packages
echo ""
echo "3. Checking Python packages..."

# PyTorch
if python -c "import torch" 2>/dev/null; then
    TORCH_VERSION=$(python -c "import torch; print(torch.__version__)")
    echo "   ✅ PyTorch $TORCH_VERSION"
else
    echo "   ❌ PyTorch not installed"
    exit 1
fi

# PennyLane
if python -c "import pennylane" 2>/dev/null; then
    PENNYLANE_VERSION=$(python -c "import pennylane; print(pennylane.__version__)")
    echo "   ✅ PennyLane $PENNYLANE_VERSION"
else
    echo "   ❌ PennyLane not installed"
    exit 1
fi

# Qiskit
if python -c "import qiskit" 2>/dev/null; then
    QISKIT_VERSION=$(python -c "import qiskit; print(qiskit.__version__)")
    echo "   ✅ Qiskit $QISKIT_VERSION"
else
    echo "   ❌ Qiskit not installed"
    exit 1
fi

# RDKit
if python -c "import rdkit" 2>/dev/null; then
    RDKIT_VERSION=$(python -c "import rdkit; print(rdkit.__version__)")
    echo "   ✅ RDKit $RDKIT_VERSION"
else
    echo "   ❌ RDKit not installed"
    exit 1
fi

# scikit-learn
if python -c "import sklearn" 2>/dev/null; then
    SKLEARN_VERSION=$(python -c "import sklearn; print(sklearn.__version__)")
    echo "   ✅ scikit-learn $SKLEARN_VERSION"
else
    echo "   ❌ scikit-learn not installed"
    exit 1
fi

# Check P7 scripts exist
echo ""
echo "4. Checking P7 scripts..."
SCRIPTS=(
    "scripts/p7_quantum_layers.py"
    "scripts/p7_training_utils.py"
    "scripts/p7_hybrid_vqc.py"
    "scripts/p7_data_preparation.py"
    "scripts/test_hybrid_implementation.py"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo "   ✅ $script"
    else
        echo "   ❌ $script not found"
        exit 1
    fi
done

# Check P7 modules can be imported
echo ""
echo "5. Checking P7 modules can be imported..."
cd scripts
if python -c "from p7_quantum_layers import HybridQNN" 2>/dev/null; then
    echo "   ✅ p7_quantum_layers imports successfully"
else
    echo "   ❌ Failed to import p7_quantum_layers"
    exit 1
fi

if python -c "from p7_training_utils import train_hybrid_model" 2>/dev/null; then
    echo "   ✅ p7_training_utils imports successfully"
else
    echo "   ❌ Failed to import p7_training_utils"
    exit 1
fi
cd ..

# Success!
echo ""
echo "======================================================================"
echo "✅ Setup verification complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Run tests: python scripts/test_hybrid_implementation.py"
echo "  2. Prepare data: python scripts/p7_data_preparation.py --p1-only"
echo "  3. Run Phase 1: python scripts/p7_hybrid_vqc.py --p1-set-a --qubits 4 --depth 2 --epochs 50"
echo ""
echo "======================================================================"
