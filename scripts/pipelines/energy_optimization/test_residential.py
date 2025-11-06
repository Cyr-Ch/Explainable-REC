"""
Test script for residential energy optimization scenarios

This script tests the energy optimization pipeline with residential scenarios.
Run with: python scripts/pipelines/energy_optimization/test_residential.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.scenarios.residential_energy_community import main

if __name__ == '__main__':
    main()

