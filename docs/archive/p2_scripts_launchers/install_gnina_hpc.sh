#!/bin/bash
# ==============================================================================
# Historical GNINA installer targeting v1.3.3 (nanaengo@100.73.21.40)
# The currently retained binary was independently audited as v1.3.2; this script
# is not provenance for that binary and must not be used to infer execution results.
#
# Gnina is a deep learning docking tool that uses CNN scoring.
# It requires CUDA-capable GPU and NVIDIA drivers.
#
# Usage:
#   scp install_gnina_hpc.sh nanaengo@100.73.21.40:~/
#   ssh nanaengo@100.73.21.40 'bash ~/install_gnina_hpc.sh'
#
# After installation, Gnina will be at ~/gnina/gnina
# ==============================================================================
set -euo pipefail

INSTALL_DIR="$HOME/gnina"
BIN_URL="https://github.com/gnina/gnina/releases/download/v1.3.3/gnina"

echo "=== Gnina v1.3.3 Installation on HPC ==="
echo "Target: $INSTALL_DIR"
echo ""

# Step 1: Check prerequisites
echo "--- Step 1: Checking prerequisites ---"

# CUDA check
if command -v nvidia-smi &>/dev/null; then
    echo "CUDA GPU detected:"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || true
    nvidia-smi 2>&1 | grep "CUDA Version" || echo "  (could not detect CUDA version)"
else
    echo "WARNING: nvidia-smi not found. Gnina will fall back to CPU scoring."
    echo "  CNN rescoring requires CUDA for full speed."
fi

# Check disk space
df -h "$HOME" | tail -1

# Step 2: Create install directory
echo ""
echo "--- Step 2: Creating install directory ---"
mkdir -p "$INSTALL_DIR"

# Step 3: Download Gnina binary
echo ""
echo "--- Step 3: Downloading Gnina binary (v1.3.3) ---"
if [ -f "$INSTALL_DIR/gnina" ]; then
    echo "  Gnina already exists at $INSTALL_DIR/gnina"
    echo "  Version: $($INSTALL_DIR/gnina --version 2>&1 | head -1)"
else
    # Try wget, fallback to curl
    DOWNLOAD_CMD=""
    WGET_OPTS="${WGET_OPTS:-}"
    if command -v wget &>/dev/null; then
        DOWNLOAD_CMD="wget -q --show-progress $WGET_OPTS \"$BIN_URL\" -O \"$INSTALL_DIR/gnina\""
    elif command -v curl &>/dev/null; then
        DOWNLOAD_CMD="curl -L -o \"$INSTALL_DIR/gnina\" \"$BIN_URL\""
    else
        echo "ERROR: Neither wget nor curl available. Install one first."
        exit 1
    fi
    
    echo "  Downloading from $BIN_URL ..."
    eval "$DOWNLOAD_CMD"
    
    # Verify download succeeded (non-zero file)
    if [ ! -s "$INSTALL_DIR/gnina" ]; then
        echo "ERROR: Download failed (file is 0 bytes). Check URL: $BIN_URL"
        echo "  Try: WGET_OPTS='--no-check-certificate' bash install_gnina_hpc.sh"
        rm -f "$INSTALL_DIR/gnina"
        exit 1
    fi
    
    chmod +x "$INSTALL_DIR/gnina"
    echo "  Download complete ($(du -h "$INSTALL_DIR/gnina" | cut -f1))"
fi

# Step 4: Verify installation
echo ""
echo "--- Step 4: Verifying installation ---"
"$INSTALL_DIR/gnina" --help 2>&1 | head -10 || echo "(help output may vary)"

# Step 5: Detect CUDA capability
echo ""
echo "--- Step 5: Testing Gnina ---"
echo "  Testing with --cuda flag..."
"$INSTALL_DIR/gnina" --cuda --help 2>&1 | head -3 && echo "  ✅ CUDA detected" || echo "  ⚠️ CUDA not available, will use CPU"

# Step 6: Add to PATH
echo ""
echo "--- Step 6: Adding to PATH ---"
if ! grep -q "gnina" "$HOME/.bashrc" 2>/dev/null; then
    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$HOME/.bashrc"
    echo "  Added $INSTALL_DIR to PATH in ~/.bashrc"
else
    echo "  Gnina already in PATH"
fi

# Summary
echo ""
echo "=============================================="
echo "  Gnina Installation Complete"
echo "=============================================="
echo "  Binary: $INSTALL_DIR/gnina"
echo "  PATH:   export PATH=\$PATH:$INSTALL_DIR"
echo "  Version: v1.3.3"
echo "  Source:  $BIN_URL"
echo ""
echo "  To verify: $INSTALL_DIR/gnina --version"
echo "  To test:   echo 'COc1ccccc1' | $INSTALL_DIR/gnina -r protein.pdbqt --score_only"
echo "=============================================="
