# Datasets

This directory contains datasets and example data files for different energy scenarios.

## Structure

- `residential/` - Residential energy profiles and scenarios
- `commercial/` - Commercial building energy profiles and scenarios
- `grid_analysis/` - Grid impact analysis scenarios and data

## Usage

Datasets can be loaded in your scripts using:

```python
from pathlib import Path
import json
import numpy as np

# Load a dataset
dataset_path = Path("datasets/residential/pv_profiles.csv")
# ... load and use data
```

## Dataset Sources

- **Residential Profiles**: Generated for residential energy community scenarios
- **Commercial Profiles**: Generated for commercial building scenarios
- **Grid Scenarios**: Custom scenarios for grid impact analysis

## Adding New Datasets

1. Create a new subdirectory in `datasets/`
2. Add your data files (CSV, JSON, etc.)
3. Update this README with dataset description and source attribution
4. Add example loading code if applicable

