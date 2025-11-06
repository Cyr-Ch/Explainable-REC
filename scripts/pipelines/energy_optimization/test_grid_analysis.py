"""
Test script for grid impact analysis scenarios

This script tests the energy optimization pipeline with grid impact analysis scenarios.
Run with: python scripts/pipelines/energy_optimization/test_grid_analysis.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.scenarios.grid_impact_analysis import main

if __name__ == '__main__':
    main()

