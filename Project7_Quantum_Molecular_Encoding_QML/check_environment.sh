#!/bin/bash
# P7 Environment Check Script
# Run: bash check_environment.sh

echo "=========================================="
echo "P7 Environment Verification"
echo "=========================================="
echo ""

# Activate environment
echo "Activating malaria_qml_hybrid environment..."
source ~/miniconda3/etc/profile.d/conda.sh  # Or adjust for your conda path
conda activate malaria_qml_hybrid

echo ""
echo "Python version:"
python --version

echo ""
echo "=========================================="
echo "Checking Core Packages..."
echo "=========================================="

# PennyLane
echo ""
echo -n "PennyLane: "
python -c "import pennylane; print(pennylane.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING"

# PyTorch
echo -n "PyTorch: "
python -c "import torch; print(torch.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING"

# RDKit
echo -n "RDKit: "
python -c "import rdkit; print(rdkit.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING"

# scikit-learn
echo -n "scikit-learn: "
python -c "import sklearn; print(sklearn.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING"

# NumPy
echo -n "NumPy: "
python -c "import numpy; print(numpy.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING"

# Pandas
echo -n "Pandas: "
python -c "import pandas; print(pandas.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING"

echo ""
echo "=========================================="
echo "Checking Optional Packages..."
echo "=========================================="

# PyTorch Geometric
echo -n "PyTorch Geometric: "
python -c "import torch_geometric; print(torch_geometric.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING (optional for Q-GNN)"

# Qiskit
echo -n "Qiskit: "
python -c "import qiskit; print(qiskit.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING (optional for IBM hardware)"

# Matplotlib
echo -n "Matplotlib: "
python -c "import matplotlib; print(matplotlib.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING"

# Seaborn
echo -n "Seaborn: "
python -c "import seaborn; print(seaborn.__version__)" 2>/dev/null && echo "✓ OK" || echo "✗ MISSING"

echo ""
echo "=========================================="
echo "Environment Check Complete"
echo "=========================================="
echo ""

# Summary
python << 'EOF'
import sys

required = []
optional = []

# Check required
packages = [
    ('pennylane', 'PennyLane'),
    ('torch', 'PyTorch'),
    ('rdkit', 'RDKit'),
    ('sklearn', 'scikit-learn'),
    ('numpy', 'NumPy'),
    ('pandas', 'Pandas')
]

for module, name in packages:
    try:
        __import__(module)
        required.append(name)
    except ImportError:
        print(f"⚠️  MISSING REQUIRED: {name}")

# Check optional
opt_packages = [
    ('torch_geometric', 'PyTorch Geometric'),
    ('qiskit', 'Qiskit'),
    ('matplotlib', 'Matplotlib'),
    ('seaborn', 'Seaborn')
]

for module, name in opt_packages:
    try:
        __import__(module)
        optional.append(name)
    except ImportError:
        pass

print(f"\n✓ Required packages: {len(required)}/{len(packages)} installed")
print(f"✓ Optional packages: {len(optional)}/{len(opt_packages)} installed")

if len(required) == len(packages):
    print("\n✅ Environment ready for P7 Phase 1 (ECFP4 + QFE)")
    if 'PyTorch Geometric' in [o for m, o in opt_packages if m in [name for name, _ in optional]]:
        print("✅ Environment ready for Q-GNN (Phase 2)")
else:
    print("\n⚠️  Install missing required packages before proceeding")
    sys.exit(1)
EOF
