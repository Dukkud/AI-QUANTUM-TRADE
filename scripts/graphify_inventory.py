#!/usr/bin/env python3
"""Build a safe structural inventory for Q-GRAPH without exposing secrets."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from qgraph.adapter import build_safe_inventory
for item in sorted(build_safe_inventory(sys.argv[1] if len(sys.argv)>1 else '.')): print(item)
