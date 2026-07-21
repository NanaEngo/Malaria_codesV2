#!/usr/bin/env python
"""
Simple syntax checker for Python scripts
"""
import py_compile
import sys

script = "step2_protein_prep.py"

try:
    py_compile.compile(script, doraise=True)
    print(f"✓ {script} - No syntax errors")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"✗ {script} - Syntax error:")
    print(e)
    sys.exit(1)
